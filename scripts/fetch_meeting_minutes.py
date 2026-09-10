#!/usr/bin/env python3
"""
Fetch CoSAI meeting minutes from Google Drive and GitHub, save as markdown.

Drive sources: Reads Gemini-generated meeting notes from shared Drive
folders, exports them as markdown. Alongside the notes it also pulls the two
other per-meeting artifacts Google Meet produces -- the in-call **chat log**
and the **attendance** sheet -- which carry material the Gemini notes drop
(links, side-questions, corrections, who was actually in the room and when).
Meet does not produce a transcript document; see scripts/README.md for how to
transcribe the recording locally when you need one.

Drive access goes through the Google
Workspace CLI (`gws`, https://github.com/googleworkspace/cli). See
scripts/README.md for one-time gws + gcloud + OAuth setup. Currently covers
WS1, WS2, WS3, WS4, the ADLC SIG and the Multimodal Agentic Security group
(both under WS4), the Code-Development SIG (under WS3), the Risk Management
SIG (under WS3), and the Agent Credentials group.

GitHub sources: Reads markdown meeting minutes committed to public GitHub
repo directories. Covers TSC minutes and PGB minutes. Uses the
unauthenticated GitHub Contents API; honors GITHUB_TOKEN env var if set to
raise the rate limit.

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
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
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
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
        ),
        "shared_folder_name_template": "{y}-{m}-{d}",
    },
    {
        "name": "Multimodal",
        "type": "drive",
        "folder_id": "1JI89V3NrSQnEzcE6nlNUed2Huv114FD4",
        "subdir": "multimodal",
        # WS4 sub-group (Shriti Priya). Mixed layout: June/July meetings are
        # filed in per-date subfolders; from August the Gemini notes sit loose
        # in the parent, so the shared-with-me fallback carries those.
        "shared_name_contains": "WS4 Multimodal Agentic Security Weekly Meeting",
        "shared_title_pattern": (
            r"^WS4 Multimodal Agentic Security Weekly Meeting - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
        ),
        "shared_folder_name_template": "{y}-{m}-{d}",
    },
    {
        "name": "WS1",
        "type": "drive",
        "folder_id": "1L7A46unF12D3Tk68_QVP53M9cGjJUMA3",
        "subdir": "ws1",
        # Prefix match — works whether or not "Notes by Gemini" is appended.
        "shared_name_contains": "CoSAI WS1 Weekly Meeting",
        "shared_title_pattern": (
            r"^CoSAI WS1 Weekly Meeting - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
        ),
        "shared_folder_name_template": "WS1-{y}{m}{d}",
    },
    {
        "name": "WS2",
        "type": "drive",
        "folder_id": "1zmeLjxAp8UJdu99LM3qAhHf-CH9JGR32",
        "subdir": "ws2",
        # Prefix match — WS2 titles end after the date, with no
        # "Notes by Gemini" suffix, so the pattern must not require one.
        "shared_name_contains": "CoSAI WS2 Defenders meeting",
        "shared_title_pattern": (
            r"^CoSAI WS2 Defenders meeting - "
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
        ),
        "shared_folder_name_template": "WS2-{y}{m}{d}",
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
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
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
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
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
            r"(?P<y>\d{4})/(?P<m>\d{2})/(?P<d>\d{2})"
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
    {
        "name": "PGB",
        "type": "github",
        "repo": "cosai-oasis/oasis-open-project",
        "path": "pgb-meeting-minutes",
        "subdir": "pgb",
    },
]

# Per-meeting artifacts that sit alongside the Gemini notes. Google Meet emits
# these with the same title stem as the notes, differing only in the trailing
# kind ("... - Chat", "... - Attendance"), so they are matched on that suffix
# plus mimeType. Each is written next to the notes file using the same stem.
#
# Two different retrieval paths are needed: Google-native files (Sheets) must be
# *exported* to a concrete format, while binary/plain files (the chat log) must
# be *downloaded* with alt=media. `gws drive files download` is not the right
# verb for either -- it returns a long-running-operation envelope carrying a
# downloadUri and writes nothing.
#
# Only the WS4 recurring meeting currently has chat capture enabled; sources
# without these artifacts yield nothing here, which is not an error.
COMPANION_ARTIFACTS = [
    {
        "kind": "chat",
        "title_suffix": "Chat",
        "extension": "-chat.txt",
        "mime_type": "text/plain",
        "method": "download",
    },
    {
        "kind": "attendance",
        "title_suffix": "Attendance",
        "extension": "-attendance.csv",
        "mime_type": "application/vnd.google-apps.spreadsheet",
        "export_mime": "text/csv",
        "method": "export",
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


def list_folder_files(folder_id):
    """List every non-folder file in a meeting folder, in one call.

    One listing serves the notes document and every companion artifact, so a
    folder costs a single Drive request regardless of how much we pull from it.
    """
    return drive_list({
        "q": (
            f"'{folder_id}' in parents and trashed=false and "
            "mimeType != 'application/vnd.google-apps.folder'"
        ),
        "fields": "nextPageToken, files(id, name, mimeType, shortcutDetails)",
        "pageSize": 100,
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    })


def _resolve_shortcut(f, wanted_mime):
    """Resolve a listing entry to a concrete file of wanted_mime, or None.

    Meet files each appear twice in a folder -- once directly and once as a
    shortcut -- so shortcuts are followed to their target rather than skipped,
    and non-matching mimeTypes are rejected either way.
    """
    if f["mimeType"] == "application/vnd.google-apps.shortcut":
        sd = f.get("shortcutDetails") or {}
        if sd.get("targetMimeType") != wanted_mime:
            return None
        return {"id": sd["targetId"], "name": f["name"], "mimeType": sd["targetMimeType"]}
    if f["mimeType"] != wanted_mime:
        return None
    return f


DOC_MIME = "application/vnd.google-apps.document"


def pick_notes_doc(files):
    """Pick the Gemini notes document from a folder listing.

    Returns a dict with id, name, and mimeType. If the match is a shortcut
    pointing to a Google Doc, the returned id is the shortcut's target id so
    the caller can export it directly.
    """
    # Prefer "Notes by Gemini" matches, fall back to any resolvable doc
    for f in files:
        if "Notes by Gemini" in f["name"]:
            resolved = _resolve_shortcut(f, DOC_MIME)
            if resolved:
                return resolved
    for f in files:
        resolved = _resolve_shortcut(f, DOC_MIME)
        if resolved:
            return resolved
    return None


def pick_companion(files, spec):
    """Pick one companion artifact (chat, attendance) from a folder listing."""
    suffix = f" - {spec['title_suffix']}"
    for f in files:
        if not f["name"].endswith(suffix):
            continue
        resolved = _resolve_shortcut(f, spec["mime_type"])
        if resolved:
            return resolved
    return None


def _gws_to_bytes(argv, workdir, tag):
    """Run a gws command that writes a file, and return the bytes it wrote.

    gws refuses any -o path that resolves outside its working directory, so
    every retrieval runs with cwd=workdir and a relative temp filename, then
    reads and removes the file.
    """
    tmp_name = f".gws-{tag}-{os.getpid()}.tmp"
    tmp_path = workdir / tmp_name
    try:
        run_gws([*argv, "-o", tmp_name], cwd=workdir)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def export_doc(file_id, workdir, mime_type):
    """Export a Google-native file (Doc, Sheet) to a concrete format."""
    data = _gws_to_bytes(
        ["drive", "files", "export",
         "--params", json.dumps({"fileId": file_id, "mimeType": mime_type})],
        workdir,
        "export",
    )
    return data.decode("utf-8")


def export_doc_as_markdown(file_id, workdir):
    """Export a Google Doc as markdown text."""
    return export_doc(file_id, workdir, "text/markdown")


def download_file(file_id, workdir):
    """Download a non-Google-native file (the chat log) via alt=media."""
    data = _gws_to_bytes(
        ["drive", "files", "get",
         "--params", json.dumps({"fileId": file_id, "alt": "media"})],
        workdir,
        "download",
    )
    return data.decode("utf-8")


def fetch_companion(spec, entry, workdir):
    """Retrieve one companion artifact's text, by whichever method it needs."""
    if spec["method"] == "export":
        return export_doc(entry["id"], workdir, spec["export_mime"])
    return download_file(entry["id"], workdir)


def folder_name_to_stem(folder_name):
    """Convert folder name like 'WS4 20260402' to the stem 'WS4-20260402'."""
    # Normalize whitespace and replace spaces with hyphens
    return re.sub(r"\s+", "-", folder_name.strip())


def folder_name_to_filename(folder_name):
    """Convert folder name like 'WS4 20260402' to 'WS4-20260402.md'."""
    return f"{folder_name_to_stem(folder_name)}.md"


def fetch_companions_for(files, stem, output_dir, skip_existing, label):
    """Write every companion artifact found in `files` next to the notes file.

    Returns (fetched, skipped, errors). Missing companions are not an error --
    older meetings predate chat capture, and not every call records attendance.
    """
    fetched = skipped = errors = 0
    for spec in COMPANION_ARTIFACTS:
        output_path = output_dir / f"{stem}{spec['extension']}"
        if skip_existing and output_path.exists():
            skipped += 1
            continue
        entry = pick_companion(files, spec)
        if not entry:
            continue
        print(f"  {label}: fetching {spec['kind']}...")
        try:
            content = fetch_companion(spec, entry, output_dir)
        except GwsError as e:
            print(f"  {label}: {spec['kind']} failed ({e}); skipping", file=sys.stderr)
            errors += 1
            continue
        output_path.write_text(content, encoding="utf-8")
        fetched += 1
    return fetched, skipped, errors


def fetch_drive_source(source, output_dir, skip_existing):
    """Fetch all Gemini meeting notes from a Drive source.

    Returns (fetched, skipped, no_notes, errors).
    """
    fetched = skipped = no_notes = errors = 0

    print(f"\n[{source['name']}] Listing meeting folders...")
    folders = list_meeting_folders(source["folder_id"])
    print(f"[{source['name']}] Found {len(folders)} meeting folders")

    for folder in folders:
        stem = folder_name_to_stem(folder["name"])
        output_path = output_dir / f"{stem}.md"

        wanted = [output_path] + [
            output_dir / f"{stem}{c['extension']}" for c in COMPANION_ARTIFACTS
        ]
        # Fast path: once a meeting's notes and companions are all on disk there
        # is nothing to list it for, so --skip-existing stays cheap after the
        # first backfill.
        if skip_existing and all(path.exists() for path in wanted):
            skipped += len(wanted)
            continue

        files = list_folder_files(folder["id"])

        if skip_existing and output_path.exists():
            skipped += 1
        else:
            notes_doc = pick_notes_doc(files)
            if not notes_doc:
                print(f"  {folder['name']}: no notes document found")
                no_notes += 1
            else:
                print(f"  {folder['name']}: fetching '{notes_doc['name']}'...")
                try:
                    content = export_doc_as_markdown(notes_doc["id"], output_dir)
                except GwsError as e:
                    # Listing surfaces shortcuts whose target doc may be in a
                    # restricted Drive the user can't export from. Don't let one
                    # bad doc kill the whole run.
                    print(f"  {folder['name']}: export failed ({e}); skipping", file=sys.stderr)
                    errors += 1
                else:
                    header = f"# {folder['name']}\n\n"
                    header += f"**Source:** {notes_doc['name']}\n\n---\n\n"
                    with open(output_path, "w") as f:
                        f.write(header + content)
                    fetched += 1

        f2, s2, e2 = fetch_companions_for(
            files, stem, output_dir, skip_existing, folder["name"]
        )
        fetched += f2
        skipped += s2
        errors += e2

    return fetched, skipped, no_notes, errors


def _notes_doc_first(f):
    """Sort key preferring Gemini notes over any other doc sharing a meeting's
    title prefix (transcripts, recaps). The title patterns match on the prefix
    alone, so several docs can map to one output filename; notes should win.
    """
    return (0 if "Notes by Gemini" in f["name"] else 1, f["name"])


def fetch_drive_loose_docs(source, output_dir, skip_existing):
    """Catch Gemini notes that sit loose in the source's parent folder rather
    than inside a per-meeting subfolder.

    The shared-with-me pass cannot see these: when a folder is shared, Drive
    sets sharedWithMe only on the folder, not on the documents inside it, so
    docs filed directly in the parent fall through both other passes. Matches
    by title pattern and writes the same canonical filename the folder pass
    would produce.

    Returns (fetched, skipped, errors).
    """
    pattern = source.get("shared_title_pattern")
    template = source.get("shared_folder_name_template")
    if not (pattern and template):
        return 0, 0, 0

    fetched = skipped = errors = 0
    pat = re.compile(pattern)

    print(f"\n[{source['name']}] Scanning parent folder for loose notes...")
    files = drive_list({
        "q": (
            f"'{source['folder_id']}' in parents and trashed = false and "
            "mimeType = 'application/vnd.google-apps.document'"
        ),
        "fields": "nextPageToken, files(id, name, mimeType)",
        "pageSize": 100,
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    })

    claimed = set()
    for f in sorted(files, key=_notes_doc_first):
        m = pat.match(f["name"])
        if not m:
            continue
        synthetic = template.format(**m.groupdict())
        if synthetic in claimed:
            continue
        claimed.add(synthetic)
        output_path = output_dir / folder_name_to_filename(synthetic)

        if skip_existing and output_path.exists():
            skipped += 1
            continue

        print(f"  [loose] {synthetic}: fetching '{f['name']}'...")
        try:
            content = export_doc_as_markdown(f["id"], output_dir)
        except GwsError as e:
            print(f"  [loose] {synthetic}: export failed ({e}); skipping", file=sys.stderr)
            errors += 1
            continue
        header = (
            f"# {synthetic}\n\n"
            f"**Source:** {f['name']} (loose in parent folder)\n\n---\n\n"
        )
        with open(output_path, "w") as out:
            out.write(header + content)
        fetched += 1

    # Companions filed loose in the parent folder, for the same reason the notes
    # are: a shared folder carries sharedWithMe, the files inside it do not.
    # Needs shared_name_contains to rebuild a per-kind title pattern, since
    # shared_title_pattern is anchored on "Notes by Gemini".
    name_contains = source.get("shared_name_contains")
    if not name_contains:
        return fetched, skipped, errors

    for spec in COMPANION_ARTIFACTS:
        cpat = re.compile(
            rf"^{re.escape(name_contains)} - "
            rf"(?P<y>\d{{4}})/(?P<m>\d{{2}})/(?P<d>\d{{2}}) .* "
            rf"{re.escape(spec['title_suffix'])}$"
        )
        try:
            found = drive_list({
                "q": (
                    f"'{source['folder_id']}' in parents and trashed = false and "
                    f"mimeType = '{spec['mime_type']}'"
                ),
                "fields": "nextPageToken, files(id, name, mimeType)",
                "pageSize": 100,
                "supportsAllDrives": True,
                "includeItemsFromAllDrives": True,
            })
        except GwsError as e:
            print(f"  [loose] {spec['kind']} listing failed ({e}); skipping",
                  file=sys.stderr)
            errors += 1
            continue

        for f in found:
            m = cpat.match(f["name"])
            if not m:
                continue
            stem = folder_name_to_stem(template.format(**m.groupdict()))
            output_path = output_dir / f"{stem}{spec['extension']}"
            if skip_existing and output_path.exists():
                skipped += 1
                continue
            print(f"  [loose] {stem}: fetching {spec['kind']}...")
            try:
                content = fetch_companion(spec, f, output_dir)
            except GwsError as e:
                print(f"  [loose] {stem}: {spec['kind']} failed ({e}); skipping",
                      file=sys.stderr)
                errors += 1
                continue
            output_path.write_text(content, encoding="utf-8")
            fetched += 1

    return fetched, skipped, errors


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

    claimed = set()
    for f in sorted(candidates, key=_notes_doc_first):
        m = pat.match(f["name"])
        if not m:
            continue
        synthetic = template.format(**m.groupdict())
        if synthetic in claimed:
            continue
        claimed.add(synthetic)
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

    # Companions for the same unfiled meetings. Each needs its own query: the
    # shared-with-me listing filters on mimeType, and chat (text/plain) and
    # attendance (a Sheet) are neither Docs nor each other. The title pattern is
    # rebuilt per kind rather than reusing shared_title_pattern, which is
    # anchored on "Notes by Gemini".
    for spec in COMPANION_ARTIFACTS:
        cpat = re.compile(
            rf"^{re.escape(name_contains)} - "
            rf"(?P<y>\d{{4}})/(?P<m>\d{{2}})/(?P<d>\d{{2}}) .* "
            rf"{re.escape(spec['title_suffix'])}$"
        )
        cq = (
            "sharedWithMe = true and trashed = false and "
            f"mimeType = '{spec['mime_type']}' and "
            f"name contains '{safe_contains}'"
        )
        try:
            found = drive_list({
                "q": cq,
                "fields": "nextPageToken, files(id, name, mimeType)",
                "pageSize": 100,
                "supportsAllDrives": True,
                "includeItemsFromAllDrives": True,
            })
        except GwsError as e:
            print(f"  [shared] {spec['kind']} listing failed ({e}); skipping",
                  file=sys.stderr)
            errors += 1
            continue

        for f in found:
            m = cpat.match(f["name"])
            if not m:
                continue
            synthetic = template.format(**m.groupdict())
            stem = folder_name_to_stem(synthetic)
            output_path = output_dir / f"{stem}{spec['extension']}"
            if skip_existing and output_path.exists():
                skipped += 1
                continue
            print(f"  [shared] {synthetic}: fetching {spec['kind']}...")
            try:
                content = fetch_companion(spec, f, output_dir)
            except GwsError as e:
                print(f"  [shared] {synthetic}: {spec['kind']} failed ({e}); skipping",
                      file=sys.stderr)
                errors += 1
                continue
            output_path.write_text(content, encoding="utf-8")
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
            f2, s2, e2 = fetch_drive_loose_docs(
                source, output_dir, args.skip_existing
            )
            fetched += f2
            skipped += s2
            total_errors += e2
            f3, s3, e3 = fetch_drive_shared_fallback(
                source, output_dir, args.skip_existing
            )
            fetched += f3
            skipped += s3
            total_errors += e3
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
