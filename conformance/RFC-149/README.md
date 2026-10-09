# RFC-149 declaration-to-action cases on the Agent Registration Record

Step 2 of [RFC-149's proposed work](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/3a38845ea8330a71b338c693e00bb996faefe2a0/RFCs/RFC-149.md#proposed-work-and-review) ([#210](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/210)) reviews the field mapping in [ws4-odis#35](https://github.com/cosai-oasis/ws4-odis/pull/35) and its sample registration record. These cases test that record. Each one names a field of the record by JSON pointer and gives two pieces of evidence that differ in one field: one a verifier accepts and one it must refuse. Each side states what a relying party receives. Nothing here changes RFC-149, ODIS or the containment draft, and every case is `candidate` until the profile it tests is accepted.

The 2026-10-07 WS4 call made the registration record the single source of truth and deprecated a standalone Agent Manifest. An earlier version of this set was written against the Manifest text. The cases below are that set moved onto the record, with the Manifest-only cases dropped (listed at the end).

## What is pinned

| Input | Pin |
| --- | --- |
| RFC-149 scope | `3a38845e`, the head of #210 after the 2026-10-07 revision |
| Sample record | `record/sample-registration-record.json`, a byte copy of `RFCs/mappings/sample-registration-record.json` at ws4-odis `2b9718ad` (#35), sha256 `7cb8b127...b19a4` |
| Evidence and readers | `agent-evidence-vectors==0.17.5` (hash-pinned in `requirements.txt`) and `aee-verify` from the Go module at `v0.17.5` |

The evidence is read from the published package, not copied into this tree. Each pair pins the sha256 of both members, and where the corpus records which accepted member a rejected one was derived from, `run.py` checks that it is the accept side of the same pair.

## Pairs that run

| Pair | Record field | Relationship | Differs in | Accept gives | Reject gives |
| --- | --- | --- | --- | --- | --- |
| RR-01 | `/approved_software_refs/0/digest` | instance_to_software | one covered byte changed after signing | `pass` | `fail` |
| RR-02 | `.../governance/authorized_updaters` | signer authorization | signed by a key the relying party did not pin | `pass` | `fail` |
| RR-03 | `/approved_software_refs` | instance_to_software | the artifact for one required role never captured | `pass` | `not_established` / content_coverage |
| RR-04 | `.../tool_catalog/tool_servers` | instance_to_software | a named dependency the evidence does not cover | `pass` | `not_established` / dependency_coverage |
| RR-05 | `/approved_software_refs/5/digest_input` | instance_to_software | valid signature over a non-canonical encoding | `pass` | processing failure |
| RR-06 | `/approved_software_refs/5/locator` | instance_to_software | a pointer names a document other than the one hashed | `pass` | `fail` |
| RR-07 | `/provider_entitlements/<ledger>/allowed_actions` | decision to action | action changed, request digest left | `pass` | processing failure |
| RR-08 | `.../audit_commitment` | decision to effect | observed effect edited to none and re-signed with the real key | `pass` | processing failure |
| RR-09 | `.../canonicalization/canonical_profile` | integrity | serialized in declaration order, not RFC 8785 | `pass` | processing failure |
| RR-10 | `.../reference_values/required_assurance` | instance_to_software | authoritative claimed from the agent's own vantage | `pass` | processing failure |
| RR-11 | `.../audit_commitment/audit_chain_root` | evidence freshness | commitment made after the interval opened | `pass` | processing failure |
| RR-12 | `.../policy_bundle/enforcement_mode` | policy | enforcement value outside the closed set | `pass` | processing failure |
| RR-13 | `.../human_oversight` | oversight | oversight block with an undefined member | `pass` | processing failure |
| RR-14 | `.../reference_values` | missing evidence | not-evaluated with the unavailable input removed | `not_established` / standing_source | processing failure |
| RR-15 | `/provider_entitlements/<ledger>/egress_destinations` | decision to effect | a write outside the declared scope marked in scope | `pass` | processing failure |
| RR-16 | `.../tool_catalog/tools/0/schema_hash` | decision to action | authoritative claimed on arguments that cannot be bound | `not_established` / invocation_binding | processing failure |
| RR-17 | `.../reference_values/required_assurance/instance_to_software` | instance_to_software | substrate coverage claimed beside a vantage of self | `not_established` / observation_vantage | processing failure |

`...` is `/extensions/agentrust-composition-v0`, the profile extension in the sample. RR-01 to RR-06 read the [artifact-binding corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.17.5/vectors-artifact-binding) with `aee-verify`. RR-07 to RR-17 read the [agent audit record corpus](https://github.com/probityai/agent-evidence-vectors/tree/v0.17.5/vectors-agent-audit-record) with `auditrecord`. RR-13's accepted member carries the overseer's record digest, the join a human oversight declaration on the record needs.

## Questions the pairs put to the open items

- RR-02: a correctly signed binding from a signer the relying party does not accept. Whether that is `fail` or `not_established` depends on who may update a record (RFC-149, unresolved question 4).
- RR-05 and RR-09: the readers refuse evidence produced under an encoding other than the named one. The profile has to say whether a consumer sees that as `fail` or as a processing failure, and the sample's `null_handling: preserve` makes the choice explicit (ws4-odis#22).
- RR-12: `enforcement_mode` needs one closed vocabulary. The Agent Manifest and TRACE enums differ today (#35, Mapping 2).
- RR-10 and RR-17: `required_assurance` is appraised by the verifier per relationship. Evidence that labels itself is refused.

## Candidate cases without a fixture yet

| Case | Record field | Declaration | Evidence | Proposed result |
| --- | --- | --- | --- | --- |
| C-01 | `/provider_entitlements/*/allowed_actions` | action in the declared set | invocation of it | membership established; authorization and benign intent not established by membership |
| C-02 | same | action outside the declared set | invocation of it | a discrepancy requiring investigation, never a match |
| C-03 | `record_version`, `created_at` | record version first issued after the action | any action | `not_established`: no record version in force before the action |
| C-04 | §6.2 `registration_record_ref` | record available | runtime credential names no version, or another one | `not_established` / version binding |
| C-05 | `.../reference_values` | evidence required per relationship | no execution evidence for the action | `not_established` / execution evidence, never a match |
| C-06 | `.../reference_values/platform` | an attestation reference | attestation unavailable in this deployment shape | field present as not-available with its reason; `not_established` when availability cannot be established |
| C-07 | §6.2 `runtime_instance_id` | credential for instance X names the record | evidence from instance Y running the same composition | `not_established` for X: a matching digest does not bind the instance |
| C-08 | `/approved_software_refs/*/locator` | a locator by mutable tag with no digest | any action | processing failure for an ambiguous reference |
| C-09 | `record_version` (ws4-odis#16 rule 3) | credential names a superseded version | action after the supersession | accepted only while issuance evidence still satisfies the current version; otherwise `fail`, or `not_established` / freshness when status at action time is unknown |
| C-10 | `.../reference_values/launch_binding` | owner changes, `record_version` bumps, composition unchanged | launch measurement over the composition digest | `instance_to_software` still passes; a composition change breaks it |
| C-11 | `/permitted_delegation_modes`, §6.3 | delegation created at runtime | delegated action | judged against the §6.3 Delegation Record; `not_established` when it is missing |
| C-12 | `/policy_profile_ref` | digest in the URI fragment | `policy_bundle.hash` differs | `fail`: the two policy digests disagree |
| C-13 | `.../rag_corpus/poisoning_scan/subject_digest` | scan result bound to a subject | subject digest differs from `merkle_root` | the scan says nothing about the corpus in use: `not_established` |

C-10, C-12 and C-13 are new with the record: they test the composition-digest launch binding, the stopgap digest in `policy_profile_ref`, and the scan-to-subject binding the RFC scopes. A candidate moves to the pairs table when it has two fixtures that differ in one field.

## Dropped with the Manifest

- Manifest-to-ODIS join (old D2A-27): there is no second document to join. Its runtime half is C-07.
- Registration record and Manifest disagreeing on the tool set (old D2A-28): one source of truth leaves nothing to disagree.
- Four decision-to-effect cases (old D2A-11 to D2A-14: deny with and without an effect, a write attributed elsewhere, an unattributed write) judge an observation, not a field of the record. They remain in the section 7.4 cases the containment draft links.

## Running

```sh
cd conformance/RFC-149/declaration-to-action
python -m pip install --require-hashes -r requirements.txt
go install github.com/probityai/agent-evidence-vectors/cmd/aee-verify@v0.17.5
python run.py    # read-only; non-zero on any mismatch
```
