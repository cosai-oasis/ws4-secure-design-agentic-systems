# WS4 tooling scripts

## `fetch_meeting_minutes.py`

Syncs CoSAI meeting minutes into `meeting_minutes/<subdir>/` (one markdown file
per meeting). It pulls Gemini-generated notes from the workstream/SIG **Google
Drive** folders and the TSC minutes from **GitHub**.

```bash
python scripts/fetch_meeting_minutes.py                 # fetch everything
python scripts/fetch_meeting_minutes.py --skip-existing  # only new meetings
```

Output lands under `meeting_minutes/` in whatever clone you run it from.

### Prerequisites

- **Drive sources** — the [`gws` CLI](https://github.com/googleworkspace/cli),
  authenticated with the `drive` scope (setup below).
- **GitHub source (TSC)** — none; uses the public Contents API. Set
  `GITHUB_TOKEN` to raise the rate limit if needed.

The Drive queries request shared-drive results
(`supportsAllDrives` / `includeItemsFromAllDrives`), so a Drive tool that only
sees "My Drive" will miss these files — `gws` handles shared drives correctly.

### One-time gws + gcloud + OAuth setup

`gws` needs its own Google Cloud OAuth client — it does not ship credentials.
The fastest path uses `gcloud` to provision everything:

1. Install `gws` from the [releases page](https://github.com/googleworkspace/cli/releases).
2. Install the [`gcloud` CLI](https://cloud.google.com/sdk/docs/install).
3. Run `gws auth setup` — creates a Cloud project, enables the Drive API, and
   configures the OAuth client. See the
   [gws auth docs](https://github.com/googleworkspace/cli#authentication) for
   the manual alternative and for adding yourself as a
   [test user](https://support.google.com/cloud/answer/13463073) on the OAuth
   consent screen.
4. Log in with read-only Drive access: `gws auth login -s drive --readonly`.

Verify:

```bash
gws auth status
gws drive files list --params '{"pageSize": 1}'
```
