#!/usr/bin/env python3
"""
Fetch CoSAI meeting minutes from Google Drive and GitHub, save as markdown.

Drive sources: Reads Gemini-generated meeting notes from shared Drive
folders, exports them as markdown. Drive access goes through the Google
Workspace CLI (`gws`, https://github.com/googleworkspace/cli). See
scripts/README.md for one-time gws + gcloud + OAuth setup. Currently covers WS4, the
ADLC SIG (under WS4), WS3, the Code-Development SIG (under WS3), the
Risk Management SIG (under WS3), and the Agent Credentials group.

GitHub sources (TSC): Reads markdown meeting minutes committed to a public
GitHub repo directory. Uses the unauthenticated GitHub Contents API; honors
GITHUB_TOKEN env var if set to raise the rate limit.

Output goes under meeting_minutes/<subdir>/ in the WS4 repo.

Usage:
    # Fetch all meeting minutes
    python scripts/fetch_meeting_minutes.py

    # Fetch only new minutes (skip existing files)
    python scripts/fetch_meeting_minutes.py --skip-existing
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Meeting sources. Each source has:
#   type:    "drive" or "github"
#   subdir:  output subdirectory under meeting_minutes/
#   For drive sources: folder_id (parent containing per-meeting subfolders)
#   For github sources: repo (owner/name), path (directory in the repo)
SOURCES = [
    {
        "name": "WS4",
        "type": "drive",
        "folder_id": "1TJl4yqWIdfPc8fKWiTO0CsmsmuecGxWa",
        "subdir": "ws4",
        # Fallback when a per-meeting subfolder hasn't been filed yet:
        # match Gemini notes shared directly with the user.
        "shared_name_contains": "CoSAI WS4 recurring meeting",
        "shared_title_pattern": (
            r"^CoSAI WS4 recurring meeting - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2}) .* Notes by Gemini$"
        ),
        "shared_folder_name_template": "WS4 {y}{m}{d}",
    },
    {
        "name": "ADLC",
        "type": "drive",
        "folder_id": "1EkoOpMCtYahLu-sEhYrgNDmvPyTtgpit",
        "subdir": "adlc",
        "shared_name_contains": "WS4 SIG Security of Agent Development Lifecycle",
        "shared_title_pattern": (
            r"^WS4 SIG Security of Agent Development Lifecycle - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2}) .* Notes by Gemini$"
        ),
        "shared_folder_name_template": "{y}-{m}-{d}",
    },
    {
        "name": "WS3",
        "type": "drive",
        "folder_id": "1NFk_-2Plyi3qYr2qtrvt42AQhzJZB0Wf",
        "subdir": "ws3",
        # No shared-with-me fallback: the docs in WS3 per-meeting folders
        # aren't Gemini-tagged with a stable "Notes by Gemini" title, so
        # we can't reliably pattern-match unfiled shares. The folder-walk
        # pass picks them up via the find_notes_doc fallback.
    },
    {
        "name": "Code-SIG",
        "type": "drive",
        "folder_id": "1yKk-Mbbpowsk3gfRwGIT7UpMOJ-fDzdo",
        "subdir": "code-sig",
        "shared_name_contains": "CoSAI WS3 SIG: Security of AI-Assisted Code Development",
        "shared_title_pattern": (
            r"^CoSAI WS3 SIG: Security of AI-Assisted Code Development - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2}) .* Notes by Gemini$"
        ),
        "shared_folder_name_template": "{y}-{m}-{d}",
    },
    {
        "name": "RM-SIG",
        "type": "drive",
        "folder_id": "1tboOFAyYHnJRlXqMO3Kdh6KrcAVVIpiB",
        "subdir": "rm-sig",
        "shared_name_contains": "CoSAI WS3 CoSAI-RM SIG weekly meeting",
        "shared_title_pattern": (
            r"^CoSAI WS3 CoSAI-RM SIG weekly meeting - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2}) .* Notes by Gemini$"
        ),
        "shared_folder_name_template": "WS3 CoSAI-RM SIG {y}{m}{d}",
    },
    {
        "name": "Agent-Credentials",
        "type": "drive",
        "folder_id": "1Telz7CDwCgPNUyHlMwu9cBGl-keqP9z3",
        "subdir": "agent-credentials",
        "shared_name_contains": "CoSAI WS4: Agent Credentials",
        "shared_title_pattern": (
            r"^CoSAI WS4: Agent Credentials - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2}) .* Notes by Gemini$"
        ),
        "shared_folder_name_template": "{y}-{m}-{d}",
    },
    {
        "name": "TSC",
        "type": "github",
        "repo": "cosai-oasis/cosai-tsc",
        "path": "tsc-meeting-minutes",
        "subdir": "tsc",
    },
]

# Output directory. Derived from this script's location (scripts/ lives at the
# repo root) so the script writes into whatever clone it is run from, rather
# than a hard-coded path.
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "meeting_minutes"


class GwsError(Exception):
    """A gws invocation failed; message carries the API error if parseable."""


def run_gws(args, cwd=None):
    """Run a gws command and return parsed JSON from stdout.

    Raises GwsError on nonzero exit, with the Drive API error message when
    gws printed one (gws emits the error JSON on stdout).
    """
    result = subprocess.run(
        ["gws", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        message = result.stderr.strip().splitlines()[-1:] or ["unknown error"]
        try:
            err = json.loads(result.stdout).get("error", {})
            message = [f"{err.get('code', '?')} {err.get('message', 'unknown error')}"]
        except (json.JSONDecodeError, AttributeError):
            pass
        raise GwsError(message[0])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise GwsError(f"unparseable gws output: {e}")


def drive_list(params):
    """Call `gws drive files list`, following pagination. Returns files[]."""
    files = []
    params = dict(params)
    while True:
        response = run_gws(["drive", "files", "list", "--params", json.dumps(params)])
        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            return files
        params["pageToken"] = page_token


def check_gws():
    """Verify the gws CLI is available before doing any Drive work."""
    if shutil.which("gws"):
        return
    print("Error: the Google Workspace CLI (`gws`) is not on PATH.", file=sys.stderr)
    print("Install it from https://github.com/googleworkspace/cli/releases", file=sys.stderr)
    print("then follow the setup in scripts/README.md.", file=sys.stderr)
    sys.exit(1)


def list_meeting_folders(parent_folder_id):
    """List all meeting subfolders in a parent Drive folder."""
    folders = drive_list({
        "q": (
            f"'{parent_folder_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false"
        ),
        "fields": "nextPageToken, files(id, name)",
        "pageSize": 100,
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    })
    return sorted(folders, key=lambda f: f["name"])


def find_notes_doc(folder_id):
    """Find the Gemini notes document in a meeting folder.

    Returns a dict with id, name, and mimeType. If the match is a shortcut
    pointing to a Google Doc, the returned id is the shortcut's target id so
    the caller can export it directly.
    """
    files = drive_list({
        "q": (
            f"'{folder_id}' in parents and trashed=false and "
            "(mimeType='application/vnd.google-apps.document' "
            "or mimeType='application/vnd.google-apps.shortcut')"
        ),
        "fields": "nextPageToken, files(id, name, mimeType, shortcutDetails)",
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    })

    def resolve(f):
        if f["mimeType"] == "application/vnd.google-apps.shortcut":
            sd = f.get("shortcutDetails") or {}
            if sd.get("targetMimeType") != "application/vnd.google-apps.document":
                return None
            return {"id": sd["targetId"], "name": f["name"], "mimeType": sd["targetMimeType"]}
        return f

    # Prefer "Notes by Gemini" matches, fall back to any resolvable doc
    for f in files:
        if "Notes by Gemini" in f["name"]:
            resolved = resolve(f)
            if resolved:
                return resolved
    for f in files:
        resolved = resolve(f)
        if resolved:
            return resolved
    return None


def export_doc_as_markdown(file_id, workdir):
    """Export a Google Doc as markdown text.

    gws only writes exports inside its working directory, so run it with
    cwd=workdir and a relative temp filename, then read and remove the file.
    """
    tmp_name = f".gws-export-{os.getpid()}.tmp"
    tmp_path = workdir / tmp_name
    try:
        run_gws(
            [
                "drive", "files", "export",
                "--params", json.dumps({"fileId": file_id, "mimeType": "text/markdown"}),
                "-o", tmp_name,
            ],
            cwd=workdir,
        )
        return tmp_path.read_text(encoding="utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)


def folder_name_to_filename(folder_name):
    """Convert folder name like 'WS4 20260402' to 'WS4-20260402.md'."""
    # Normalize whitespace and replace spaces with hyphens
    name = re.sub(r"\s+", "-", folder_name.strip())
    return f"{name}.md"


def fetch_drive_source(source, output_dir, skip_existing):
    """Fetch all Gemini meeting notes from a Drive source.

    Returns (fetched, skipped, no_notes, errors).
    """
    fetched = skipped = no_notes = errors = 0

    print(f"\n[{source['name']}] Listing meeting folders...")
    folders = list_meeting_folders(source["folder_id"])
    print(f"[{source['name']}] Found {len(folders)} meeting folders")

    for folder in folders:
        filename = folder_name_to_filename(folder["name"])
        output_path = output_dir / filename

        if skip_existing and output_path.exists():
            skipped += 1
            continue

        notes_doc = find_notes_doc(folder["id"])
        if not notes_doc:
            print(f"  {folder['name']}: no notes document found")
            no_notes += 1
            continue

        print(f"  {folder['name']}: fetching '{notes_doc['name']}'...")
        try:
            content = export_doc_as_markdown(notes_doc["id"], output_dir)
        except GwsError as e:
            # Listing surfaces shortcuts whose target doc may be in a
            # restricted Drive the user can't export from. Don't let one
            # bad doc kill the whole run.
            print(f"  {folder['name']}: export failed ({e}); skipping", file=sys.stderr)
            errors += 1
            continue

        header = f"# {folder['name']}\n\n"
        header += f"**Source:** {notes_doc['name']}\n\n---\n\n"

        with open(output_path, "w") as f:
            f.write(header + content)

        fetched += 1

    return fetched, skipped, no_notes, errors


def fetch_drive_shared_fallback(source, output_dir, skip_existing):
    """Catch Gemini notes that are shared with the user but not yet filed
    into a per-meeting subfolder. Matches by title pattern; writes to the
    same canonical filename the folder pass would produce.

    Returns (fetched, skipped, errors).
    """
    name_contains = source.get("shared_name_contains")
    pattern = source.get("shared_title_pattern")
    template = source.get("shared_folder_name_template")
    if not (name_contains and pattern and template):
        return 0, 0, 0

    fetched = skipped = errors = 0
    pat = re.compile(pattern)

    safe_contains = name_contains.replace("'", "\\'")
    q = (
        "sharedWithMe = true and trashed = false and "
        "mimeType = 'application/vnd.google-apps.document' and "
        f"name contains '{safe_contains}'"
    )

    print(f"\n[{source['name']}] Scanning shared-with-me for unfiled Gemini notes...")
    candidates = drive_list({
        "q": q,
        "fields": "nextPageToken, files(id, name, mimeType)",
        "pageSize": 100,
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    })

    for f in candidates:
        m = pat.match(f["name"])
        if not m:
            continue
        synthetic = template.format(**m.groupdict())
        output_path = output_dir / folder_name_to_filename(synthetic)

        if skip_existing and output_path.exists():
            skipped += 1
            continue

        print(f"  [shared] {synthetic}: fetching '{f['name']}'...")
        try:
            content = export_doc_as_markdown(f["id"], output_dir)
        except GwsError as e:
            print(f"  [shared] {synthetic}: export failed ({e}); skipping", file=sys.stderr)
            errors += 1
            continue
        header = (
            f"# {synthetic}\n\n"
            f"**Source:** {f['name']} (via shared-with-me fallback)\n\n---\n\n"
        )
        with open(output_path, "w") as out:
            out.write(header + content)
        fetched += 1

    return fetched, skipped, errors


def _github_request(url):
    """Open a GitHub API/raw URL with optional bearer auth from GITHUB_TOKEN."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "fetch_meeting_minutes",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req, timeout=30)


def fetch_github_source(source, output_dir, skip_existing):
    """Fetch markdown meeting minutes from a GitHub repo directory.

    Lists files via the GitHub Contents API and downloads .md files via
    each file's download_url. Returns (fetched, skipped, errors).
    """
    fetched = skipped = errors = 0
    api_url = f"https://api.github.com/repos/{source['repo']}/contents/{source['path']}"

    print(f"\n[{source['name']}] Listing GitHub directory {source['repo']}/{source['path']}...")
    try:
        with _github_request(api_url) as resp:
            listing = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"[{source['name']}] GitHub API error: {e.code} {e.reason}", file=sys.stderr)
        return fetched, skipped, errors + 1

    md_files = [f for f in listing if f.get("type") == "file" and f["name"].endswith(".md")]
    print(f"[{source['name']}] Found {len(md_files)} markdown files")

    for f in md_files:
        output_path = output_dir / f["name"]
        if skip_existing and output_path.exists():
            skipped += 1
            continue

        print(f"  {f['name']}: fetching...")
        # One bad download (transient error, moved file) shouldn't abort the
        # whole source; log it and move on, mirroring the Drive path.
        try:
            with _github_request(f["download_url"]) as resp:
                content = resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError) as e:
            print(f"  {f['name']}: download failed ({e}); skipping", file=sys.stderr)
            errors += 1
            continue
        output_path.write_text(content, encoding="utf-8")
        fetched += 1

    return fetched, skipped, errors


def main():
    parser = argparse.ArgumentParser(description="Fetch CoSAI meeting minutes from Drive and GitHub")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip meetings that already have a local file")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    if any(s["type"] == "drive" for s in SOURCES):
        check_gws()

    total_fetched = 0
    total_skipped = 0
    total_no_notes = 0
    total_errors = 0

    for source in SOURCES:
        output_dir = OUTPUT_DIR / source["subdir"] if source["subdir"] else OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        if source["type"] == "drive":
            fetched, skipped, no_notes, errors = fetch_drive_source(
                source, output_dir, args.skip_existing
            )
            total_no_notes += no_notes
            total_errors += errors
            f2, s2, e2 = fetch_drive_shared_fallback(
                source, output_dir, args.skip_existing
            )
            fetched += f2
            skipped += s2
            total_errors += e2
        elif source["type"] == "github":
            fetched, skipped, errors = fetch_github_source(
                source, output_dir, args.skip_existing
            )
            total_errors += errors
        else:
            print(f"[{source['name']}] Unknown source type: {source['type']}", file=sys.stderr)
            continue

        total_fetched += fetched
        total_skipped += skipped

    print(
        f"\nDone: {total_fetched} fetched, {total_skipped} skipped, "
        f"{total_no_notes} without notes, {total_errors} export errors"
    )


if __name__ == "__main__":
    main()
