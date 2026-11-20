# Task-grouped rates: a synthetic software example

**Status:** Informative illustration for [the section 7.2 rate amendment](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/233) and [containment issue #172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172), following the editor's [worked-record invitation](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219#issuecomment-5973362587). All task and episode labels are authored. The calculations are reproducible over those labels; matching and task independence are declared assumptions.

**Scope:** This example uses software-task labels. Physical-actuation evidence belongs in companion material with independently observed physical outcomes, sensing scope and domain safety engineering.

## What is retained

- `input.json` holds four tasks, each with an attack arm and a benign arm, explicit episode IDs, failure/success/unresolved labels and redundant counts. Both arms declare the same conditions and outcome criterion; their declared intervention differs.
- `report.json` is the expected output from the source-pinned [Atlas reader](https://github.com/probityai/agent-evidence-atlas/blob/ec68111f4b68a27c9932e4eb67a525a4404d97d7/tools/check_grouped_rates.py), including exact rational rates, every paired task draw and input/reader hashes.
- `source.json` identifies the immutable reader source and the SHA-256 hashes of the copied input and expected report. The [Open Evidence Lab](https://probityai.github.io/agent-evidence-atlas/lab.html) is the companion hub; the files here keep the worked calculation available in-repo.

The labels deliberately include unequal task sizes and one unresolved episode in each arm of T04. Counts are checked against the retained episode labels before calculating rates.

| Task | Attack failures / resolved | Benign failures / resolved | Unresolved per arm | Attempts per arm |
| --- | --- | --- | --- | --- |
| T01 | 8 / 10 | 2 / 10 | 0 | 10 |
| T02 | 3 / 4 | 1 / 4 | 0 | 4 |
| T03 | 0 / 2 | 1 / 2 | 0 | 2 |
| T04 | 1 / 2 | 0 / 2 | 1 | 3 |
| Total | 12 / 18 | 4 / 18 | 1 | 19 |

## The aggregation rule changes the question

For the episode-weighted resolved rate, sum failures and resolved episodes within each arm, then divide. For the equal-task resolved rate, calculate each declared task's failure proportion and average all four proportions with equal weight. The contrast is attack minus benign under the same aggregation rule.

| Estimand | Attack | Benign | Attack minus benign |
| --- | --- | --- | --- |
| Episode-weighted resolved rate | 2/3 | 2/9 | 4/9 |
| Equal-task resolved rate | 41/80 | 19/80 | 11/40 |

Both calculations preserve the four tasks. Their difference comes from the declared weighting, not a new measurement. Unresolved labels stay in the record and are excluded only from the disclosed resolved denominators. The report also gives all-attempt failure bounds: assign every unresolved label first to success, then to failure. For example, the attack arm spans 12/19 through 13/19 under those two completions.

## Compute uncertainty over the task groups

Each draw selects four tasks with replacement. A selected task brings both arms and every episode in those arms with it; the contrast is recomputed jointly. This example enumerates all 4^4 = 256 ordered task draws, preserving each tuple and its exact rational statistics. It therefore needs no random seed.

The method is `paired-task-bootstrap-percentile-v1`, with nominal level `0.95`. Percentiles use the left inverse empirical CDF: rank `max(1, ceil(p * B))`, without interpolation. The exact enumeration is a property of the empirical resampling distribution. Repeated-sampling coverage remains unestablished for this authored four-task population: `intervalCoverageEstablished` is `false`, and `independentUnitsVerified` is `null`.

A real application must justify independent exchangeable task clusters and state residual dependence, such as tasks sharing an agent, session or scene. Repeating episodes within an existing task adds no independently sampled tasks. A zero resolved denominator yields a null rate. Every undefined draw is retained, and it blocks the affected percentile interval rather than being silently removed. An undefined task rate also blocks the equal-task statistic over the declared task population.

## Reproduce the retained report

Run from this directory with Python 3.11 or later and Git. The reader uses only the Python standard library. The checkout is temporary; its source revision and byte hash come from `source.json`.

```bash
git clone --no-checkout https://github.com/probityai/agent-evidence-atlas.git .atlas-reader
python3 - <<'PY'
from pathlib import Path
import hashlib
import json
import subprocess
import sys

source = json.loads(Path("source.json").read_text(encoding="utf-8"))
for name in ("input.json", "report.json"):
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != source["sha256"][name]:
        raise SystemExit(f"copied file hash mismatch: {name}")
subprocess.run(
    ["git", "-C", ".atlas-reader", "checkout", "--detach", source["upstreamCommit"]],
    check=True,
)
reader = Path(".atlas-reader") / source["upstreamReaderPath"]
actual = hashlib.sha256(reader.read_bytes()).hexdigest()
if actual != source["sha256"]["reader"]:
    raise SystemExit("reader source hash mismatch")
subprocess.run(
    [sys.executable, str(reader), "--input", "input.json", "--expect", "report.json",
     "--output", "reproduced-report.json"],
    check=True,
)
PY
```

A successful run reconstructs the retained arithmetic and checks the whole expected report. Evidence for a real deployment also needs supported outcome labels, actual matched conditions, a justified sampling unit and observation coverage; those obligations stay open in this illustration. The contrast here is descriptive, and no robot or agent was run to produce its labels.
