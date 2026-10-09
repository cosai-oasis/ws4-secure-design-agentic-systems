# Section 7.4 candidate cases: what a verifier may conclude when evidence is absent

These are executable cases for [section 7.4 of the containment paper](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/84604125869469926968acdf433501f87d1d1665/whitepapers/agent-containment.md#74-evidence-sufficiency-for-absence-claims), merged into `feat/containment` at `84604125` through [#219](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219), and [issue #189](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189). Every case file carries `"status": "candidate"` and an `against` block naming that file, section and commit; `run.py` refuses a case pinned to any other text. The cases stay non-normative until the paper is approved, as section 7.4 says. When an amendment changes 7.4, the pin, the clause table below and the expectations move together in one commit.

Case leads, named in section 7.4: @aeoess and @astrogilda ([proposal](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827010158), [Imran's reply](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827685232)).

## The rule, clause by clause

C1-C6 are the clauses of section 7.4 as merged at `84604125`, worded as there. C7 and C8 remain open proposals. Section 7.4 names them as open items: C7 is gap naming, C8 is the observation vantage claim. Its third open item, the independent witness for the prior commitment, is the C5 binding question below. The case files cite these IDs.

| ID | Clause | Source |
| --- | --- | --- |
| C1 | Use `not_established` as defined in section 7: the observation could not be established, with the missing premise recorded. After the applicable verification has run, an absence claim that the admissible observations justify neither passing nor failing remains `not_established`. Name the unresolved proof obligation and bind the result to the property, invocation, interval and scope checked. This does not redefine the observation states: an unknown action outcome remains `pending`, including when the reporting window ends. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104) |
| C2 | Malformed input, an unsupported verification path, parser failure, and internal verifier error are processing failures. They are never `not_established`; otherwise a broken verifier becomes conformant by returning the third value. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5671639059) |
| C3 | Outcomes are asymmetric. An admissible observation of the prohibited event within the evaluated scope can settle `fail` without complete coverage. A self-reported write is not an admission on its own: without independent observation it stays `not_established`, even if the record is signed or reports a write. No observed event without established coverage is also `not_established`. Admissibility for the property is distinct from structural validity of the record. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5672256489), [Levaj2000](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5672817487), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219#issuecomment-5904200879) |
| C4 | A claim that no event occurred over a scope passes only when the producer could see the relevant field for the invocation and the observation covers the evaluated interval. A present but empty field needs the same premises as a missing field. If either premise is unestablished or bound to another scope, return `not_established` with the missing obligation. Coverage can be established by another verifier surface. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5702083982), [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5739339967) |
| C5 | Coverage must be bound to the claim or invocation it covers. A complete record for one call cannot establish completeness for another. Matching identifiers alone do not prove that binding; an authenticated identifier inside the observation still needs an independently established join to the evaluated invocation. | [chernistry](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5710166163), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5745298467) |
| C6 | Checker input and harness expectation stay structurally separate. The expected verdict and obligation are authored, so they are never visible to the inference that derives the result. | [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104), [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5638613689) |
| C7 (open) | An observation that declares incomplete coverage without locating its gap is malformed; explicit unknown coverage can remain `not_established`. | [astrogilda](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827010158) |
| C8 (open) | A claim of independent observation made from the observed party's own vantage is refused. It supports neither `pass` nor `fail`. | proposed here, case 08 |

The containment paper's section 7 states the same boundary for evidence records: missing visibility or incomplete observation is `not_established` with its missing premise, and malformed records stay visible as processing failures. These cases exercise both texts.

## Two case sets, one rule

| Directory | Evidence | Obligations it exercises |
| --- | --- | --- |
| [aps-conformance-suite cosai-ws4-189-evidence-sufficiency](https://github.com/Agent-Authority-Conformance/aps-conformance-suite/tree/main/interop/cosai-ws4-189-evidence-sufficiency) | producer audit records (SINK-01 to SINK-03) | `producer_capability_coverage`, `observation_coverage` |
| [observed-effect/](observed-effect/) | signed Observed Effect records from [agent-evidence-vectors](https://github.com/probityai/agent-evidence-vectors/tree/main/vectors-observed-effect) | `observation_coverage`, `observation_vantage`, `invocation_binding` |

An Observed Effect record states what an observer saw change during one interval. Its declared vantage may be independent or self-reported; the authoritative claim requires an independent vantage. It carries:

- the path scope it watched
- the gaps it did not watch
- each write it saw

The reference verifier in the [agent-evidence-vectors](https://pypi.org/project/agent-evidence-vectors/) package checks the record's signatures, the observer's prior commitment and the consistency of its coverage declaration. The checker then decides what the proposed rule permits it to conclude. A `valid` self-reported record still lacks independent observation. Case 10 returns `not_established` under C3; its reported write does not settle `fail` on its own.

`observation_vantage` is the [agent-evidence-vocabulary](https://github.com/probityai/agent-evidence-vocabulary/blob/main/vocabulary.yaml) term for who observed: whether every input a claim depends on came from a vantage the observed party could neither forge nor suppress, such as a network boundary, syscall supervision or a hypervisor's read of guest state. A record the observed party could have written or suppressed is not independent evidence of what it asserts. Case 08 is that record.

## Cases

| Case | Record | Expected under 7.4 at `84604125` | Clauses |
| --- | --- | --- | --- |
| 01 | read-only interval, complete coverage | `pass` | C4 |
| 02 | two writes observed in scope | `fail` | C3 |
| 03 | no write seen, a named gap inside the scope | `not_established` / `observation_coverage` | C1, C4 |
| 04 | record 03, claim narrowed to a path the gap does not touch | `pass` | C4, C5 |
| 05 | a named gap, and a write observed in scope anyway | `fail` | C3 |
| 06 | incomplete coverage, no gap named | processing failure, `coverage-incomplete-without-gaps` | C2, C7 (open) |
| 07 | complete coverage claimed, gap named in scope | processing failure, `coverage-self-contradictory` | C2 |
| 08 | the observed party's own record claiming independence | `not_established` / `observation_vantage` | C1, C8 (open) |
| 09 | record 03 claiming independence over its own gap | `not_established` / `observation_coverage` | C1, C4 |
| 10 | a valid self-reported record that reports writes | `not_established` / `observation_vantage` | C1, C3 |
| 11 | record 01 offered for a different interval | `not_established` / `observation_coverage` | C5 |
| 12 | record 01 asked about a wider scope than it watched | `not_established` / `observation_coverage` | C4 |
| 13 | a property the checker does not implement | processing failure, `UnsupportedVerification` | C2 |
| 14 | matching interval IDs, but the record's prior commitment differs from the one expected for this invocation | `not_established` / `invocation_binding` | C5 |
| 15 | matching interval IDs, but no expected commitment independently anchored for this invocation | `not_established` / `invocation_binding` | C5 |
| 16 | complete observation, but write visibility declared for another invocation | `not_established` / `producer_capability_coverage` | C4, C5 |
| 17 | complete observation, but no write visibility premise | `not_established` / `producer_capability_coverage` | C4 |
| 18 | complete observation, but write visibility covers a narrower path than the claim | `not_established` / `producer_capability_coverage` | C4 |
| 19 | a retried write, the interval sealed while blind where the write would land | `not_established` / `observation_coverage` | C1, C4 |
| 20 | record 19, asked whether the retried write landed | outcome `pending` / `observation_coverage` | C1 |
| 21 | a retry with one write observed below the agent | outcome `present` | C3 |
| 22 | record 19's interval claiming the authoritative tier over its blind spot | outcome `pending` / `observation_coverage` | C1, C4 |
| 23 | case 10's self-reported write, asked whether the action wrote | outcome `pending` / `observation_vantage` | C1, C3 |
| 24 | case 01's read-only interval, asked whether the action wrote | outcome `absent` | C4 |

Cases 03, 04 and 05 are the reason naming a gap matters: in all three the checker reads valid records that name /srv/app/vendor/ as unobserved, and it reaches three different verdicts. The same record cannot support "nothing changed under /srv/app/", yet it fully supports "nothing changed under /srv/app/src/", and a write it did see still settles `fail`.

An absence claim needs both observation coverage and write visibility for the same invocation and path scope. The Observed Effect checker takes write visibility from trusted evaluation context, not from the record. Cases 16 and 17 test a mismatched or missing premise. The producer audit cases SINK-01 to SINK-03 test declared field visibility at its source; these fixtures assume that an independent surface established the context and do not prove its provenance.

Cases 11, 14 and 15 exercise three necessary binding checks. The observer's signature authenticates the interval identifier and its prior commitment; the observer public key is selected out of band. The checker compares the signed `intervalId` with the context's `claim_ref`, then compares the signed prior `commitmentDigest` with `context.anchored_commitment_digest`. Case 14 keeps the identifiers equal but supplies the commitment for a different invocation, so matching strings cannot import its coverage. Case 15 omits an external commitment altogether; it also returns `not_established` / `invocation_binding` rather than passing or failing.

The synthetic fixtures **stipulate** that `anchored_commitment_digest` and `producer_capability` were established for the evaluated invocation outside the Observed Effect record. They test how the checker uses those premises, including mismatches, but do not prove that a real controller witnessed the commitment before an invocation, retained it independently, or established write visibility. A real deployment must establish that provenance at a separate verifier surface. Copying the values from the presented record does not satisfy C4 or C5.

The checker returns the evaluated property, path scope, claim reference, observer key, expected prior commitment and producer capability with each result. The claim reference is the interval identifier, so the binding names the property, invocation, interval and scope that C1 requires. The harness checks that binding before it grades the verdict and unmet obligation. These values identify the evaluation; they do not establish external provenance.

## Action outcomes stay `pending`

C1 keeps an unknown action outcome `pending` when the reporting window ends. Cases 19 to 24 test that sentence with the lost-response retry records: a tool completes a write, its response is lost, and the agent retries. The `action_outcome` property reads the same evidence as `no_write_in_scope` in section 7's observation states. An observed write is `present`, an established absence is `absent`, and everything else is `pending` with its unmet obligation. In cases 20 and 22 the interval is sealed, so the window has ended, and the outcome still reads `pending`; a checker that turns it into `not_established` fails both. Case 23 is C3 applied to the outcome: a self-reported write does not make the outcome `present`. A refused or malformed record stays a processing failure on this axis too.

## The three open items, and the cases that depend on them

Section 7.4 names three open items. Each case file lists the ones its expected result depends on in `open_item_dependencies`, and the list is measured rather than written by hand: `test_checker.OpenItemDependencies` settles each item the other way, reruns every case, and fails unless the cases whose outcome changes are exactly the cases that declare the dependency.

| Open item | Settled the other way, for the measurement | Cases whose result changes |
| --- | --- | --- |
| Gap naming | incomplete coverage that locates no gap is a well-formed unknown coverage state, so the claim is `not_established` | 06 |
| Claim binding | the checker requires provenance evidence for the prior commitment, which these fixtures only stipulate | 01, 02, 03, 04, 05, 16, 17, 18, 19, 20, 21, 24 |
| Observation vantage | a claim of independent observation from the observed party's own vantage is a processing failure of its own | 08 |

Case 10 depends on none of them: C3 settles it. Cases 22 and 23 depend on none either, because their records are refused or self-reported before any binding question arises. The claim-binding row is the dependency @aeoess measured on [#219](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219#issuecomment-5937888670) for cases 01 to 05 and 16 to 18, now extended to the new cases and held by a test.

## Open questions for the rule text

- C5 binding: Which independent witness anchors the expected prior commitment to the evaluated invocation, before that invocation, and how is its provenance checked? Case 14 tests a mismatch with matching interval IDs; the synthetic context still assumes the witness rather than proving it.

- O2: A record the reference verifier refuses as `invalid` (coherent, but its own rules reject its claim) is graded `not_established` with the obligation its refusal names (cases 08, 09). Should a refused claim of independence also be reported as its own finding?

## Running

```sh
cd conformance/RFC-189/observed-effect
python -m pip install --require-hashes -r requirements.txt
agent-evidence-vectors --corpus vectors-observed-effect   # the pinned corpus behaves as its manifest declares
python run.py                      # grades every case, read-only, non-zero on any mismatch
python -m unittest test_checker    # harness and checker regressions
```

`run.py` resolves each record by its identifier from the installed corpus, checks it against the SHA-256 digest the case pins, and passes the checker only the `checker_input`. It never writes. Every record comes from the published release that `requirements.txt` pins by hash; nothing is copied into this directory.
