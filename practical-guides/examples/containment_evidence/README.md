# Containment evidence record — software-only sample

One tool call, recorded the way the agent-containment paper's §7.1 evidence contract asks for it, from a producer that has no hardware attestation. The file is `evidence-record-software-only.json`. It exists so the OCSF mapping in the practical guide has a concrete record to be checked against, including the explicit-absence cases that a schema can get wrong.

Scope: this sample records a software tool call. The record structure — decision before dispatch, a separate outcome entry, the observation states — is action-agnostic, but evidence for physical actuation, such as whether an actuator crossed a keep-out boundary, needs independently observed outcome fields and domain safety engineering outside this guide's scope.

The record is three sequenced entries — the enforcement decision, the accounting decision, the outcome — plus a signed checkpoint. The hash chain, the assurance-boundary statement digest and the checkpoint signature are real; `verify.py` recomputes all three.

## Every row of the evidence table, and where it is

| §7.1 row | Path in the record | Source |
| :---- | :---- | :---- |
| Principal and full delegation chain | `entries[0].principal` (`id`, `delegation_chain[]`, `correlation_key`) | real run |
| Actor identity and provenance | `entries[0].actor` (`actor_id`, `provenance`, `verification`) | real run |
| Subject identity and provenance | `entries[0].subject` | real run; `human_principal` is `not_established` |
| Policy version | `entries[0].policy.version` — a content digest | real run |
| Assurance-boundary statement | `entries[0].assurance_boundary` — the statement of covered and excluded paths at the decision, and its content digest | illustrative statement; the digest is real and recomputable |
| Tool-catalog version | `entries[0].tool_catalog.version` — a content digest | illustrative |
| Action or tool-call identifier | `entries[*].action_id` / `references.action_id` | illustrative |
| Request digest | `entries[0].request_digest` — keyed commitment, covered fields, canonicalization | illustrative |
| Enforcement decision and reason | `entries[0].decision` (`verdict`, `reason`, `enforcement_point`) | illustrative |
| Runtime identity or attestation reference | `entries[0].runtime` — `attestation.status: not-available` with a reason, plus the software identity | real run |
| Outcome | `entries[2].outcome`, referencing the decision by entry hash | illustrative |
| Integrity-protected sequence with trusted checkpoints | `entries[*].prev_hash` / `entry_hash`, `sequence.checkpoint` | real, recomputable |
| The accounting decision | `entries[1].decision` (`verdict`, `reason`), `entries[1].budget`, `entries[1].claim` | real budget state; illustrative claim and decision |

"Real run" values come from a run of an Apache-2.0 orchestrator on 2026-09-20 (run `20260920-165918`): the principal chain, the policy bundle digest, the build digest, the model, the worker's Ed25519 key. "Illustrative" values show the shape of rows that this producer does not journal yet, because its journal carries no tool-call events; they are not a production record and say so in the file's `$comment`. `producer.trust_record_profile` is the producer's own statement of the record profile it emits; the paper endorses no profile, and the guide cites none.

## The boundary statement records a claim

`entries[0].assurance_boundary` carries the statement of which paths the containment claim covered and which it excluded at the moment of decision, and the content digest of that statement, for the same reason the policy row carries a digest: the paths a claim covers can change while its name does not. It sits beside the policy version because the two answer different questions — the policy says what was allowed, the statement says on which paths that was enforced and which paths the claim leaves out.

It records claimed scope. It does not prove that enforcement covered every route: an excluded path is not thereby closed, and an included path is not thereby mediated. The sample shows the gap on purpose — the statement claims egress was refused at dispatch, and `entries[2].egress_observed` stays `not_established`, because no independent observer exists in this shape. The statement also records that no allow fallback is configured, so no path is excluded on that ground; a producer that runs an allow fallback records the excluded path here, per decision.

## The absence cases, deliberately

The contract's rule is that a determined absence must be distinguishable from one that was never established. The sample carries one of each kind so a mapping has to represent all of them:

| Case | Where | Value |
| :---- | :---- | :---- |
| Determined absence with a reason | `runtime.attestation` | `not-available` — no hardware attestation exists in this shape |
| Determined absence with a reason | `entries[1].budget.applicable` | `absent` — no budget was configured for the run |
| Determined absence with a reason | `sequence.checkpoint.collection_scope.omitted_before_recording` | `absent` — the decision is written before dispatch |
| Determined absence with a reason | `entries[0].assurance_boundary.statement.allow_fallback` | `absent` — no allow fallback is configured, so no path is excluded on that ground |
| Never established, with the missing premise | `subject.human_principal` | `not_established` — the operator session is outside the collection scope |
| Never established, with the missing premise | `entries[2].egress_observed` | `not_established` — no network observer exists in this shape |
| Never established, with the missing premise | `entries[1].budget.remaining` | `not_established` — undefined without an applicable budget |
| Not yet known | `entries[0].decision.outcome.status` | `pending` — resolved by a later entry that references this one |

## The ordering the contract relies on

The decision entry is index 0 and is written before the action is dispatched; the outcome is index 2 and references the decision's `entry_hash`. A reader who finds a decision with no outcome entry treats the outcome as unknown, and per §4 the accounting stays charged. The sample shows the resolved case; the unresolved case is the same record with `entries[2]` missing.

## Verifying it

```bash
pip install rfc8785 cryptography
python verify.py evidence-record-software-only.json
```

`verify.py` recomputes each `entry_hash` as SHA-256 over the RFC 8785 canonical form of the entry without its `entry_hash` member and checks every `prev_hash` link; checks that each entry's `index` is its position in the sequence and that the checkpoint's `index` and `expected_boundaries` name the entries actually present; recomputes the assurance-boundary statement digest from the statement; and verifies the checkpoint signature against the public key carried in the checkpoint. The checkpoint key was generated for this sample; a producer signs checkpoints with its runtime identity key.

The request commitment cannot be recomputed from the file: it is an HMAC whose key the operator holds, which is the point of that row for guessable arguments. What the file does state is what the commitment covers and how it was canonicalized, so two records can be compared or declared incomparable.

## For the OCSF mapping

Three places where the mapping will have to make a choice, listed so they are not discovered late:

- `runtime.attestation.status: not-available` needs a representation that is distinct from an omitted attestation object.
- `entries[1]` carries the claim check (`claim`: type, presenter, verification) next to the accounting decision (`decision`: a verdict in §4's vocabulary, allowed, refused or held, with a coded reason) and the budget state; the halves are separate objects in the sample and may map to different objects.
- `entries[2].egress_observed.status: not_established` is an observation status, not a network event; mapping it to a network activity class would assert an observation that was never made.
