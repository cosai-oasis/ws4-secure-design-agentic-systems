"""Checker for section 7.4 of the containment paper over Observed Effect records.

The rule under test is section 7.4, "Evidence sufficiency for absence claims",
of `whitepapers/agent-containment.md` as merged into `feat/containment` at
84604125 (see ../README.md for the clauses and the #189 comments each comes
from). The paper is a working draft, so every case this checker grades is a
candidate case pinned to that text, not a conformance requirement.

The evidence is a signed Observed Effect statement (a DSSE envelope carrying an
in-toto Statement): an observer records a mutation interval, the path scope it
covered, the gaps it did not cover, and every write it saw. The checker tests
whether the vantage is independent. Admission of the record is delegated to
the reference verifier published as the `agent-evidence-vectors` package, so
this file decides only what section 7.4 decides: what the admitted record lets
a verifier conclude.

Properties implemented:

- `no_write_in_scope`, a negative quantified over a path scope and one observed
  interval: "no write occurred under these paths during this interval." Its
  verdict is exactly `pass`, `fail` or `not_established`.
- `action_outcome`, the outcome of the invoked action's write under a path
  scope, reported in section 7's observation states: `present`, `absent` or
  `pending`. C1 keeps an unknown action outcome `pending` after the reporting
  window ends; it never becomes `not_established`.

The outcome axes stay apart, as C1 and C2 require:

- A record the reference verifier refuses as malformed, an unsupported property
  and a structurally invalid candidate input are processing failures. They
  raise; they never become `not_established` or `pending`.
- `not_established` and `pending` always name the unmet obligation.
- Each result carries the property and context used to reach it.

Checker input is {property, evidence, context}. Context may carry an expected
prior commitment and producer capability established outside the record for
this invocation.
The harness expectation is held outside the checker input and compared by
run.py afterwards.
"""

from __future__ import annotations

import base64
import copy
import json
from typing import Any

from agent_evidence_vectors import observedeffect

PREDICATE_TYPE = (
    "https://probityai.github.io/agent-evidence-vectors/predicate/v1/observed-effect"
)
NO_WRITE_IN_SCOPE = "no_write_in_scope"
ACTION_OUTCOME = "action_outcome"
OBSERVER_INDEPENDENCE = "observer_independence"
SUPPORTED_PROPERTIES = frozenset({NO_WRITE_IN_SCOPE, ACTION_OUTCOME, OBSERVER_INDEPENDENCE})

# Obligation names. `observation_coverage` is the name the #189 thread already
# uses. `observation_vantage` is the agent-evidence-vocabulary term for who
# observed: a record the observed party could have written or suppressed is not
# independent evidence of anything it asserts.
OBSERVATION_COVERAGE = "observation_coverage"
OBSERVATION_VANTAGE = "observation_vantage"
OBSERVATION_SCOPE = "observation_scope"
ADMISSIBLE_OBSERVATION = "admissible_observation"
INVOCATION_BINDING = "invocation_binding"
PRODUCER_CAPABILITY_COVERAGE = "producer_capability_coverage"

# The independence test proposed for section 7.4 on #240: three conditions,
# each established by evidence carried in or referenced from the record. The
# order is the order the text lists them, and the first unmet one is named.
INDEPENDENCE_CONDITIONS = (
    ("trust_domain", "observer_trust_domain"),
    ("identity_basis", "observer_identity_basis"),
    ("key_control", "observer_key_control"),
)
_EVIDENCE_FIELDS = ("controlled_by", "established_by", "evidence_ref")

# A record the reference verifier finds coherent but whose own rules refuse its
# claim (verdict `invalid`) is not a processing failure: the verification ran.
# It cannot support pass or fail, so the property is not_established, and the
# refusal code names which premise the record failed to carry.
INVALID_CODE_OBLIGATION = {
    "authoritative-vantage-not-independent": OBSERVATION_VANTAGE,
    "commitment-keyid-not-disjoint": OBSERVATION_VANTAGE,
    "commitment-not-prior": OBSERVATION_VANTAGE,
    "commitment-signature-invalid": OBSERVATION_VANTAGE,
    "authoritative-coverage-incomplete": OBSERVATION_COVERAGE,
    "authoritative-empty-path-scope": OBSERVATION_SCOPE,
    "authoritative-without-observed-rows": OBSERVATION_SCOPE,
}


class MalformedEvidence(Exception):
    """The reference verifier refused the record as malformed. Not a verdict."""

    def __init__(self, codes: list[str]) -> None:
        super().__init__(", ".join(codes))
        self.codes = codes


class UnsupportedVerification(Exception):
    """This checker does not implement the requested property. Not a verdict."""


class CandidateInputError(ValueError):
    """The candidate input is structurally invalid. Not a verdict."""


def _validate(checker_input: Any) -> None:
    """Structural gate, run once before any inference, so no inference branch
    decides what an absent key means."""
    if not isinstance(checker_input, dict):
        raise CandidateInputError("checker input must be an object")
    for key in ("property", "evidence", "context"):
        if not isinstance(checker_input.get(key), dict):
            raise CandidateInputError(f"checker input requires object {key!r}")
    prop = checker_input["property"]
    if not isinstance(prop.get("name"), str) or not prop["name"]:
        raise CandidateInputError("property requires a non-empty string name")
    scope = prop.get("scope")
    if (
        not isinstance(scope, list)
        or not scope
        or not all(isinstance(p, str) and p.startswith("/") for p in scope)
    ):
        raise CandidateInputError(
            "property.scope must be a non-empty list of absolute path prefixes"
        )
    evidence = checker_input["evidence"]
    if not isinstance(evidence.get("envelope"), bytes):
        raise CandidateInputError("evidence.envelope must be the record's bytes")
    ctx = checker_input["context"]
    if not isinstance(ctx.get("claim_ref"), str) or not ctx["claim_ref"]:
        raise CandidateInputError(
            "context requires claim_ref: coverage is bound to one claim instance, "
            "so the evaluated one must be named"
        )
    key = ctx.get("observer_public_key")
    if not isinstance(key, str) or len(key) != 64:
        raise CandidateInputError(
            "context requires the observer's Ed25519 public key as 64 hex characters, "
            "anchored out of band and never read from the record"
        )
    expected_commitment = ctx.get("anchored_commitment_digest")
    if expected_commitment is not None and (
        not isinstance(expected_commitment, str)
        or len(expected_commitment) != 64
        or any(ch not in "0123456789abcdef" for ch in expected_commitment)
    ):
        raise CandidateInputError(
            "context.anchored_commitment_digest must be a 64-character lowercase "
            "hex digest when supplied"
        )
    capability = ctx.get("producer_capability")
    if capability is not None:
        if not isinstance(capability, dict):
            raise CandidateInputError("context.producer_capability must be an object")
        if not isinstance(capability.get("claim_ref"), str) or not capability["claim_ref"]:
            raise CandidateInputError(
                "context.producer_capability.claim_ref must be a non-empty string"
            )
        paths = capability.get("visible_write_paths")
        if not isinstance(paths, list) or not all(
            isinstance(p, str) and p.startswith("/") for p in paths
        ):
            raise CandidateInputError(
                "context.producer_capability.visible_write_paths must be a list "
                "of absolute path prefixes"
            )


def _validate_independence(ctx: dict[str, Any]) -> None:
    producer = ctx.get("producer")
    if not isinstance(producer, str) or not producer:
        raise CandidateInputError(
            "observer_independence requires context.producer: independence holds "
            "between one observer and one named producer"
        )
    evidence = ctx.get("independence_evidence")
    if not isinstance(evidence, dict):
        raise CandidateInputError(
            "observer_independence requires context.independence_evidence as an "
            "object; an absent condition is an empty entry, not an absent object"
        )
    known = {name for name, _ in INDEPENDENCE_CONDITIONS}
    unknown = sorted(set(evidence) - known)
    if unknown:
        raise CandidateInputError(f"unknown independence condition(s) {unknown}")
    for name, entry in evidence.items():
        if not isinstance(entry, dict):
            raise CandidateInputError(f"independence_evidence.{name} must be an object")
        for key, value in entry.items():
            if key not in (*_EVIDENCE_FIELDS, "basis") or not isinstance(value, str):
                raise CandidateInputError(
                    f"independence_evidence.{name}.{key} is not a known string field"
                )


def _under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(
        prefix if prefix.endswith("/") else prefix + "/"
    )


def _overlaps(a: str, b: str) -> bool:
    return _under(a, b) or _under(b, a)


def _not_established(obligation: str, reason: str) -> dict[str, Any]:
    return {
        "verdict": "not_established",
        "unmet_obligation": obligation,
        "reason": reason,
    }


def _evaluate(checker_input: dict[str, Any]) -> dict[str, Any]:
    _validate(checker_input)
    prop = checker_input["property"]
    if prop["name"] not in SUPPORTED_PROPERTIES:
        raise UnsupportedVerification(
            f"property {prop['name']!r} is not implemented by this checker; "
            "no verification of the property was performed"
        )
    if prop["name"] == OBSERVER_INDEPENDENCE:
        _validate_independence(checker_input["context"])
        return _independence_verdict(
            checker_input["context"], checker_input["evidence"]["envelope"]
        )
    verdict = _absence_verdict(
        prop["scope"], checker_input["context"], checker_input["evidence"]["envelope"]
    )
    if prop["name"] == NO_WRITE_IN_SCOPE:
        return verdict
    return _action_outcome(verdict)


# The action outcome is the same evidence read as section 7's observation
# states. An observed write is `present`; an established absence is `absent`.
# Anything the evidence leaves open is an unknown outcome, and C1 keeps it
# `pending` with its unmet obligation, including after the window has ended.
_SETTLED_OUTCOME = {"fail": "present", "pass": "absent"}


def _action_outcome(verdict: dict[str, Any]) -> dict[str, Any]:
    if verdict["verdict"] == "not_established":
        return {
            "outcome": "pending",
            "unmet_obligation": verdict["unmet_obligation"],
            "reason": f"not verified by the end of the window: {verdict['reason']}",
        }
    return {
        "outcome": _SETTLED_OUTCOME[verdict["verdict"]],
        "unmet_obligation": None,
        "reason": verdict["reason"],
    }


def _admit(raw: bytes, ctx: dict[str, Any]) -> dict[str, Any]:
    """Admit the record through the reference verifier. Returns the predicate,
    or a not_established result when the verifier refused the claim."""
    policy = observedeffect.Policy(
        predicate_type=PREDICATE_TYPE, observer_public_key=ctx["observer_public_key"]
    )
    report = observedeffect.verify(raw, policy)
    if report.verdict == "malformed":
        raise MalformedEvidence(report.codes)
    if report.verdict == "invalid":
        code = report.codes[0] if report.codes else ""
        return {
            "refused": _not_established(
                INVALID_CODE_OBLIGATION.get(code, ADMISSIBLE_OBSERVATION),
                f"the reference verifier refused the record ({code}); a refused "
                "record supports neither pass nor fail",
            )
        }
    if report.verdict != "valid":
        raise CandidateInputError(f"unexpected admission verdict {report.verdict!r}")
    return {"predicate": json.loads(base64.b64decode(json.loads(raw)["payload"]))["predicate"]}


def _independence_verdict(ctx: dict[str, Any], raw: bytes) -> dict[str, Any]:
    """Decide "this record's observer is independent of the named producer for
    this claim". Each condition needs an evidence entry that names who controls
    the thing it is about, who established that, and where the evidence is. An
    entry without `evidence_ref` is a declaration; an entry the producer
    controls or established is the producer testifying about itself."""
    admitted = _admit(raw, ctx)
    if "refused" in admitted:
        return admitted["refused"]
    pred = admitted["predicate"]
    if pred["intervalId"] != ctx["claim_ref"]:
        return _not_established(
            OBSERVATION_COVERAGE,
            f"the record covers interval {pred['intervalId']!r}, not the evaluated "
            f"claim {ctx['claim_ref']!r}; independence is recorded per claim",
        )
    vantage = pred["observation"]["vantage"]
    if vantage != "below-observed":
        return _not_established(
            OBSERVATION_VANTAGE,
            f"observation vantage is {vantage!r}; the record places the observer "
            "inside the producer's reach, which fails the first condition",
        )
    producer = ctx["producer"]
    evidence = ctx["independence_evidence"]
    for name, obligation in INDEPENDENCE_CONDITIONS:
        entry = evidence.get(name, {})
        missing = [f for f in _EVIDENCE_FIELDS if not entry.get(f)]
        if missing:
            return _not_established(
                obligation,
                f"{name}: no evidence establishes this condition (missing {missing}); "
                "a declaration does not establish independence",
            )
        held = [f for f in ("controlled_by", "established_by") if entry[f] == producer]
        if held:
            return _not_established(
                obligation,
                f"{name}: {held} is the producer {producer!r}; the producer cannot "
                "establish its own observer's independence",
            )
    return {
        "verdict": "pass",
        "unmet_obligation": None,
        "reason": "each independence condition is established by evidence that the "
        "producer neither controls nor issued",
    }


def _absence_verdict(
    scope: list[str], ctx: dict[str, Any], raw: bytes
) -> dict[str, Any]:
    """Decide "no write under `scope` during the evaluated interval"."""
    admitted = _admit(raw, ctx)
    if "refused" in admitted:
        return admitted["refused"]
    pred = admitted["predicate"]
    observation = pred["observation"]

    # Per-claim binding. Coverage established for one interval cannot establish
    # completeness for another.
    if pred["intervalId"] != ctx["claim_ref"]:
        return _not_established(
            OBSERVATION_COVERAGE,
            f"the record covers interval {pred['intervalId']!r}, not the evaluated "
            f"claim {ctx['claim_ref']!r}",
        )
    # The property may not be wider than what was observed.
    uncovered = [p for p in scope if not any(_under(p, s) for s in pred["pathScope"])]
    if uncovered:
        return _not_established(
            OBSERVATION_COVERAGE,
            f"the property scope {uncovered} lies outside the observed pathScope "
            f"{pred['pathScope']}",
        )
    # Who observed. A record at the observed party's own vantage, or at a peer
    # layer it could route around, is not independent evidence in either
    # direction.
    if observation["vantage"] != "below-observed":
        return _not_established(
            OBSERVATION_VANTAGE,
            f"observation vantage is {observation['vantage']!r}; only a vantage the "
            "observed party cannot address is independent evidence",
        )
    # The signed interval identifier authenticates what the observer asserted,
    # but does not join that interval to the invocation under evaluation. The
    # expected prior commitment must come from trusted context independent of
    # this record (for example, an external pre-interval witness). These
    # synthetic cases stipulate that context; they do not prove its provenance.
    expected_commitment = ctx.get("anchored_commitment_digest")
    prior = observation.get("priorCommitment")
    actual_commitment = prior.get("commitmentDigest") if isinstance(prior, dict) else None
    if not expected_commitment or actual_commitment != expected_commitment:
        return _not_established(
            INVOCATION_BINDING,
            "the record's prior commitment is not independently bound to the "
            "evaluated invocation",
        )
    # Asymmetry: one observed write inside the property scope settles fail on
    # its own, with no completeness premise.
    witnesses = [
        w["path"] for w in pred["writes"] if any(_under(w["path"], s) for s in scope)
    ]
    if witnesses:
        return {
            "verdict": "fail",
            "unmet_obligation": None,
            "reason": f"write(s) observed inside the property scope: {witnesses}",
        }
    # A negative needs complete coverage of the property scope for the interval.
    # A gap the record names is a gap it did not watch.
    coverage = observation["coverage"]
    blind = (
        []
        if coverage["scopeComplete"]
        else [g for g in coverage["gaps"] if any(_overlaps(g, s) for s in scope)]
    )
    if blind:
        return _not_established(
            OBSERVATION_COVERAGE,
            f"the record names unobserved path(s) inside the property scope: {blind}",
        )
    capability = ctx.get("producer_capability")
    if capability is None:
        return _not_established(
            PRODUCER_CAPABILITY_COVERAGE,
            "no write visibility was established for the evaluated invocation",
        )
    if capability["claim_ref"] != ctx["claim_ref"]:
        return _not_established(
            PRODUCER_CAPABILITY_COVERAGE,
            "write visibility was established for a different invocation",
        )
    if any(
        not any(_under(p, visible) for visible in capability["visible_write_paths"])
        for p in scope
    ):
        return _not_established(
            PRODUCER_CAPABILITY_COVERAGE,
            "write visibility does not cover the evaluated path scope",
        )
    return {
        "verdict": "pass",
        "unmet_obligation": None,
        "reason": "no write observed inside the property scope, with write visibility "
        "and complete coverage for the interval from an independent vantage",
    }


def evaluate(checker_input: dict[str, Any]) -> dict[str, Any]:
    result = _evaluate(checker_input)
    prop = checker_input["property"]
    ctx = checker_input["context"]
    result["evaluation"] = {
        "property": {"name": prop["name"], "scope": list(prop["scope"])},
        "context": {
            "claim_ref": ctx["claim_ref"],
            "observer_public_key": ctx["observer_public_key"],
            "anchored_commitment_digest": ctx.get("anchored_commitment_digest"),
            "producer_capability": (
                {
                    "claim_ref": ctx["producer_capability"]["claim_ref"],
                    "visible_write_paths": list(
                        ctx["producer_capability"]["visible_write_paths"]
                    ),
                }
                if ctx.get("producer_capability") is not None
                else None
            ),
            "producer": ctx.get("producer"),
            "independence_evidence": (
                copy.deepcopy(ctx["independence_evidence"])
                if ctx.get("independence_evidence") is not None
                else None
            ),
        },
    }
    return result
