"""Grade every committed case against checker.evaluate. Read-only.

For each case file: check that it is a candidate case pinned to the section
7.4 text in AGAINST, resolve the named Observed Effect record to its bytes,
check the bytes against the pinned SHA-256, build the checker input from
`checker_input` alone, evaluate, and compare the outcome with `expected`. The
expectation never reaches the checker. Nothing is written; any mismatch,
missing record, hash mismatch or case pinned to other text exits non-zero.

Records come only from the installed `agent-evidence-vectors` package: the
published corpus at the release requirements.txt pins by hash.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from importlib import resources
from typing import Any

import checker

HERE = os.path.dirname(os.path.abspath(__file__))

# The text every case is graded against: section 7.4 as merged through #219.
# Repinning the cases to an amended 7.4 changes this constant and every case
# file together, so no case can silently stay graded against older text.
AGAINST = {
    "document": "whitepapers/agent-containment.md",
    "section": "7.4",
    "commit": "84604125869469926968acdf433501f87d1d1665",
}
STATUS = "candidate"
FAILURES = (
    checker.MalformedEvidence,
    checker.UnsupportedVerification,
    checker.CandidateInputError,
)


def record_bytes(vector: str) -> bytes:
    published = resources.files("agent_evidence_vectors").joinpath(
        "corpora", "vectors-observed-effect", "statements", f"{vector}.json"
    )
    if not published.is_file():
        raise FileNotFoundError(f"record {vector} is not in the installed corpus")
    return published.read_bytes()


def build_input(case: dict[str, Any]) -> dict[str, Any]:
    spec = case["checker_input"]
    ref = spec["evidence"]["observed_effect"]
    raw = record_bytes(ref["vector"])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ref["sha256"]:
        raise ValueError(
            f"record {ref['vector']} hashes to {digest}, case pins {ref['sha256']}"
        )
    return {
        "property": spec["property"],
        "evidence": {"envelope": raw},
        "context": {
            "claim_ref": spec["context"]["claim_ref"],
            "observer_public_key": spec["context"]["observer_public_key"],
            "anchored_commitment_digest": spec["context"].get(
                "anchored_commitment_digest"
            ),
            "producer_capability": spec["context"].get("producer_capability"),
            "producer": spec["context"].get("producer"),
            "independence_evidence": spec["context"].get("independence_evidence"),
        },
    }


def outcome(checker_input: dict[str, Any]) -> dict[str, Any]:
    try:
        result = checker.evaluate(checker_input)
    except FAILURES as exc:
        out: dict[str, Any] = {
            "verdict": None,
            "processing_failure": type(exc).__name__,
        }
        if isinstance(exc, checker.MalformedEvidence):
            out["codes"] = exc.codes
        return out
    prop = checker_input["property"]
    ctx = checker_input["context"]
    expected_evaluation = {
        "property": {"name": prop["name"], "scope": prop["scope"]},
        "context": {
            "claim_ref": ctx["claim_ref"],
            "observer_public_key": ctx["observer_public_key"],
            "anchored_commitment_digest": ctx.get("anchored_commitment_digest"),
            "producer_capability": ctx.get("producer_capability"),
            "producer": ctx.get("producer"),
            "independence_evidence": ctx.get("independence_evidence"),
        },
    }
    if result.get("evaluation") != expected_evaluation:
        raise ValueError("checker result is not bound to the evaluated property and context")
    axis = "outcome" if "outcome" in result else "verdict"
    return {axis: result[axis], "unmet_obligation": result["unmet_obligation"]}


# The observer-independence cases are graded against the independence test
# proposed for 7.4 on #240, as worded in the commit below, not against the
# merged 7.4: that test is not merged text yet.
AGAINST_INDEPENDENCE = {
    "document": "whitepapers/agent-containment.md",
    "section": "7.4",
    "commit": "672b8c50502274be634b05c6a11a7ad69330936b",
}
PINS = {"RFC189-OE-": AGAINST, "RFC189-IND-": AGAINST_INDEPENDENCE}


def check_pin(case: dict[str, Any]) -> None:
    case_id = case.get("id", "")
    against = next((pin for pre, pin in PINS.items() if case_id.startswith(pre)), None)
    if against is None:
        raise ValueError(f"case id {case_id!r} belongs to no pinned case set")
    if case.get("status") != STATUS or case.get("against") != against:
        raise ValueError(
            f"case is not a {STATUS} case pinned to section {against['section']} "
            f"at {against['commit'][:8]}"
        )


def main() -> int:
    case_dir = os.path.join(HERE, "cases")
    names = sorted(n for n in os.listdir(case_dir) if n.endswith(".json"))
    if not names:
        print("no cases found", file=sys.stderr)
        return 2
    mismatches = 0
    for name in names:
        with open(os.path.join(case_dir, name), encoding="utf-8") as fh:
            case = json.load(fh)
        try:
            check_pin(case)
            got = outcome(build_input(case))
        except (OSError, ValueError, KeyError) as exc:
            print(f"ERROR {case.get('id', name)}: {exc}")
            mismatches += 1
            continue
        want = case["expected"]
        ok = got == want
        mismatches += not ok
        status = "ok  " if ok else "FAIL"
        print(f"{status} {case['id']}: {json.dumps(got, sort_keys=True)}")
        if not ok:
            print(f"     expected {json.dumps(want, sort_keys=True)}")
    print(f"{len(names) - mismatches} of {len(names)} cases match their expectation")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
