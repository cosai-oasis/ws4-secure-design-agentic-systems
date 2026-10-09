"""Check every RFC-149 declaration-to-action pair against the pinned readers.

Each pair names a field of the sample Agent Registration Record from
cosai-oasis/ws4-odis#35 by JSON pointer, and two members of a published corpus:
one the reader accepts and one it rejects, differing in one field. The harness
checks the parts that are facts:

- the vendored sample record has the bytes it was copied with, and the pointer
  resolves in it;
- each member's bytes match the digest the pair pins;
- where the corpus records which member a reject was derived from, it is the
  accept member of the same pair;
- the pinned reader reaches the stated verdict on both members.

The consumer result on each side is the candidate expectation for review under
RFC-149; the harness checks that it is well formed and that an open result
names its unmet obligation. Nothing is written; any mismatch exits non-zero.

Readers: `auditrecord` from the `agent-evidence-vectors` package, and
`aee-verify` (the Go reader at the same tag) for the artifact-binding corpus,
found on PATH or through $AEE_VERIFY.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from functools import cache
from importlib import resources
from typing import Any

from agent_evidence_vectors import auditrecord

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = "agent-evidence-vectors==0.17.5"
STATUS = "candidate"

# The sample record from cosai-oasis/ws4-odis#35, copied byte for byte.
RECORD_PATH = os.path.join(HERE, "record", "sample-registration-record.json")
RECORD_SHA256 = "7cb8b12737018224ab7bcd85ba2dd2d5019b58843352ea8730001eea204b19a4"

# The scope bullets of RFC-149 at 3a38845e that a pair exercises.
RFC_SCOPE = frozenset(
    {"typed-references", "deployment-profile", "policy-profile-ref", "who-may-update", "runtime-appraisal"}
)
RESULTS = frozenset({"pass", "fail", "not_established", "processing_failure"})
READERS = {"vectors-artifact-binding": "aee-verify", "vectors-agent-audit-record": "auditrecord"}


def corpus(name: str) -> Any:
    return resources.files("agent_evidence_vectors").joinpath("corpora", name)


@cache
def manifest(name: str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(corpus(name).joinpath("MANIFEST.json").read_text())
    return loaded


def entry(name: str, member: str) -> dict[str, Any]:
    for item in manifest(name)["vectors"]:
        if item["id"] == member:
            found: dict[str, Any] = item
            return found
    raise KeyError(f"{member} is not a member of {name} in {SOURCE}")


def member_bytes(name: str, member: str) -> bytes:
    item = entry(name, member)
    data: bytes = corpus(name).joinpath(item.get("file") or item["manifest"]).read_bytes()
    return data


@cache
def aee_verify_verdicts(name: str) -> dict[str, str]:
    binary = os.environ.get("AEE_VERIFY") or shutil.which("aee-verify")
    if not binary:
        raise FileNotFoundError("aee-verify is not on PATH and $AEE_VERIFY is unset")
    done = subprocess.run([binary, "-json", str(corpus(name))], capture_output=True, text=True, check=True)
    return {m["id"]: m["kind"] for m in json.loads(done.stdout)["members"]}


def read(name: str, member: str) -> dict[str, Any]:
    if READERS[name] == "aee-verify":
        return {"verdict": aee_verify_verdicts(name)[member]}
    meta = manifest(name)
    report = auditrecord.verify(
        member_bytes(name, member),
        auditrecord.Policy(
            predicate_type=meta["predicateType"],
            observer_public_key=meta["keys"]["observer"]["publicKey"],
        ),
    )
    out: dict[str, Any] = {"verdict": report.verdict, "codes": report.codes}
    if report.verdict == "valid":
        out["tier"] = report.derived_tier
    return out


def resolve(document: Any, pointer: str) -> Any:
    """RFC 6901 JSON pointer."""
    node = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def check_side(label: str, side: dict[str, Any]) -> list[str]:
    problems = []
    name, member = side["corpus"], side["member"]
    digest = hashlib.sha256(member_bytes(name, member)).hexdigest()
    if digest != side["sha256"]:
        problems.append(f"{label}: member hashes to {digest}, pair pins {side['sha256']}")
    got = read(name, member)
    if got != side["reader_expected"]:
        problems.append(f"{label}: reader returned {got}, pair expects {side['reader_expected']}")
    result = side["consumer_result"]
    if result.get("result") not in RESULTS:
        problems.append(f"{label}: consumer result {result.get('result')!r} is not one of {sorted(RESULTS)}")
    if result.get("result") == "not_established" and not result.get("unmet_obligation"):
        problems.append(f"{label}: a not_established result must name its unmet obligation")
    return problems


def check(pair: dict[str, Any], record: Any) -> list[str]:
    problems = []
    if pair.get("status") != STATUS:
        problems.append(f"status is {pair.get('status')!r}, not {STATUS!r}")
    if pair.get("source") != SOURCE:
        problems.append(f"source is {pair.get('source')!r}, not {SOURCE!r}")
    if pair.get("rfc_scope") not in RFC_SCOPE:
        problems.append(f"rfc_scope {pair.get('rfc_scope')!r} is not a scope bullet of RFC-149")
    try:
        resolve(record, pair["record"]["pointer"])
    except (KeyError, IndexError, ValueError, TypeError):
        problems.append(f"pointer {pair['record']['pointer']} does not resolve in the sample record")
    accept, reject = pair["accept"], pair["reject"]
    if accept["corpus"] != reject["corpus"] or READERS.get(accept["corpus"]) != pair.get("reader"):
        problems.append("both members must come from one corpus, read by that corpus's reader")
    parent = entry(reject["corpus"], reject["member"]).get("parent")
    if parent is not None and parent != accept["member"]:
        problems.append(f"the corpus derives the reject member from {parent}, not from the accept member")
    if accept["consumer_result"]["result"] == "processing_failure":
        problems.append("the accept member must be one the reader accepts")
    problems += check_side("accept", accept)
    problems += check_side("reject", reject)
    return problems


def main() -> int:
    with open(RECORD_PATH, "rb") as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != RECORD_SHA256:
        print("the vendored sample record does not match the bytes copied from ws4-odis#35", file=sys.stderr)
        return 2
    record = json.loads(raw)
    pair_dir = os.path.join(HERE, "pairs")
    names = sorted(n for n in os.listdir(pair_dir) if n.endswith(".json"))
    if not names:
        print("no pairs found", file=sys.stderr)
        return 2
    bad = 0
    for name in names:
        with open(os.path.join(pair_dir, name), encoding="utf-8") as fh:
            pair = json.load(fh)
        try:
            problems = check(pair, record)
        except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
            problems = [f"{type(exc).__name__}: {exc}"]
        bad += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} {pair.get('id', name)}")
        for problem in problems:
            print(f"     {problem}")
    print(f"{len(names) - bad} of {len(names)} pairs check against {SOURCE}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
