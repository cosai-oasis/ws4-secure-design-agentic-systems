"""Grade every committed case with a published verifier. Read-only.

First check that section 7.4 still hashes to the digest in AGAINST, so a change
to the rule cannot leave the cases green. Then, for each case file: check that
it is a candidate case pinned to that digest, resolve the named Observed Effect
record to its bytes, check the bytes against the pinned SHA-256, and hand the
record and `checker_input` alone to `agent_evidence_verify.adjudicate` under the
`evidence_sufficiency/v1` claim type. The verdict it returns is compared with
`expected`, which never reaches the verifier. Nothing in the tree is written;
any mismatch, missing record, hash mismatch or case pinned to other text exits
non-zero. `--summary FILE` appends a plain account of the run to FILE, which CI
shows on the run's summary page. `--paper FILE` reads section 7.4 from FILE
instead of this checkout, for a branch that does not carry the paper.

The verifier and the records come only from installed packages,
`agent-evidence-verify` and `agent-evidence-vectors`, at the releases
requirements.txt pins by hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from importlib import metadata, resources
from pathlib import Path
from typing import Any

from agent_evidence_verify import adjudicate
from agent_evidence_verify.common import CaseError

HERE = os.path.dirname(os.path.abspath(__file__))

# The text every case is graded against: the SHA-256 of section 7.4, from its
# heading up to the next heading. A digest rather than a commit, because it can
# be checked against the paper in this checkout and it can change in the same
# commit as the text. Repinning to an amended 7.4 changes this constant and
# every case file together: `python run.py --text-digest` prints the new value.
AGAINST = {
    "document": "whitepapers/agent-containment.md",
    "section": "7.4",
    "text_sha256": "4b3b4a46bf8220542eb8a0cb290adbdbe9e15d37c7aa158dfbf160d885f01f48",
}
STATUS = "candidate"
CLAIM_TYPE = "evidence_sufficiency/v1"
# A CaseError whose text starts with one of these is a processing failure
# under C2, named as the case files name it. Any other CaseError means the
# harness built a bad input, which is an error of the run, never a verdict.
FAILURES = {
    "malformed_record: ": "MalformedEvidence",
    "unsupported_property: ": "UnsupportedVerification",
    "candidate_input: ": "CandidateInputError",
}
# The verifier's common decision for each claim-level answer.
DECISION = {
    "pass": "supported",
    "absent": "supported",
    "fail": "contradicted",
    "present": "contradicted",
    "not_established": "not_established",
    "pending": "not_established",
}
CONTEXT_KEYS = (
    "anchored_commitment_digest",
    "producer_capability",
    "producer",
    "independence_evidence",
)


def section_digest(text: str) -> str | None:
    """The digest of section 7.4 in `text`, or None if it has no such section."""
    found = re.search(r"^### 7\.4 .*?(?=^#{1,3} )", text, re.MULTILINE | re.DOTALL)
    if found is None:
        return None
    return hashlib.sha256(found.group(0).rstrip(" \n-").encode("utf-8")).hexdigest()


def paper_digest(path: str | None = None) -> str | None:
    path = path or os.path.join(HERE, "..", "..", AGAINST["document"])
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return section_digest(fh.read())


def text_problem(digest: str | None) -> str | None:
    """Why the cases cannot be read against this checkout's text, if they cannot."""
    if digest is None or digest == AGAINST["text_sha256"]:
        return None
    return (
        f"section {AGAINST['section']} hashes to {digest}, the cases pin "
        f"{AGAINST['text_sha256']}"
    )


def record_bytes(vector: str) -> bytes:
    published = resources.files("agent_evidence_vectors").joinpath(
        "corpora", "vectors-observed-effect", "statements", f"{vector}.json"
    )
    if not published.is_file():
        raise FileNotFoundError(f"record {vector} is not in the installed corpus")
    return published.read_bytes()


def build_input(case: dict[str, Any]) -> dict[str, Any]:
    """The verifier's input: the record's bytes plus `checker_input`, nothing else."""
    spec = case["checker_input"]
    ref = spec["evidence"]["observed_effect"]
    raw = record_bytes(ref["vector"])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != ref["sha256"]:
        raise ValueError(
            f"record {ref['vector']} hashes to {digest}, case pins {ref['sha256']}"
        )
    ctx = spec["context"]
    assessment: dict[str, Any] = {
        "claim_type": CLAIM_TYPE,
        "envelope": "envelope.json",
        "observer_public_key": ctx["observer_public_key"],
        "claim_ref": ctx["claim_ref"],
        "property": {"name": spec["property"]["name"], "scope": spec["property"]["scope"]},
    }
    for key in CONTEXT_KEYS:
        if ctx.get(key) is not None:
            assessment[key] = ctx[key]
    return {"case_id": case["id"], "envelope": raw, "assessment": assessment}


def outcome(given: dict[str, Any]) -> dict[str, Any]:
    """Run the verifier on one input and read its answer in the case's terms."""
    raw = given["envelope"]
    assessment = given["assessment"]
    artifacts = {
        "envelope.json": {
            "path": "envelope.json",
            "length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "envelope.json").write_bytes(raw)
        try:
            result = adjudicate(
                {"schema_version": "probity-case/v1", "case_id": given["case_id"],
                 "artifacts": artifacts},
                {"schema_version": "probity-policy/v1",
                 "assessments": {given["case_id"]: assessment}},
                Path(tmp),
            )
        except CaseError as exc:
            text = str(exc)
            prefix = next((p for p in FAILURES if text.startswith(p)), None)
            if prefix is None:
                raise ValueError(f"verifier refused the harness input: {text}") from exc
            out: dict[str, Any] = {"verdict": None, "processing_failure": FAILURES[prefix]}
            if FAILURES[prefix] == "MalformedEvidence":
                out["codes"] = sorted(text[len(prefix):].split(","))
            return out
    scope = result.get("scope", {})
    bound = {key: scope.get(key) for key in ("claim_ref", *CONTEXT_KEYS)}
    asked = {key: assessment.get(key) for key in ("claim_ref", *CONTEXT_KEYS)}
    if scope.get("property") != assessment["property"] or bound != asked:
        raise ValueError("verifier result is not bound to the evaluated property and context")
    checks = result.get("checks") or []
    if len(checks) != 1:
        raise ValueError(f"verifier returned {len(checks)} checks, expected one")
    check = checks[0]
    axis = "outcome" if "outcome" in check else "verdict"
    if DECISION.get(check[axis]) != result.get("decision"):
        raise ValueError(
            f"verifier decision {result.get('decision')!r} does not follow from {check[axis]!r}"
        )
    return {axis: check[axis], "unmet_obligation": check["unmet_obligation"]}


# Both case sets now read merged text, so both carry the same pin.
PINS = {"RFC189-OE-": AGAINST, "RFC189-IND-": AGAINST}


def check_pin(case: dict[str, Any]) -> None:
    case_id = case.get("id", "")
    against = next((pin for pre, pin in PINS.items() if case_id.startswith(pre)), None)
    if against is None:
        raise ValueError(f"case id {case_id!r} belongs to no pinned case set")
    if case.get("status") != STATUS or case.get("against") != against:
        raise ValueError(
            f"case is not a {STATUS} case pinned to section {against['section']} "
            f"at text {against['text_sha256'][:12]}"
        )


MEANING = {
    "ok": "The verifier reached the answer the case expects.",
    "FAIL": (
        "The verifier reached a different answer from the case. Either the verifier "
        "changed or the expectation did; the clauses say which part of 7.4 decides."
    ),
    "ERROR": (
        "The case could not be graded: its record is missing, or the record's bytes "
        "miss the digest the case pins, or the case is pinned to other text. No "
        "verdict was reached."
    ),
}


def answer(got: dict[str, Any]) -> str:
    return str(got.get("verdict") or got.get("outcome") or got.get("processing_failure"))


def summary(
    rows: list[dict[str, Any]], digest: str | None, problem: str | None, paper: str | None = None
) -> str:
    good = sum(row["status"] == "ok" for row in rows)
    counts: dict[str, int] = {}
    for row in rows:
        if row["status"] == "ok":
            counts[row["answer"]] = counts.get(row["answer"], 0) + 1
    lines = [
        f"## Section 7.4 cases: {good} of {len(rows)} match their expectation",
        "",
        "Each case gives a verifier one signed record and one question, and states the "
        "answer section 7.4 requires. The cases test what a verifier may conclude from "
        "the evidence. They do not test a sandbox or a deployment, the fixtures are "
        "synthetic, and a pass here says nothing about whether any real system holds.",
        "",
        f"- Rule: `{AGAINST['document']}` section {AGAINST['section']}, text digest "
        f"`{AGAINST['text_sha256'][:12]}`",
        "- Text check: "
        + (
            "this checkout has no section 7.4 to compare, so this run did not check it"
            if digest is None
            else f"MISMATCH, {problem}"
            if problem
            else f"section 7.4 {'in ' + os.path.basename(paper) if paper else 'in this checkout'} "
            "matches that digest"
        ),
        f"- Verifier: agent-evidence-verify {metadata.version('agent-evidence-verify')}, "
        f"claim type `{CLAIM_TYPE}`, installed by hash",
        f"- Records: agent-evidence-vectors {metadata.version('agent-evidence-vectors')}, "
        "installed by hash; each case pins its record by SHA-256",
        "",
        "| Answer the verifier reached | Cases |",
        "| --- | --- |",
    ]
    lines += [f"| `{name}` | {counts[name]} |" for name in sorted(counts)]
    lines += [
        "",
        "`pass` and `fail` settle the claim. `not_established` means the evidence cannot "
        "settle it, and names what is missing. `present`, `absent` and `pending` are "
        "observation states for an action's outcome. A processing failure means the "
        "input could not be evaluated, which is never a verdict.",
    ]
    bad = [row for row in rows if row["status"] != "ok"]
    if problem:
        lines += [
            "",
            f"**The rule changed.** {problem}. Read what changed in 7.4, decide whether "
            "any expectation moves, then repin with `python run.py --text-digest`.",
        ]
    if bad:
        lines += ["", "### Cases to look at", ""]
    for row in bad:
        lines.append(f"- **{row['id']}** ({row['status']}): {MEANING[row['status']]}")
        lines.append(f"  - Reached: `{row['got']}`")
        if row.get("want"):
            lines.append(f"  - Expected: `{row['want']}`")
        if row.get("clauses"):
            lines.append(f"  - Clauses: {', '.join(row['clauses'])}")
        if row.get("note"):
            lines.append(f"  - What the case tests: {row['note']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grade the section 7.4 cases.")
    parser.add_argument("--summary", metavar="FILE", help="append a plain account of the run")
    parser.add_argument(
        "--text-digest", action="store_true", help="print the digest of 7.4 in this checkout"
    )
    parser.add_argument("--paper", metavar="FILE", help="read section 7.4 from FILE")
    args = parser.parse_args(argv)
    digest = paper_digest(args.paper)
    if args.text_digest:
        print(digest)
        return 0 if digest else 2
    problem = text_problem(digest)
    if args.paper and digest is None:
        # A paper named on the command line must be checked, never skipped.
        problem = f"{args.paper} has no section {AGAINST['section']} to compare"
    case_dir = os.path.join(HERE, "cases")
    names = sorted(n for n in os.listdir(case_dir) if n.endswith(".json"))
    if not names:
        print("no cases found", file=sys.stderr)
        return 2
    mismatches = 0
    rows: list[dict[str, Any]] = []
    for name in names:
        with open(os.path.join(case_dir, name), encoding="utf-8") as fh:
            case = json.load(fh)
        row = {
            "id": case.get("id", name),
            "clauses": case.get("clauses"),
            "note": case.get("note"),
        }
        rows.append(row)
        try:
            check_pin(case)
            got = outcome(build_input(case))
        except (OSError, ValueError, KeyError) as exc:
            print(f"ERROR {row['id']}: {exc}")
            row.update(status="ERROR", got=str(exc))
            mismatches += 1
            continue
        want = case["expected"]
        ok = got == want
        mismatches += not ok
        status = "ok  " if ok else "FAIL"
        print(f"{status} {case['id']}: {json.dumps(got, sort_keys=True)}")
        row.update(status=status.strip(), got=json.dumps(got, sort_keys=True), answer=answer(got))
        if not ok:
            print(f"     expected {json.dumps(want, sort_keys=True)}")
            row["want"] = json.dumps(want, sort_keys=True)
    print(f"{len(names) - mismatches} of {len(names)} cases match their expectation")
    if problem:
        print(f"TEXT {problem}")
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(summary(rows, digest, problem, args.paper))
    return 1 if mismatches or problem else 0


if __name__ == "__main__":
    sys.exit(main())
