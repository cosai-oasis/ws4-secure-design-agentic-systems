"""Regressions for run.py, the harness around agent-evidence-verify.

The verifier's own behaviour on these cases is tested where it is built; these
tests hold the harness to its three duties: refuse a case pinned to other text,
never let the expectation reach the verifier, and read the verifier's answer
back in the case's terms without inventing one.
"""

from __future__ import annotations

import copy
import json
import os
import unittest
from unittest import mock

from agent_evidence_verify.common import CaseError

import run

CASE_DIR = os.path.join(run.HERE, "cases")


def load(stem: str) -> dict:
    with open(os.path.join(CASE_DIR, f"{stem}.json"), encoding="utf-8") as fh:
        return json.load(fh)


class Pins(unittest.TestCase):
    def test_every_case_is_pinned_to_the_current_text(self):
        for name in sorted(os.listdir(CASE_DIR)):
            with self.subTest(name=name):
                run.check_pin(load(name[:-5]))

    def test_a_case_pinned_to_other_text_is_refused(self):
        case = load("RFC189-OE-01-PASS")
        case["against"] = dict(case["against"], text_sha256="0" * 64)
        with self.assertRaises(ValueError):
            run.check_pin(case)

    def test_a_moved_section_is_reported(self):
        self.assertIsNone(run.text_problem(run.AGAINST["text_sha256"]))
        self.assertIn("hashes to", run.text_problem("0" * 64))


class Separation(unittest.TestCase):
    def test_the_expectation_never_reaches_the_verifier(self):
        case = load("RFC189-OE-02-FAIL-WITNESS")
        given = run.build_input(case)
        seen = json.dumps(given["assessment"], sort_keys=True)
        self.assertNotIn("expected", seen)
        self.assertNotIn(json.dumps(case["expected"], sort_keys=True), seen)
        self.assertEqual(given["assessment"]["claim_type"], run.CLAIM_TYPE)

    def test_a_record_that_misses_its_pin_is_refused(self):
        case = copy.deepcopy(load("RFC189-OE-01-PASS"))
        case["checker_input"]["evidence"]["observed_effect"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            run.build_input(case)


class Reading(unittest.TestCase):
    def setUp(self):
        self.given = run.build_input(load("RFC189-OE-01-PASS"))

    def _answer(self, result=None, error=None):
        def fake(case, policy, root):
            if error is not None:
                raise error
            return result

        with mock.patch.object(run, "adjudicate", fake):
            return run.outcome(self.given)

    def _result(self, decision, **check):
        scope = {"property": self.given["assessment"]["property"]}
        scope.update({k: self.given["assessment"].get(k) for k in ("claim_ref", *run.CONTEXT_KEYS)})
        return {"decision": decision, "scope": scope, "checks": [check]}

    def test_a_verdict_is_read_with_its_obligation(self):
        got = self._answer(self._result(
            "not_established", verdict="not_established", unmet_obligation="observation_coverage"))
        self.assertEqual(got, {"verdict": "not_established", "unmet_obligation": "observation_coverage"})

    def test_an_outcome_is_read_on_its_own_axis(self):
        got = self._answer(self._result("contradicted", outcome="present", unmet_obligation=None))
        self.assertEqual(got, {"outcome": "present", "unmet_obligation": None})

    def test_a_decision_that_does_not_follow_from_the_verdict_is_refused(self):
        with self.assertRaises(ValueError):
            self._answer(self._result("supported", verdict="fail", unmet_obligation=None))

    def test_a_result_bound_to_another_claim_is_refused(self):
        result = self._result("supported", verdict="pass", unmet_obligation=None)
        result["scope"]["claim_ref"] = "another-interval"
        with self.assertRaises(ValueError):
            self._answer(result)

    def test_a_malformed_record_is_a_processing_failure_with_its_codes(self):
        got = self._answer(error=CaseError("malformed_record: b-code,a-code"))
        self.assertEqual(got, {"verdict": None, "processing_failure": "MalformedEvidence",
                               "codes": ["a-code", "b-code"]})

    def test_an_unsupported_property_is_a_processing_failure(self):
        got = self._answer(error=CaseError("unsupported_property: 'x' is not implemented"))
        self.assertEqual(got, {"verdict": None, "processing_failure": "UnsupportedVerification"})

    def test_any_other_refusal_is_an_error_of_the_run_never_a_verdict(self):
        with self.assertRaises(ValueError):
            self._answer(error=CaseError("assessment.property: expected an object"))


if __name__ == "__main__":
    unittest.main()
