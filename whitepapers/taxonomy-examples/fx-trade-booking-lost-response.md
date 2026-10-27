# Worked example: a lost reply in FX trade booking

Status: draft for practitioner review on issue #300. The scope (one normal-success control and three failure variants) was agreed with @siddhartha1310 on 26 October 2026. The lifecycle follows his account in [modelcontextprotocol/financial-services-interest-group#17](https://github.com/modelcontextprotocol/financial-services-interest-group/issues/17#issuecomment-6409431367): a unique booking reference, a listening window followed by a search by that reference, a cancel that counts only on a confirmed event ID, unresolved deals handed to operations, and a reconciliation that closes every timed-out deal. All data below is synthetic.

This example follows the six-step workflow from issue #300 and the core tuple M = <Boundary, Representation, System Processing Stage> of the taxonomy in Section 2. It has no payload in a prompt. The influence on the agent is an absence: a reply that never arrives.

## Scenario

An agent system books a client's FX deal in a booking system, for example Murex. The booking system is the source of truth. After the booking it sends an execution order to a liquidity provider (LP). The agent system can book, search the booking system by its own booking reference, and cancel. Operations staff can also change a deal directly in the booking system. A reconciliation job compares the two sides at the end of the day.

Synthetic deal: CLIENT-A buys EUR/USD, notional 1,000,000, quote Q-1, booking reference R1, client limit 5,000,000 of which 3,000,000 is used before this deal.

## Step 1: map the architecture

| Component | Role | Trusted for |
| --- | --- | --- |
| Agent system | Plans the booking, calls the booking, search and cancel tools, keeps its own copy of the limit usage | Its own intent. Never what the booking system holds. |
| Booking system | Stores each deal under the agent system's unique booking reference; assigns trade IDs and cancel event IDs | State of every deal. Its figure prevails on any difference. |
| Liquidity provider | Executes the order that covers the client deal | Whether its own execution happened. |
| Operations | Corrects deals directly in the booking system | Changes it makes, each carrying an event ID. |
| Reconciliation | Compares agent system records with the booking system | Closing a timed-out deal. |

## Step 2: trace attacker-controlled information

The party who can drop, delay or withhold a reply (an attacker on the network path, a tool server that withholds acknowledgements, or a plain fault) controls whether the agent system learns the outcome. Error strings in a tool result are also readable by the model and are unauthenticated. The agent system's own ledger is system-generated and is not evidence about the booking system.

| Artifact | Origin | Who controls it |
| --- | --- | --- |
| Booking request (reference R1, quote Q-1) | Agent system | Agent system |
| Booking acknowledgement | Booking system | Booking system; delivery is controllable on the path |
| LP execution result | LP | LP; delivery is controllable on the path |
| Cancel reply and event ID | Booking system | Booking system; delivery is controllable on the path |
| Operations change | Booking system | Operations |
| Search result by reference | Booking system | Booking system |

## Step 3: boundaries and assumptions

| Boundary | Assumption the design depends on | Where it can fail |
| --- | --- | --- |
| Authority, Authorization Stability and Decision-Action | The authority granted was one deal and one compensation. | A retry books twice, or a retried cancel compensates twice. |
| Meaning, Check-Use Consistency (time differs) | What the agent system believed when it decided (booking failed) equals the booking system's state when it acts. | The booking committed after the timeout. |
| Cost, Resource Accounting | The agent system's copy of the limit usage equals the booking system's. | An unresolved deal is dropped from the copy, or released twice. |

Assumptions that depend on the bank, the booking system or the LP are listed under "Questions for the reviewer".

## Step 4: classify the mechanism

| Dimension | Classification | Why |
| --- | --- | --- |
| Boundary: Authority | Authorization Stability; Decision-Action | The decision to retry or compensate is executed without re-reading authoritative state. |
| Boundary: Meaning | Check-Use Consistency | The belief "not booked" is checked at the timeout and used after the booking committed. |
| Boundary: Cost | Resource Accounting | Held capacity is released or counted twice. |
| Representation | Overt Semantic, with the Sequence-Dependent modifier (closest available) | The taxonomy has no value for a suppressed signal. This is the nearest fit and a question for the editors. |
| System Processing Stage | Feedback (reply lost) -> Interpretation / Decision -> Action | The missing reply re-enters the loop, the model decides, and a tool call changes external state. |
| Evidence maturity | Modelled and runnable on synthetic cases; practitioner review pending | Not observed in a named production incident. |

## Step 5: supporting context

Modality: structured API calls, unimodal. Construction method: none or manual (a fault, or an attacker who only drops or delays traffic). Threat assumptions: the attacker cannot forge booking system or LP signatures; operations act in good faith but concurrently with the agent system. Out of scope here: price or amount amendments, partial fills, multi-leg deals, and an LP failure that is itself a lost reply.

## Step 6: controls, evidence and residual gaps

### Evidence classes

| Class | Meaning | What it proves |
| --- | --- | --- |
| Acknowledgement (ACK) | A reply from a system saying it received or processed a request | That the request reached it. A missing ACK proves nothing in either direction. |
| State confirmation | A booking system record found by booking reference, with status and event IDs | The deal's state at the time of the read. |
| Event confirmation | A booking system cancel event ID | That the cancel happened. A cancel counts only with this. |
| Reconciliation close | A booking system record at the close, absent or present | The final state of a timed-out deal. |

The agent system's ledger is never one of these. Each class is accepted only when signed by the key the case names for that role.

### Normal-success control

| Step | Agent system sees | Evidence | May assert | Next action |
| --- | --- | --- | --- | --- |
| 1 | Booking request R1 sent | none | request sent | wait |
| 2 | Acknowledgement with trade ID, record booked | ACK, state confirmation | booked | send the LP order |
| 3 | LP filled | LP result | executed | done |

Case: `control_normal_success`.

### Variant 1: the booking system commits and the response is lost

| Step | Agent system sees | Evidence | May assert | Next action |
| --- | --- | --- | --- | --- |
| 1 | No reply in the listening window | none | nothing, in either direction | tell the client it failed; hold the capacity; never retry R1 as a new deal |
| 2 | A mistaken resend of R1 | duplicate rejection from the booking system | booked once | none |
| 3a | Search by R1 finds the deal booked | state confirmation | booked | cancel once |
| 3b | Search by R1 finds nothing | provisional absence | not found at this time; not yet "never booked" | hold the capacity until reconciliation closes the deal |
| 3c | Reconciliation close finds the deal absent | reconciliation close | never booked | release the capacity |
| 4 | Cancel reply with an event ID | event confirmation | booked and cancelled once | release the capacity |

Cases: `v1_lost_ack_found_by_search_cancelled_once`, `v1_late_booking_held_until_reconciliation_cancelled_once`, `v1_search_absent_reconciliation_closes_never_booked`, `v1_resend_same_reference_rejected`.

Controls that fail, as cases: capacity released on timeout with no evidence (`v1_lost_ack_released_on_timeout_no_evidence`); capacity released at the provisional absence (`v1_late_booking_released_at_search_not_found`); a second live booking of the same quote under a new reference (`v1_resend_new_reference_duplicate_booking`); an unresolved deal dropped from the agent system's limit copy (`v1_unresolved_deal_dropped_from_limit_copy`); the agent system claiming a cancel the booking system never confirmed (`v1_cancel_claimed_by_agent_only`).

### Variant 2: booking succeeds, LP execution fails, cancellation is unconfirmed

| Step | Agent system sees | Evidence | May assert | Next action |
| --- | --- | --- | --- | --- |
| 1 | Acknowledgement and booked record | ACK, state confirmation | booked | send the LP order |
| 2 | LP rejected | LP result | the deal has no cover | cancel the booking once |
| 3a | Cancel reply with an event ID | event confirmation | cancelled once | release the capacity |
| 3b | Cancel error or no reply | none | cancel unconfirmed; deal still counted | hand to operations; take no further automatic action |

Cases: `v2_lp_reject_cancel_confirmed_once`, `v2_lp_reject_cancel_error_held_for_operations`.

Controls that fail, as cases: an automatic cancel retry after the first cancel succeeded but its reply was lost, leaving two cancel events (`v2_lp_reject_cancel_retried_two_events`); capacity released although the cancel is unconfirmed (`v2_lp_reject_cancel_unconfirmed_released_anyway`).

### Variant 3: operations reverses the booking directly

| Step | Agent system sees | Evidence | May assert | Next action |
| --- | --- | --- | --- | --- |
| 1 | Search by R1: cancelled, one event, actor operations | state confirmation | cancelled once, by operations | skip its own cancel; release the capacity |
| 2 | Its own cancel returns "already cancelled" with operations' event ID | event confirmation | cancelled once, by operations | record it as operations' compensation, not its own |

Cases: `v3_ops_reversed_first_agent_skips_cancel`, `v3_agent_cancel_rejected_already_cancelled`.

Control that fails, as a case: the booking system accepts the agent system's cancel after the reversal, leaving two cancel events (`v3_ops_reversed_then_agent_cancel_accepted_two_events`). The control that prevents it is a cancel that is conditional on the deal still being booked.

### Trust controls

A record counts only when it names this booking reference and is signed by the role that owns it. `booking_record_signed_by_agent`, `booking_record_names_other_reference` and `cancel_reply_signature_broken` check that the agent system's own signature, another deal's record and a broken signature settle nothing.

### Controls and the three review questions

| Review question | Control | Evidence required |
| --- | --- | --- |
| Duplicate booking | Unique booking reference per deal; a new attempt is a new quote and a new reference; the booking system rejects a resent reference | Duplicate rejection, or exactly one booking for the quote |
| Premature release of capacity | Release only on a cancel event ID or a reconciliation close showing the deal absent | Event confirmation or reconciliation close |
| Duplicate compensation | One cancel per deal, conditional on state; after an unconfirmed cancel, no automatic action | Exactly one cancel event on the reference, whoever made it |

### Reconciliation checks (from the practitioner account)

1. Every deal the agent system booked is in the booking system, with matching amount, rate, dates, direction and status.
2. A deal in the booking system under a booking reference the agent system recorded as failed is a late booking and must show exactly one confirmed cancel.
3. A deal the agent system shows as booked and the booking system lacks is a break for operations (`break_agent_booked_booking_system_absent`).
4. Every timed-out deal ends as never booked, or as booked and cancelled exactly once.
5. The agent system's copy of the limit usage matches the booking system's.

This depends on the booking system storing the agent system's booking reference. Without it, a late booking cannot be tied to its request.

### Run the cases

Each variant is an executable case in the public corpus. Pinned install and run, Python 3.12 or later:

```sh
python -m pip install agent-evidence-vectors==@PIN@
agent-evidence-vectors-trade-booking --output trade-booking-result
```

The command checks every corpus member against its manifest, judges all cases from the signed records alone without reading the expected answers, and exits 1 if any case differs. The corpus is [probityai/agent-evidence-vectors](https://github.com/probityai/agent-evidence-vectors). Its sibling lost-call cases for paid tool calls are `lost_call_no_statement` and `lost_call_settled_not_run` in the occurrence-binding corpus.

### Questions for the reviewer

1. Lifecycle accuracy: are these sequences realistic? Which assumptions depend on the bank, the booking system or the LP, for example check-only versus atomic cancel, or all-or-none LP execution?
2. Is a search by reference that finds nothing final, or is the deal held until a reconciliation closes? The cases hold it, and the stricter reading is a choice to confirm or change.
3. Which missing failure case would materially change the answers? One known gap: an LP failure that is itself a lost reply.

### Residual gaps

Operations authorship of a cancel is read from the booking system's event actor; where the booking system does not record it, variant 3 cannot be told apart from the agent system's own cancel. The corpus judges signed records and does not judge price, amount or settlement.
