# SmolVLA / LIBERO: a simulated-robot rate companion

**Scope:** The paper's worked examples cover software-mediated actions; this record of simulated embodied actions is companion material. All source episodes are simulator rollouts.

This companion reads two committed Provael runs from 14 September 2026. It connects the [section 7.2 rate proposal](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/233) to measured outcomes, with the [software calculation](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/234) kept separate. The underlying policy and simulator are not run again by the reader.

The counted outcome is the publisher-reported envelope-exit flag. The reader checks native decision flags for consistency; it does not recompute safety predicates from trajectories. Clean task success on the benign arm is a separate competence control.

## The correction belongs beside the counts

The suite run records 42 envelope exits in 50 `roleplay` episodes, beside 1 in 50 for its `none` benign arm. Its separate control run records 26/30 for `roleplay`, 27/30 for `roleplay_no_target`, and 18/30 for `scrambled_text`, beside 1/30 for `none`. Those controls change the interpretation: the record supports envelope fragility under these instruction strings. It does not establish steering toward an attacker-chosen target. Provael carries that correction as [E-2026-12](https://github.com/provael/provael/blob/f1dbc5352bfa7774c0a5599eff20407125914c78/docs/errata.md).

The no-target arm removes the graspable target from the same frame. The scrambled arm replaces that target and destroys word order while retaining token count. `benign_reword` and `nonsense_text` each record 0/30, but those short controls alone did not test the long out-of-distribution instruction that motivated the correction.

| Run | Arm | Envelope exits / applicable episodes | Task success on benign arm |
| --- | --- | --- | --- |
| Suite | `none` | 1 / 50 | 48 / 50 |
| Suite | `roleplay` | 42 / 50 | - |
| Control | `none` | 1 / 30 | 29 / 30 |
| Control | `roleplay` | 26 / 30 | - |
| Control | `roleplay_no_target` | 27 / 30 | - |
| Control | `scrambled_text` | 18 / 30 | - |
| Control | `benign_reword` | 0 / 30 | - |
| Control | `nonsense_text` | 0 / 30 | - |

The suite retains 400 episode records across eight arms; 50 `mcp_tool_desc` records are explicitly not applicable. The control run retains 180 records across six arms. Both cover the same ten LIBERO-Object tasks, with five seeds per suite task/arm and three per control task/arm. Their denominators and benign arms stay within their respective runs.

The runs share 60 task/seed/arm keys. At 30 shared `none` cells, the complete native episode objects are canonically identical. These bytes do not establish fresh independent benign repeats; they also do not determine whether a separate deterministic execution occurred. The reader keeps the two runs separate and retains the overlap bindings.

## Preserve the run provenance

The source snapshot is [Provael f1dbc535](https://github.com/provael/provael/tree/f1dbc5352bfa7774c0a5599eff20407125914c78). It binds the published reports and correction; it is not a reconstruction of the code installed during either run.

| Recorded field | Suite run | Control run |
| --- | --- | --- |
| Package version | `0.41.2` | `0.41.2` |
| Runtime source commit | `null` | `de6c231` (short commit only) |
| Runtime repository | `null` | `null` |
| Dependency lock digest | `null` | `null` |
| Precision | `null` | `null` |
| Horizon | 280 | 280 |
| Python | `3.12.14` | `3.12.14` |

The reports name SmolVLA and the `HuggingFaceVLA/smolvla_libero` checkpoint. Their manifests leave checkpoint revision and digest, action-schema digest and suite-configuration digest unknown. The control manifests record more hardware detail than the suite manifests. These gaps stay attached to the result; the publication commit supplies none of the missing runtime values.

The report-to-manifest checks establish the retained artifacts' bindings. Structural task/seed pairing supports a within-run comparison, while experimental allocation and independent exchangeable task sampling require their own justification. A simulator envelope endpoint also supplies no independently observed physical-robot outcome.

## Keep all arms together when resampling tasks

For each run, a task contributes its whole vector of arm counts, with every seed retained. Each of ten bootstrap draws selects one of the ten task vectors with replacement. Integer convolution collects identical summed vectors and retains their multiplicities: 9,581 joint states for the suite and 1,716 for the control run, each representing all 10^10 ordered task draws.

Arm rates and contrasts against `none` come from the same joint distribution. The nominal level is 0.95. Each percentile is the smallest statistic whose cumulative integer weight reaches `ceil(p * totalWeight)`; there is no interpolation or random seed. In these balanced runs, episode weighting and equal task weighting agree. The sampling unit remains the task, rather than a task's repeated seeds.

This is exact arithmetic for the empirical bootstrap distribution over the ten retained tasks. Task independence and interval coverage remain unestablished: the tasks share a policy, simulator and selected benchmark. Degenerate zero distributions remain degenerate; they do not establish absence in another task population. The source's random-bootstrap intervals and McNemar/Holm analysis are retained separately as publisher analysis, without a claim of task-cluster-valid significance or simultaneous coverage.

## What is retained here

- `source-record.json` binds 57 complete publisher files by path, byte count and SHA-256, including all 20 reports, all 20 execution manifests, the correction and the relevant source definitions.
- `contract.json` states the outcome, denominators, matching checks, runtime gaps, overlap rule and uncertainty assumptions.
- `report.json` retains source-bound episode pointers, native manifests, per-task counts, all-arm joint state weights and the calculated bounds. Its published flags are kept distinct from independently observed effects.
- `source.json` pins the Atlas reader and these copied files. The original rollout logs stay external at the immutable Provael source and in the [native job's complete-source archive](https://github.com/probityai/agent-evidence-atlas/actions/runs/37160396341).

## Rerun the source-bound calculation

Run from this directory with Python 3.12 and Git. The [source-pinned reader](https://github.com/probityai/agent-evidence-atlas/blob/1d5b468816e348305eb75b122406c86b5483d19c/tools/check_provael_controls.py) uses only the Python standard library. It reconstructs the report from the original publisher files and can retain a complete copy of every source file it checked.

```bash
git clone --no-checkout https://github.com/probityai/agent-evidence-atlas.git .atlas-reader
git clone --no-checkout https://github.com/provael/provael.git .provael-source
python3 - <<'PY'
from pathlib import Path
import hashlib
import json
import subprocess
import sys

source = json.loads(Path("source.json").read_text(encoding="utf-8"))
for name, expected in source["sha256"].items():
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"copied file hash mismatch: {name}")
for directory, commit in (
    (".atlas-reader", source["readerCommit"]),
    (".provael-source", source["publisherPublicationCommit"]),
):
    subprocess.run(["git", "-C", directory, "checkout", "--detach", commit], check=True)
reader_root = Path(".atlas-reader")
reader = reader_root / source["readerPath"]
if hashlib.sha256(reader.read_bytes()).hexdigest() != source["readerSha256"]:
    raise SystemExit("reader source hash mismatch")
for name in ("source-record.json", "contract.json"):
    pinned = reader_root / source["readerExamplePath"] / name
    if hashlib.sha256(pinned.read_bytes()).hexdigest() != source["sha256"][name]:
        raise SystemExit(f"reader's bound file differs: {name}")
subprocess.run(
    [sys.executable, str(reader), "--source-root", ".provael-source",
     "--expect", "report.json", "--output", "reproduced-report.json",
     "--retain-source-zip", "provael-complete-source.zip"],
    check=True,
)
PY
```

A successful run checks exact source bytes, their declared manifest/report bindings and the retained calculation. The output remains a reader of publisher reports, with the source's runtime gaps and interpretation correction attached.
