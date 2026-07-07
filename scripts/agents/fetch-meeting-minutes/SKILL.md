---
name: fetch-meeting-minutes
description: >-
  Sync CoSAI meeting minutes into `meeting_minutes/`. Pulls Gemini-generated
  meeting notes from the workstream/SIG Google Drive folders (via a Google
  Drive MCP server) and the TSC minutes from GitHub, exports each as markdown,
  and writes them under `meeting_minutes/<subdir>/`. Use before drafting an
  agenda, or on a schedule, to refresh the local minutes the meeting-agenda
  agent reads. Trigger phrases: "fetch meeting minutes", "sync minutes",
  "update meeting notes".
---

# Fetch CoSAI Meeting Minutes

**Version:** 1.0.0

You sync CoSAI meeting minutes into the repo so the `meeting-agenda` agent has
fresh material to read. This replaces the old `scripts/fetch_meeting_minutes.py`
one-shot script: instead of shelling out to the `gws` CLI, you drive a **Google
Drive MCP server** for the Drive sources and the **GitHub CLI** for the TSC
source. Same inputs, same output layout — just run by a person through their
assistant, with no local Python/`gws` toolchain to install.

You are a **fetcher, not an editor**: you export minutes verbatim and write them
to disk. You do not summarise, rewrite, or post anything.

---

## Prerequisites

Before doing any Drive work, confirm a **Google Drive MCP server is connected**.
Check the assistant's available tools/connectors for Drive capabilities (listing
files, searching, reading/exporting a Google Doc).

**If no Drive MCP is connected, stop and help the user add one**, then resume:

- In Claude Code / Claude Desktop: connect the **Google Drive** connector, or add
  a Drive MCP server, e.g.:

  ```bash
  claude mcp add gdrive -- npx -y @modelcontextprotocol/server-gdrive
  ```

  then complete the OAuth flow so the server has the `drive.readonly` scope.
- Any Drive MCP that can (a) list files in a folder, (b) search
  `sharedWithMe`, and (c) export a Google Doc as text/markdown will do. If the
  connected server exposes differently-named tools, map them to the three
  capabilities used below.

For the **TSC (GitHub) source** you need the `gh` CLI authenticated (`gh auth
status`). No Drive access is required for that source.

Do **not** silently fall back to any other path if the Drive MCP is missing —
halt and tell the user exactly what to connect.

---

## Input

- `--skip-existing` (optional) — skip any meeting whose output file already
  exists. Use this for routine/scheduled refreshes; omit it for a full re-sync.

Output goes under `meeting_minutes/<subdir>/` **relative to the repository root**
(the working directory), one markdown file per meeting. Do not hard-code an
absolute home path.

---

## Sources

Each source is either a **drive** source (a parent Drive folder containing
per-meeting subfolders, each holding a Gemini "Notes by Gemini" doc) or a
**github** source (a repo directory of committed markdown minutes).

| Name | Type | Subdir | Drive folder ID / GitHub path | Shared-with-me title pattern (fallback) | Synthetic filename |
|------|------|--------|-------------------------------|------------------------------------------|--------------------|
| WS4 | drive | `ws4` | `1TJl4yqWIdfPc8fKWiTO0CsmsmuecGxWa` | `^CoSAI WS4 recurring meeting - (Y)/(M)/(D) .* Notes by Gemini$` | `WS4 {y}{m}{d}` |
| ADLC | drive | `adlc` | `1EkoOpMCtYahLu-sEhYrgNDmvPyTtgpit` | `^WS4 SIG Security of Agent Development Lifecycle - (Y)/(M)/(D) .* Notes by Gemini$` | `{y}-{m}-{d}` |
| WS3 | drive | `ws3` | `1NFk_-2Plyi3qYr2qtrvt42AQhzJZB0Wf` | _(none — folder-walk only)_ | — |
| Code-SIG | drive | `code-sig` | `1yKk-Mbbpowsk3gfRwGIT7UpMOJ-fDzdo` | `^CoSAI WS3 SIG: Security of AI-Assisted Code Development - (Y)/(M)/(D) .* Notes by Gemini$` | `{y}-{m}-{d}` |
| RM-SIG | drive | `rm-sig` | `1tboOFAyYHnJRlXqMO3Kdh6KrcAVVIpiB` | `^CoSAI WS3 CoSAI-RM SIG weekly meeting - (Y)/(M)/(D) .* Notes by Gemini$` | `WS3 CoSAI-RM SIG {y}{m}{d}` |
| Agent-Credentials | drive | `agent-credentials` | `1Telz7CDwCgPNUyHlMwu9cBGl-keqP9z3` | `^CoSAI WS4: Agent Credentials - (Y)/(M)/(D) .* Notes by Gemini$` | `{y}-{m}-{d}` |
| TSC | github | `tsc` | `cosai-oasis/cosai-tsc` → `tsc-meeting-minutes` | — | (repo filename) |

In the patterns, `(Y)/(M)/(D)` is `YYYY/MM/DD`; the synthetic filename uses the
captured `y`/`m`/`d` (so `WS4 {y}{m}{d}` → `WS4 20260709`).

---

## Procedure

Create `meeting_minutes/` and each source's `meeting_minutes/<subdir>/` if
absent. Then process every source:

### Drive sources — folder walk (primary)

1. **List meeting subfolders** in the source's parent folder ID (folders only,
   not trashed). Sort by name for stable output.
2. For each subfolder, compute the output filename by normalising the folder
   name: collapse whitespace to single hyphens, append `.md` (e.g.
   `WS4 20260402` → `WS4-20260402.md`).
3. If `--skip-existing` and that file already exists, skip.
4. **Find the notes doc** in the subfolder: prefer a Google Doc whose name
   contains `Notes by Gemini`; otherwise take any resolvable Google Doc. If the
   match is a **shortcut** to a Doc, resolve to the shortcut's target Doc.
5. **Export the Doc as markdown/plain text** via the Drive MCP.
6. Write the file with a header, then the exported body:

   ```markdown
   # <folder name>

   **Source:** <doc name>

   ---

   <exported content>
   ```

7. If an export fails (e.g. a shortcut into a restricted Drive you can't read),
   log it and continue — one bad doc must not abort the run.

### Drive sources — shared-with-me fallback

Some Gemini notes are shared directly with the user but not yet filed into a
per-meeting subfolder. For each drive source that defines a title pattern:

1. Search `sharedWithMe = true`, not trashed, Google Docs whose name contains
   the source's fixed prefix.
2. For each candidate matching the full title pattern, build the **synthetic**
   folder name from the captured `y`/`m`/`d`, then the same canonical filename
   the folder-walk pass would produce.
3. Honour `--skip-existing`; export and write exactly as above, but tag the
   header source as `<doc name> (via shared-with-me fallback)`.

Sources without a title pattern (WS3) get folder-walk only — no fallback.

### GitHub source (TSC)

1. List the repo directory via `gh api` (or the Contents API), e.g.:

   ```bash
   gh api repos/cosai-oasis/cosai-tsc/contents/tsc-meeting-minutes --jq '.[] | select(.type=="file" and (.name|endswith(".md"))) | .name'
   ```

2. For each `.md` file (honouring `--skip-existing`), download its raw content
   and write it verbatim to `meeting_minutes/tsc/<name>` — no header rewrite.

---

## Output & report

When done, print a one-line summary per the totals you tracked:

```
Done: <fetched> fetched, <skipped> skipped, <no-notes> without notes, <errors> export errors
```

List any folders with no notes doc and any export errors so the user can chase
missing/ restricted minutes.

---

## Boundaries

This skill does **not**:

- Modify or summarise minute content — export verbatim only.
- Write anywhere except `meeting_minutes/<subdir>/`.
- Post to GitHub, apply labels, or touch `agenda_drafts/`.
- Proceed with Drive sources when no Drive MCP is connected — it halts and asks.

## Failure modes

- **No Google Drive MCP connected** — halt; give the connect/`claude mcp add`
  instruction above. Do not attempt any other Drive path.
- **Drive MCP unauthorised / missing `drive.readonly` scope** — halt with the
  re-auth instruction.
- **`gh` unavailable or unauthenticated** — skip only the TSC source, note it in
  the summary, and continue with Drive sources.
- **A single doc export fails** — log and continue; never abort the whole run.

## Governance

- **License:** CC-BY-4.0
- **AI attribution:** AI-assisted commits use `Co-authored-by: AI Assistant
  <ai-assistant@coalitionforsecureai.org>` per the CoSAI vendor-neutral
  attribution convention (cosai-oasis/secure-ai-tooling#149).
