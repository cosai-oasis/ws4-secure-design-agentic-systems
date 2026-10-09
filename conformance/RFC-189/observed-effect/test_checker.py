"""Regressions for the checker and the harness. Run: python -m unittest test_checker"""

from __future__ import annotations

import copy
import json
import os
import unittest
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager, nullcontext
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from agent_evidence_vectors import observedeffect

import checker
import run

HERE = os.path.dirname(os.path.abspath(__file__))


def load(case_id: str) -> dict[str, Any]:
    with open(os.path.join(HERE, "cases", f"{case_id}.json"), encoding="utf-8") as fh:
        case: dict[str, Any] = json.load(fh)
    return case


class Harness(unittest.TestCase):
    def test_every_committed_case_matches(self) -> None:
        self.assertEqual(run.main(), 0)

    def test_expectation_never_reaches_the_checker(self) -> None:
        built = run.build_input(load("RFC189-OE-03-NE-NAMED-GAP"))
        self.assertNotIn("expected", json.dumps(sorted(built)))
        self.assertEqual(set(built), {"property", "evidence", "context"})

    def test_a_tampered_expectation_is_reported_not_repaired(self) -> None:
        case = load("RFC189-OE-03-NE-NAMED-GAP")
        got = run.outcome(run.build_input(case))
        case["expected"] = {"verdict": "pass", "unmet_obligation": None}
        self.assertNotEqual(got, case["expected"])

    def test_a_pinned_hash_mismatch_refuses(self) -> None:
        case = load("RFC189-OE-01-PASS")
        case["checker_input"]["evidence"]["observed_effect"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            run.build_input(case)

    def test_a_record_absent_from_the_pinned_release_refuses(self) -> None:
        case = load("RFC189-OE-01-PASS")
        case["checker_input"]["evidence"]["observed_effect"]["vector"] = (
            "v0000000000000000"
        )
        with self.assertRaises(FileNotFoundError):
            run.build_input(case)

    def test_a_verdict_without_its_evaluation_is_not_graded(self) -> None:
        inp = run.build_input(load("RFC189-OE-03-NE-NAMED-GAP"))
        detached = {
            "verdict": "not_established",
            "unmet_obligation": "observation_coverage",
            "evaluation": {},
        }
        with patch.object(checker, "evaluate", return_value=detached):
            with self.assertRaisesRegex(ValueError, "not bound"):
                run.outcome(inp)


class Checker(unittest.TestCase):
    def base(self) -> dict[str, Any]:
        return run.build_input(load("RFC189-OE-01-PASS"))

    def test_missing_claim_ref_is_an_input_error_not_a_verdict(self) -> None:
        inp = self.base()
        del inp["context"]["claim_ref"]
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_missing_observer_key_is_an_input_error_not_a_verdict(self) -> None:
        inp = self.base()
        del inp["context"]["observer_public_key"]
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_empty_property_scope_is_an_input_error(self) -> None:
        inp = self.base()
        inp["property"]["scope"] = []
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_a_record_signed_under_another_key_fails_the_vantage_claim(self) -> None:
        inp = self.base()
        inp["context"]["observer_public_key"] = (
            "763929ab5e25073572c6c63a261bc5b375a5b66f1cfe26cafe36885402d69632"
        )
        got = checker.evaluate(inp)
        # The observer's prior commitment is the member that carries the vantage
        # claim, and it is the first thing that fails to verify under the wrong key.
        self.assertEqual(got["verdict"], "not_established")
        self.assertEqual(got["unmet_obligation"], checker.OBSERVATION_VANTAGE)
        self.assertIn("commitment-signature-invalid", got["reason"])

    def test_unparseable_bytes_are_malformed_evidence(self) -> None:
        inp = self.base()
        inp["evidence"]["envelope"] = b"{not json"
        with self.assertRaises(checker.MalformedEvidence):
            checker.evaluate(inp)

    def test_an_open_result_always_names_an_obligation(self) -> None:
        for name in sorted(os.listdir(os.path.join(HERE, "cases"))):
            case = load(name.removesuffix(".json"))
            got = run.outcome(run.build_input(case))
            if got.get("verdict") == "not_established" or got.get("outcome") == "pending":
                self.assertTrue(got["unmet_obligation"], name)

    def test_an_unknown_action_outcome_stays_pending_after_the_window(self) -> None:
        inp = run.build_input(load("RFC189-OE-20-PENDING-RETRY-OUTCOME-AFTER-WINDOW"))
        got = checker.evaluate(inp)
        self.assertEqual(got["outcome"], "pending")
        self.assertNotIn("verdict", got)
        self.assertIn("not verified by the end of the window", got["reason"])

    def test_action_outcome_reads_the_absence_verdict_on_the_same_evidence(self) -> None:
        for case_id in case_ids():
            inp = run.build_input(load(case_id))
            if inp["property"]["name"] != checker.ACTION_OUTCOME:
                continue
            absence = copy.deepcopy(inp)
            absence["property"]["name"] = checker.NO_WRITE_IN_SCOPE
            verdict = checker.evaluate(absence)
            outcome = checker.evaluate(inp)
            want = {"pass": "absent", "fail": "present", "not_established": "pending"}
            with self.subTest(case=case_id):
                self.assertEqual(outcome["outcome"], want[verdict["verdict"]])
                self.assertEqual(outcome["unmet_obligation"], verdict["unmet_obligation"])

    def test_a_malformed_record_is_a_processing_failure_for_the_outcome_too(self) -> None:
        inp = run.build_input(load("RFC189-OE-06-MALFORMED-UNNAMED-GAP"))
        inp["property"]["name"] = checker.ACTION_OUTCOME
        with self.assertRaises(checker.MalformedEvidence):
            checker.evaluate(inp)

    def test_a_case_pinned_to_other_text_is_not_graded(self) -> None:
        case = load("RFC189-OE-01-PASS")
        case["against"] = dict(case["against"], commit="0" * 40)
        with self.assertRaisesRegex(ValueError, "pinned to section 7.4"):
            run.check_pin(case)
        case = load("RFC189-OE-01-PASS")
        case["status"] = "approved"
        with self.assertRaises(ValueError):
            run.check_pin(case)

    def test_the_gap_decides_only_the_claims_it_touches(self) -> None:
        wide = run.build_input(load("RFC189-OE-03-NE-NAMED-GAP"))
        narrow = copy.deepcopy(wide)
        narrow["property"]["scope"] = ["/srv/app/src/"]
        vendor = copy.deepcopy(wide)
        vendor["property"]["scope"] = ["/srv/app/vendor/lib/"]
        self.assertEqual(checker.evaluate(wide)["verdict"], "not_established")
        self.assertEqual(checker.evaluate(narrow)["verdict"], "pass")
        self.assertEqual(checker.evaluate(vendor)["verdict"], "not_established")

    def test_equal_verdicts_keep_distinct_evaluations(self) -> None:
        first_input = run.build_input(load("RFC189-OE-03-NE-NAMED-GAP"))
        second_input = copy.deepcopy(first_input)
        second_input["property"]["scope"] = ["/srv/app/vendor/"]
        third_input = copy.deepcopy(first_input)
        third_input["context"]["claim_ref"] = "another-interval"
        first = checker.evaluate(first_input)
        second = checker.evaluate(second_input)
        third = checker.evaluate(third_input)
        self.assertEqual(first["verdict"], second["verdict"])
        self.assertEqual(first["unmet_obligation"], second["unmet_obligation"])
        self.assertEqual(first["verdict"], third["verdict"])
        self.assertEqual(first["unmet_obligation"], third["unmet_obligation"])
        self.assertNotEqual(first["evaluation"], second["evaluation"])
        self.assertNotEqual(first["evaluation"], third["evaluation"])
        self.assertEqual(first["evaluation"]["property"]["scope"], ["/srv/app/"])
        self.assertEqual(
            first["evaluation"]["context"]["claim_ref"],
            first_input["context"]["claim_ref"],
        )
        first_input["property"]["scope"].append("/elsewhere/")
        self.assertEqual(first["evaluation"]["property"]["scope"], ["/srv/app/"])

    def test_no_write_visibility_cannot_establish_absence(self) -> None:
        inp = self.base()
        del inp["context"]["producer_capability"]
        got = checker.evaluate(inp)
        self.assertEqual(got["verdict"], "not_established")
        self.assertEqual(
            got["unmet_obligation"], checker.PRODUCER_CAPABILITY_COVERAGE
        )

    def test_narrower_write_visibility_cannot_cover_the_claim(self) -> None:
        inp = self.base()
        inp["context"]["producer_capability"]["visible_write_paths"] = [
            "/srv/app/src/"
        ]
        got = checker.evaluate(inp)
        self.assertEqual(got["verdict"], "not_established")
        self.assertEqual(
            got["unmet_obligation"], checker.PRODUCER_CAPABILITY_COVERAGE
        )

    def test_invalid_write_visibility_is_a_processing_error(self) -> None:
        inp = self.base()
        inp["context"]["producer_capability"]["visible_write_paths"] = "*"
        with self.assertRaisesRegex(
            checker.CandidateInputError, "visible_write_paths must be a list"
        ):
            checker.evaluate(inp)

    def test_observed_write_can_fail_without_full_visibility(self) -> None:
        inp = run.build_input(load("RFC189-OE-05-FAIL-WITNESS-DESPITE-GAP"))
        del inp["context"]["producer_capability"]
        self.assertEqual(checker.evaluate(inp)["verdict"], "fail")

    def test_result_keeps_a_copy_of_capability_context(self) -> None:
        inp = self.base()
        got = checker.evaluate(inp)
        inp["context"]["producer_capability"]["visible_write_paths"].append(
            "/other/"
        )
        self.assertEqual(
            got["evaluation"]["context"]["producer_capability"][
                "visible_write_paths"
            ],
            ["/srv/app/"],
        )


def case_ids() -> list[str]:
    return sorted(
        n.removesuffix(".json")
        for n in os.listdir(os.path.join(HERE, "cases"))
        if n.endswith(".json")
    )


@contextmanager
def _reference_verifier_reads(
    old_verdict: str, code: str, new_verdict: str, new_code: str
) -> Iterator[None]:
    """Re-read one refusal of the reference verifier as another verdict."""
    real = observedeffect.verify

    def verify(raw: bytes, policy: Any) -> Any:
        report = real(raw, policy)
        if report.verdict == old_verdict and report.codes[:1] == [code]:
            return SimpleNamespace(verdict=new_verdict, codes=[new_code])
        return report

    with patch.object(observedeffect, "verify", verify):
        yield


def _without_stipulated_commitment(inp: dict[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(inp)
    changed["context"]["anchored_commitment_digest"] = None
    return changed


def _unchanged(inp: dict[str, Any]) -> dict[str, Any]:
    return inp


# Each open item of section 7.4, settled the other way. A case depends on an
# open item exactly when its graded outcome changes under that resolution.
# - gap_naming: incomplete coverage that locates no gap is a well-formed
#   unknown coverage state, so the claim is not_established, not malformed.
# - claim_binding: a checker that requires provenance evidence for the prior
#   commitment, which these fixtures only stipulate, at the point where binding
#   is checked now.
# - observation_vantage: a claim of independent observation from the observed
#   party's own vantage is reported as a processing failure of its own rather
#   than graded not_established.
OPEN_ITEMS: dict[
    str,
    tuple[
        Callable[[], AbstractContextManager[Any]],
        Callable[[dict[str, Any]], dict[str, Any]],
    ],
] = {
    "gap_naming": (
        lambda: _reference_verifier_reads(
            "malformed",
            "coverage-incomplete-without-gaps",
            "invalid",
            "authoritative-coverage-incomplete",
        ),
        _unchanged,
    ),
    "claim_binding": (nullcontext, _without_stipulated_commitment),
    "observation_vantage": (
        lambda: _reference_verifier_reads(
            "invalid",
            "authoritative-vantage-not-independent",
            "malformed",
            "authoritative-vantage-not-independent",
        ),
        _unchanged,
    ),
}


def cases_changed_by(item: str) -> set[str]:
    resolve, rewrite = OPEN_ITEMS[item]
    changed = set()
    for case_id in case_ids():
        inp = run.build_input(load(case_id))
        before = run.outcome(inp)
        with resolve():
            after = run.outcome(rewrite(inp))
        if after != before:
            changed.add(case_id)
    return changed


class ObserverIndependence(unittest.TestCase):
    def base(self) -> dict[str, Any]:
        return run.build_input(load("RFC189-IND-01-PASS-ATTESTED-IDENTITY"))

    def test_a_missing_producer_is_an_input_error_not_a_verdict(self) -> None:
        inp = self.base()
        del inp["context"]["producer"]
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_an_absent_evidence_object_is_an_input_error(self) -> None:
        inp = self.base()
        inp["context"]["independence_evidence"] = None
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_an_unknown_condition_is_an_input_error(self) -> None:
        inp = self.base()
        inp["context"]["independence_evidence"]["measured_state"] = {}
        with self.assertRaises(checker.CandidateInputError):
            checker.evaluate(inp)

    def test_each_condition_fails_alone_on_producer_control(self) -> None:
        for name, obligation in checker.INDEPENDENCE_CONDITIONS:
            for field in ("controlled_by", "established_by"):
                inp = self.base()
                inp["context"]["independence_evidence"][name][field] = inp["context"][
                    "producer"
                ]
                with self.subTest(condition=name, field=field):
                    got = checker.evaluate(inp)
                    self.assertEqual(
                        (got["verdict"], got["unmet_obligation"]),
                        ("not_established", obligation),
                    )

    def test_each_condition_fails_alone_as_a_declaration(self) -> None:
        for name, obligation in checker.INDEPENDENCE_CONDITIONS:
            inp = self.base()
            del inp["context"]["independence_evidence"][name]["evidence_ref"]
            with self.subTest(condition=name):
                got = checker.evaluate(inp)
                self.assertEqual(got["unmet_obligation"], obligation)


class OpenItemDependencies(unittest.TestCase):
    """A case's declared open-item dependencies are measured, not authored."""

    def test_declared_dependencies_match_the_measured_ones(self) -> None:
        for item in OPEN_ITEMS:
            declared = {
                case_id
                for case_id in case_ids()
                if item in load(case_id)["open_item_dependencies"]
            }
            with self.subTest(open_item=item):
                self.assertEqual(cases_changed_by(item), declared)

    def test_every_declared_item_is_an_open_item_of_the_text(self) -> None:
        for case_id in case_ids():
            for item in load(case_id)["open_item_dependencies"]:
                self.assertIn(item, OPEN_ITEMS, case_id)


if __name__ == "__main__":
    unittest.main()
