# WS4 tooling scripts

## `fetch_meeting_minutes.py`

Syncs CoSAI meeting artifacts into `meeting_minutes/<subdir>/`. It pulls
Gemini-generated notes from the workstream/SIG **Google Drive** folders and the
TSC minutes from **GitHub**.

```bash
python scripts/fetch_meeting_minutes.py                 # fetch everything
python scripts/fetch_meeting_minutes.py --skip-existing  # only what is missing
```

Output lands under `meeting_minutes/` in whatever clone you run it from.

### What it pulls per meeting

Google Meet emits four artifacts per call. Three of them are worth having:

| File | Source artifact | Why |
|---|---|---|
| `WS4-20260903.md` | Notes by Gemini | the summary |
| `WS4-20260903-chat.txt` | Chat | **links, side-questions and corrections the notes drop** |
| `WS4-20260903-attendance.csv` | Attendance | who was in the room, and for how long |

The chat log is consistently the highest-value-per-byte of the three: it is
where people paste the issue and document links that the notes only allude to,
and where mis-statements get corrected in the moment.

Two things worth knowing about how these are stored:

- **Chat and attendance are usually not filed into the per-meeting subfolder.**
  Those folders typically hold only the notes doc, so both artifacts are
  recovered by the shared-with-me pass instead. Both passes handle both.
- **Attendance is a recent addition.** Expect it on recent meetings only;
  its absence on older ones is not an error and is not reported as one.

There is **no transcript document** — Meet does not generate one for these
calls. To get one, transcribe the recording locally; see below.

### Transcribing a recording

Worth the ~20 minutes when the notes are load-bearing. The Sept 3 2026 WS4
transcript surfaced an entire WS4 subgroup that appeared in no written artifact.

```bash
# 1. find the recording (mimeType video/mp4; ~700 MB per hour)
gws drive files list --params '{"q": "name contains '"'"'CoSAI WS4 recurring meeting'"'"' and trashed=false", "fields": "files(id,name,mimeType,size)", "pageSize": 100}'

# 2. download it -- note: `files get` with alt=media, NOT `files download`,
#    which returns a long-running-operation envelope and writes nothing.
#    -o must be a relative path inside the current directory.
gws drive files get --params '{"fileId": "<id>", "alt": "media"}' -o recording.mp4

# 3. extract 16 kHz mono audio
ffmpeg -nostdin -v error -y -i recording.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le audio.wav

# 4. transcribe
whisper audio.wav --model medium --language en --fp16 False \
  --output_format txt --initial_prompt "CoSAI, CoSAI-RM, MCP, ADLC, OCSF, OpenTelemetry, ODIS, WIMSE, MITRE ATLAS, TSC, PGB, OASIS. Sarah Novotny, Ian Molloy, Claudia Rauch, David LaBianca, David Pierce, Emrick Donadei, Rithikha Rajamohan, Benedict Lau, Josiah Hagen, Bill Stout, Raymond Sheh, Shriti Priya, Kevin Calloway, Jeff Leva, John Cavanaugh, Kapil Singh."
```

- Use **`medium`** — about 4x realtime on an M-series Mac, so ~15 min for an
  hour-long call. **`large-v3` is not worth it here**: it failed to finish a
  180-second slice in 10 minutes on the same machine.
- The `--initial_prompt` is not optional in practice. Without it the model
  produces Josiah→"Chasaya", Emrick→"Emmerich", Parul→"a parole", ODIS→"Otis",
  OTEL→"hotel", Grok→"Croc".
- Whisper does **no speaker diarization**. Attribute speakers by
  cross-referencing the notes, chat log and attendance — and say so before
  quoting anyone.

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
