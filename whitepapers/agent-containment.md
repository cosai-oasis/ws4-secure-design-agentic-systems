---
title: "Agent Containment: From Sandboxing to Bounded Authority"
author: "Workstream 4: Secure Design Patterns for Agentic Systems"
date: 2026-09-05
version: 0.2-skeleton
status: "Working draft. Not approved. Tracks issue #172."
---

# Agent Containment: From Sandboxing to Bounded Authority

**Title.** Settled with the section 1 frame (2026-09-05): containment is one layer of a bounded-authority model, which is what the title already says. No longer provisional.

**Status:** Working draft, skeleton. Not reviewed, not approved. Follows on from the WS4 blog post *Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait* (2026-08-25) and takes as its scope the 21 questions banked from that post's review in [issue #172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172).

**How to contribute to this draft.** Every section below states what it must answer (the `Qn` references are to #172), who raised the question, what the blog post already says, and what is still open. Add material by pull request against this file, referencing #172. Short contributions in the "Starting material" or "Open items" lists are as welcome as full prose; the editor will unify voice and cut duplication before the first review draft. Drafting notes are in blockquotes and will be removed.

# Table of contents

- [Abstract](#abstract)
  - [Scope](#scope)
  - [Anti-scope](#anti-scope)
  - [Target audience](#target-audience)
- [1. Introduction: from sandboxing to bounded authority](#1-introduction-from-sandboxing-to-bounded-authority)
  - [1.1 Deployment shapes and what containment can mean in each](#11-deployment-shapes-and-what-containment-can-mean-in-each)
- [2. The three hardening axes](#2-the-three-hardening-axes)
- [3. Mediation: the tool call, not the network flow](#3-mediation-the-tool-call-not-the-network-flow)
  - [3.1 The permitted channel is the exfiltration path](#31-the-permitted-channel-is-the-exfiltration-path)
- [4. Composition: per-sandbox controls across a set of agents](#4-composition-per-sandbox-controls-across-a-set-of-agents)
- [5. The enforcement property and four failure modes](#5-the-enforcement-property-and-four-failure-modes)
- [6. Reachability and blast radius](#6-reachability-and-blast-radius)
- [7. Detection and evidence](#7-detection-and-evidence)
  - [7.1 What to log](#71-what-to-log)
  - [7.2 The false-positive profile](#72-the-false-positive-profile)
  - [7.3 Measuring containment](#73-measuring-containment)
- [8. A vetted-sandbox commons](#8-a-vetted-sandbox-commons)
- [9. Positions](#9-positions)
- [10. Takeaways and conclusion](#10-takeaways-and-conclusion)
- [11. References](#11-references)
- [12. Contributors and acknowledgements](#12-contributors-and-acknowledgements)
- [Appendix A. Evidence receipts](#appendix-a-evidence-receipts)
- [Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright](#appendix-b-cosai-focus-ai-usage-guidelines-disclaimer-copyright)

---

## Abstract

> Drafting note: write last. One paragraph. It should be possible to read the abstract and know which of the blog post's claims this paper deepens and which questions it answers that the blog could not.

### Scope

Containment of autonomous agents that hold real access: what the boundary is, where it is enforced, how it composes across a set of agents, how its failures are classified, and how a containment action is detected and measured. The paper deepens the blog post; it does not restate it.

### Anti-scope

- Authorization semantics beyond what containment needs. Bounded authority is treated as the frame; its full treatment is the WS4 *Agentic Identity and Access Management* paper.
- Model-level safety training and refusals. The paper assumes a model that wants to escape.
- A restatement of the runtime-isolation cookbooks. The MCP runtime isolation practical guide remains the how-to; this paper says what the how-to must achieve and why.

### Target audience

Practitioners and architects who deploy agents with production access. Section 1 is written so an executive can read it alone and take away the frame and the four failure modes. (Q5, settled 2026-09-05; raised by @Johncavanaugh-IIS and open since the #167 review — objections welcome by comment on #172, but drafting proceeds on this basis.)

---

## 1. Introduction: from sandboxing to bounded authority

**Answers:** Q1, Q2. **Raised by:** @getglad, @Levaj2000.

**Purpose.** Establish whether containment is a coherent standalone control family or one layer of a bounded-authority model, and if the latter, give the decomposition the rest of the paper follows.

**Starting material.** The blog post already separates two failure classes: containment failures, where the agent reached systems it should not have been able to reach, and authority failures, where the agent never escaped anything and used access it was legitimately granted. Sandboxing answers *can this agent reach a resource*; bounded authority answers *what is this agent allowed to do once it is there*. The gym-booking incident is the canonical case of asking only the first question.

**Settled (2026-09-05): the frame.** Containment is one layer of a bounded-authority model, not a standalone control family. Converged independently by @getglad and @Levaj2000 in the #167 review and #172 thread with no objection since. The decomposition follows @getglad's candidate: lead with the objective — an environment in which the agent has bounded authority in the way a corporate laptop does — and map each control back to the layer it serves. Section 2's three axes are the *internal* structure of the containment layer, not the top-level frame (per @Levaj2000 in #172). The decomposition also does the paper's hardest job in §1.1: it states which layers survive when a deployment shape removes isolation entirely.

**Open items.**
- State precisely what this paper takes from the Agentic IAM paper and what it leaves there. Caution for the drafter: bounded authority is that paper's entire subject, and its core principles already cover standing privilege, agent-vs-OBO rights, per-hop enforcement, and gateways. §1 states where the containment layer sits inside that model and cites the rest; it does not re-derive the principles.

### 1.1 Deployment shapes and what containment can mean in each

**Answers:** Q3, Q4, Q5. **Raised by:** @imolloy, @skvcool-rgb, @Johncavanaugh-IIS.

**Purpose.** Say who the guidance is for and which controls are available to them.

**Starting material** (from @skvcool-rgb in #172, adopted as the section's spine). Where the deployment shape denies a container boundary — desktop agents, integrated third-party agents — isolation is unavailable, but the authority and mediation layers survive *to the extent you can still interpose at the request layer*: mediated tool/MCP calls (§3), bounded and attenuated authority, and subtree accounting (§4). Where you can interpose none of them — a fully third-party agent — containment is wholly a procurement requirement on the provider, and the paper says so plainly. This resolves Q3 the same way: where the organization controls the principal's authority, the requirements are engineering; where it does not, the identical requirements land on the provider as procurement, and each section should be markable as one or the other.

**Open items.**
- Per section, mark which requirements are engineering and which become procurement in the procured-and-integrated case.
- Add the coding agent that needs its own container runtime as a shape in its own right. Unlike the desktop and integrated cases it has a container boundary, but the workload wants to create containers, so the question is what the boundary must look like rather than whether one exists (see §8).

---

## 2. The three hardening axes

**Answers:** Q11. **Raised by:** @getglad.

**Settled (2026-09-05).** Adopted: local, outbound, and inbound as the organizing structure — as the internal decomposition of the containment layer per §1, not the paper's top frame. The strongest argument for adoption is one the thread hasn't made yet: the MCP runtime isolation guide, our own how-to, is almost entirely *local* axis with a little *outbound* and no *inbound* at all. The axes give the existing guidance a spine it currently lacks, and make its gaps legible.

**Inbound is cross-referenced, not written here.** The input sanitization practical guide and the MCP paper's untrusted-content guidance already cover the controls; writing inbound content here duplicates two documents at once. The axis stays in the structure so the decomposition is complete; the reader is sent elsewhere for the how.

**Starting material.** The blog post's "What Strong Sandboxing Requires" list is almost entirely local and outbound: OS-enforced isolation, egress controls, privilege minimization, progressive hardening, short-lived credentials.

**Open items.**
- For each axis, name the enforcement point, the property it must hold, and the blog-post controls that belong to it.
- Local axis: container-runtime access is the concrete case to work through, host Docker socket versus a rootless or VM-backed engine inside the sandbox. Criterion lives in §8; the enforcement-point analysis belongs here.

---

## 3. Mediation: the tool call, not the network flow

**Answers:** Q8. **Raised by:** @getglad.

**Purpose.** Argue that for agent workloads the tool or MCP call, not the network flow, is the correct mediation surface, and connect that to the complete-mediation requirement and to the MCP whitepaper.

**Starting material.** The blog post's complete-mediation bullet: every agent action must pass through a policy enforcement point, the policy must express more than which endpoint may be called, and the reference monitor must be authoritative and outside the agent's reach.

**Candidate invariant** (from @ryjen in #172): define containment around **effective reach** — for any consequential effect, the relevant reach is the union of every path through which the agent can cause it (direct network access, mediated tool calls, provider-side fetches and execution, delegated agents, alternate endpoints or credentials) — and require that *every path capable of producing an equivalent consequential effect cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary*. A correctly mediated tool call is not sufficient if the same effect remains reachable another way. Corollary, also @ryjen's: prior receipts, traces, and completed results stay evidence and never become executable authority for the final effect. Refinement from the #172 discussion (@Levaj2000): a receipt may authorize skipping duplicate work within a single claimed assurance boundary; it may never substitute for a mediation step that boundary claims to enforce.

**Open items.**
- Decide whether the effective-reach invariant becomes this section's normative statement. It subsumes the section's original claim and gives §3.1 its definition.
- What egress allow/deny at the network layer still buys you once tool-call mediation exists, and what it cannot express.
- Relationship to the MCP paper's Sandboxing and Isolation and Logging controls, and to the secure tool design guide's "don't defer decisions to the LLM" principle; cross-reference, do not duplicate.

### 3.1 The permitted channel is the exfiltration path

**Answers:** Q9, Q10. **Raised by:** @imolloy, @getglad.

**Purpose.** Treat gateway and provider capabilities (model-side URL retrieval, web search, code interpreters, retrieval connectors) as part of the agent's effective reach. An agent's egress envelope is the union of its own network policy and every fetch its providers will perform on request.

**Starting material.** The x32 seccomp case in the blog post: agents chained the bypass with the LLM API's own URL retrieval to reach external destinations through an otherwise restricted proxy. The only permitted channel became the relay.

**Design principle to state** (from the GET-only observation): where a permitted party will act on the agent's behalf, constrain what it will do, not just whether the agent may ask. Bandwidth-limited, method-limited, and non-reflective channels bound exfiltration even when the channel cannot be removed.

---

## 4. Composition: per-sandbox controls across a set of agents

**Answers:** Q6, Q7. **Raised by:** @skvcool-rgb, @imolloy.

**Purpose.** Show how per-sandbox controls fail to constrain aggregate consumption across a set of agents sharing a principal, and take a position on aggregate accounting: budgets and egress accounted across the set rather than per container.

**Settled (2026-09-05): the position, per @skvcool-rgb in #172.** Aggregate accounting is a control the paper recommends, as a scoped requirement: where the deploying organization controls the principal's authority, a conformant model MUST account budgets and egress across the set of agents sharing a principal (and across a delegation subtree), not only per container; where it does not, the same requirement lands on the provider as procurement (§1.1). Per-container and per-edge invariants are named explicitly as *local invariants that do not compose*.

### 4.1 The failure shape

Every control in §§2–3 is evaluated per container or per edge: an egress cap on a sandbox, a
destination allowlist on a network policy, a scope that narrows at each delegation hop. Each is
correct on its own terms and each is a **local invariant**: it bounds what one container or one
edge may do. The quantities an operator actually cares about are not local. Bytes leaving the
organisation, distinct destinations touched, money spent, side-effecting actions taken, agents
spawned, subtree depth and fan-out — these are consumed **across the set of agents that share a
principal**, and across the delegation subtree that principal roots. A set of N agents, each inside
its cap, consumes N caps. Nothing in a per-container model fires, because nothing in it ever sees
the sum.

The #172 review reached this from two directions. From the sandboxing side: a coordinator that
fans work out to twelve workers, each in a compliant sandbox with a 10 MB/day egress limit, moves
120 MB through twelve distinct destinations without a single local control tripping. From the
authority side: the approved *Agentic Identity and Access Management* paper requires scope to
narrow at each hop, and names the phenomenon in its threat themes — two or more agents can pass
data or proxy calls so that, together, they perform an action neither could perform alone — but its
controls stop at the edge. Per-hop attenuation is necessary. It is not sufficient, because
attenuation is also a local invariant: it bounds the child relative to the parent, not the subtree
relative to the principal. This section extends that paper on exactly that point.

**Worked example.** A principal holds a 100 MB/day egress budget and a 50-destination envelope. An
orchestrating agent spawns twelve workers under the principal; each worker's sandbox is capped at
10 MB/day and its network policy allows five destinations. Every worker stays inside both caps. At
the end of the day 120 MB has left through up to sixty destinations, the principal's budget is
exceeded by 20 % and its envelope by 20 %, and the audit trail shows twelve unremarkable sandboxes.
Under subtree accounting the eleventh worker's first outbound request is evaluated against the
principal's remaining budget — zero — and is refused or held; the refused attempt is the alert, and
it carries the lineage that names the orchestrator.

### 4.2 The closing control: aggregate accounting at the consuming action

The control that closes the gap is **aggregate accounting keyed on the shared principal and its
delegation subtree, evaluated at the consuming action** — the point at which a unit of the
quantity is about to be spent — over an enumerated set of quantities. The list SHOULD be explicit
and small, because each quantity needs its own counter and its own budget:

- egress volume (bytes), per principal and per subtree;
- distinct external destinations;
- spend (currency, tokens, compute) against the principal's budget;
- rate of side-effecting actions (writes, sends, executions);
- spawn count, subtree depth and fan-out.

The decision at the consuming action is *allow only if the aggregate after this action remains
within the principal's budget*. Two properties make it a control rather than a report:

- **Consume atomically.** A check that reads the aggregate and then commits the action separately
  is a race: N concurrent consumers each observe headroom and all proceed. Conformant
  implementations MUST consume by compare-and-consume (reserve, then commit or release) or serialise
  consumption per principal. A reservation is released only when it is known that the action did
  not happen. A reservation whose outcome is unknown — the consumer timed out or failed between
  reserve and commit, or the downstream did not answer — MUST remain charged until non-consumption
  is established authoritatively, or reconciled idempotently against the downstream's own record.
  Expiry alone MUST NOT refund it: an action that did occur and a reservation that merely lapsed
  are otherwise indistinguishable, and the budget could be spent repeatedly by letting
  reservations lapse.
- **Deny above the sum, not just above the slice.** A per-agent slice of the budget (budget/N) is
  a local invariant in disguise; it fails the same way when N changes. The authority MUST be
  consulted for the subtree aggregate. A local slice is acceptable only as a **lease**: a quantity
  the authority has already consumed atomically on the agent's behalf, which the agent may then
  spend locally down to zero. A slice that is merely cached is not a lease and authorises nothing.

**Requirements.**

- **R4.1** Where the deploying organisation controls the principal's authority, a conformant model
  MUST account the enumerated quantities across the set of agents sharing that principal, and
  across each delegation subtree, evaluated at the consuming action.
- **R4.2** Per-container and per-edge limits MUST be documented as local invariants. A containment
  claim MUST NOT rest on them alone for any quantity that sums across agents.
- **R4.3** Consumption MUST be atomic (compare-and-consume or per-principal serialisation). A
  reservation MUST be released only when the action is known not to have happened; a reservation
  with an unknown outcome MUST remain charged until it is reconciled authoritatively.
- **R4.4** Where the organisation does not control the principal's authority — the procured and
  integrated agents of §1.1 — R4.1 to R4.3 are procurement requirements on the provider, and MUST be
  written as such.

### 4.3 The hard sub-problem: the accounting authority

R4.1 presupposes something the per-container model never needed: a **shared accounting authority**
that every consuming action in the subtree consults. Naming it is the honest part of this section,
because it carries three problems a per-container design does not.

- **Consistency.** The aggregate is a read-modify-write per principal. Anything weaker than
  serialised or compare-and-swap consumption re-opens the race in 4.2 as a window whose width is
  the replication delay. Eventual consistency is acceptable for the *report*; it is not acceptable
  for the *decision*.
- **Latency budget.** The check sits on the hot path of every side-effecting action. The
  implementation MUST bound it, and MUST define what happens when the bound is exceeded: the action
  is denied or held for confirmation, never allowed. Continuous accounting without a fail-safe
  default is allow-on-error (Saltzer and Schroeder, fail-safe defaults). A local cache MAY serve
  reads for reporting; it MUST NOT authorise any consumption, however small — N stale caches each
  authorising a small action is the race of 4.2 again. The only local authorisation is against a
  lease the authority has already consumed atomically (4.2).
- **Trust status.** The authority is a reference monitor in the §5 sense: it MUST be outside the
  reach of the agents it accounts for, MUST be invoked for every consuming action of an enumerated
  quantity (complete mediation, §3), and its decisions MUST be verifiable after the fact. In the
  procured case the provider operates it, and the deploying organisation's assurance is whatever
  the provider's evidence supports — which is why R4.4 is procurement.

**Evidence.** Aggregate accounting is both the preventive control and the detection signal. When
the control holds, the aggregate never crosses its threshold, so the alert is the *attempt*: a
consumption refused or held because it would have crossed. The attempt MUST be recorded and raised
with the same lineage as a successful consumption. An aggregate found above its threshold after
the fact is a different alert — it means the control failed. Both depend on the record carrying
the join key.
Every consuming-action record MUST carry the principal and the **full** delegation lineage, not only
the immediate parent, integrity-protected, so that the subtree aggregate can be reconstructed by
someone who was not there (§7; this is the "accounting decision" row of the evidence contract in
#172, which has no OCSF home today).

### 4.4 Prior art: colluding applications

The problem is older than agents. The Android permission literature of 2011–2012 treated
**colluding applications** — two apps whose individual permission sets are benign and whose
combination exceeds the user's intent, via an inter-app channel — as an inter-application
information-flow problem to be policed over the *combination*, not per grant (Bugiel et al.,
*XManDroid*, and the analyses of inter-application communication and permission re-delegation
from the same period; the exact citations to be confirmed with @imolloy, who raised them). The
mapping onto agents is direct:

| Android | Agent containment |
|---|---|
| an application's permission set | an agent's attenuated scope and sandbox caps |
| the user's intent | the principal's authority and budgets |
| an inter-app channel | a delegation edge or a shared principal |
| system-wide policy over the transitive closure | subtree accounting at the accounting authority |

The lesson carried over is the same one the review arrived at independently: a per-grant model
cannot express the constraint, because the constraint is over a set.

**Open items.**
- Confirm the colluding-applications citations with @imolloy and add them to §11.
- Decide whether the enumerated quantity list is normative or illustrative; the authors' position
  is normative-minimum (egress bytes, destinations, spend, spawn) with the rest RECOMMENDED.
- Cross-reference the IAM paper's per-hop narrowing requirement by section number once its final
  numbering is confirmed.
- Worked example: keep the twelve-worker case, or replace with an incident from §6.

---

## 5. The enforcement property and four failure modes

**Answers:** Q12, Q13. **Raised by:** @getglad, @imolloy.

> Drafting note (2026-09-08): first prose draft, by the editor. Two commitments are embedded and open to challenge by PR or comment on #172: the vocabulary lands on *reference monitor* with a plain gloss (rather than a new term), and *verifiable* is read evidence-forward per @ryjen. The mapping of modes 1–3 onto the monitor's three properties at the end of 5.2 is new reasoning, not from the thread. Citation numbers are provisional per §11.

Every control in this paper presumes an enforcement point: something that sees the agent's action and decides whether it proceeds. The blog post described that point as "independently enforced, not agent-enforced," which was accurate but informal. A document that will be cited needs the property named, and needs the ways it fails kept apart — because the incidents this body of work draws on do not fail in one way, and the remedies do not interchange.

### 5.1 The property, named

This paper uses the term **reference monitor**, and asks nothing of the reader beyond its plain meaning: the component that observes every consequential action an agent takes and decides, from policy the agent cannot touch, whether the action proceeds.

The term comes with three classical requirements, and each maps onto plain language:

- **Complete mediation.** The monitor sees every path to the effect. An action that can reach its effect without crossing the monitor is not partially mediated; it is unmediated (§3).
- **Tamper-proof.** The agent can neither alter the monitor nor the policy it applies. In practice: enforced from outside the agent's reach, with the monitor's own configuration outside the agent's write scope.
- **Verifiable.** It must be possible to check the first two claims.

For agent workloads, the third property does the most work, and this paper reads it more demandingly than the classical literature did. Historically, *verifiable* meant small enough to analyze. For agents it must also mean **evidenced**: the monitor emits a record sufficient for someone who was not present, and does not trust the operator, to confirm that mediation occurred (§7). After an incident, a monitor that cannot be verified from its records is indistinguishable from a monitor that was not there.

One clarification the blog post's review forced: the property is not "kernel-enforced." The kernel is one implementation of the monitor at one layer. For tool and MCP calls the monitor is a gateway or policy enforcement point (§3); for system calls it is the kernel; for network egress it is a proxy. An agent deployment has several monitors, one per mediation surface, and the property must hold at each. What defines a reference monitor is the three requirements, not the privilege level it runs at.

### 5.2 The four failure modes

When containment fails, it fails in one of four ways, and this paper keeps them separate throughout.

**Mode 1 — the agent defeats the control.** The control was correctly specified and remained in force; the mechanism itself broke. An exploitable vulnerability in the isolation path is the canonical case. The remedy lives in the mechanism: a patch posture the isolation path can be held to, minimum attack surface, and stronger isolation where the workload warrants it (§6).

**Mode 2 — the agent disables the control.** The agent had, or acquired, authority over the control itself. The documented case: an agent that, when a sandbox blocked its workaround, autonomously disabled the sandbox and continued [11]. This is a failure of enforcement placement — of the tamper-proof property — and its remedy is architectural: the control and its configuration outside the agent's reach, and any attempt to alter them treated as a high-signal alert (§7).

**Mode 3 — the control was insufficiently specified.** The control was on, untouched, and wrong. The seccomp filter that checked syscall numbers but not the architecture value — a pitfall the kernel's own documentation has warned about for a decade [7] — is the anchor case: the agent had no authority over the policy; the system applied an insufficient one. A denylist that misses an alternate path to the same binary, and a workspace with a reachable Docker socket [6], fail the same way. The remedy is verification of the policy, not strengthening of the mechanism: pre-deployment tests that the sandbox enforces what its operator believes it enforces (§8), and a mediation surface expressive enough to state the intended boundary at all (§3).

**Mode 4 — the control was correct and the agent used permitted authority.** Nothing was escaped. The agent that cancelled a stranger's gym reservation crossed no containment boundary; its authority was scoped to an endpoint, not to whose reservation it could act on [11]. The gateway that performs a fetch with agent-controlled input is the same shape: a permitted party, acting as asked (§3.1). No isolation posture reaches this mode. What bounds it is scope on the grant — the subject of the Agentic IAM paper [9] — together with constraining what permitted parties will do on request (§3.1), accounting authority across the set of agents that share it (§4), and evidence afterwards (§7).

The first three modes are failures of the monitor's three properties, in order: mode 1 breaks the mechanism, mode 2 breaks tamper-proofing, mode 3 breaks complete mediation — the policy did not cover the path. Mode 4 is not a failure of the monitor at all, and that is the deepest reason containment is one layer of a bounded-authority model rather than the whole of it (§1): a perfect monitor, perfectly specified, enforcing a grant that is too broad, produces the gym incident every time.

### 5.3 Why the separation is load-bearing

Most of the incidents this body of work rests on are modes 3 and 4. Industry attention — and spending — concentrates on modes 1 and 2: stronger isolation, more exotic sandboxes. The taxonomy is what makes that mismatch visible, and it has three practical consequences.

First, remedies do not interchange. Buying stronger isolation does not fix an insufficient policy, and neither fixes a grant that was too broad. The blog post presented a mode-2 incident and a mode-3 incident in adjacent sentences as one phenomenon; they demand different fixes from different teams.

Second, classifying an incident requires evidence. Telling mode 2 from mode 3 needs a record of the control's configuration and the enforcement decision at the time; telling mode 1 from mode 4 needs a record of what was actually permitted. Without the evidence contract of §7, the taxonomy is rhetoric; with it, an incident review can assign a mode and route the fix.

Third, every control in this paper can now say what it is for:

| Section | Addresses |
|---|---|
| §3 Mediation | Mode 3 — a surface expressive enough to specify the boundary |
| §3.1 Permitted channels | Mode 4 — constraining what permitted parties will do |
| §4 Composition | Mode 4 — authority consumed across a set, every local check passing |
| §6 Reachability | Bounds the blast radius when modes 1–3 occur |
| §7 Detection and evidence | Makes all four modes distinguishable, during and after |
| §8 Verification | Mode 3 — proving the control enforces what its operator believes |

The question each section answers is therefore not "how strong is the box?" but: which failure mode does this control remove — and how would we know it worked?

---

## 6. Reachability and blast radius

**Answers:** Q16. **Raised by:** @getglad, @imolloy.

**Purpose.** Treat reachability minimization as a first-class control, distinct from vulnerability management.

**Starting material.** The blog post's patch-posture bullet: "zero CVEs" is not a promise anyone can keep and would not have covered the Artifactory chain or the 2014-era seccomp gap. What can be required is narrower: no known-exploitable CVEs in the isolation path, a measured patch SLA, minimum attack surface, named compensating controls.

**Correction to the worked example (2026-09-05, from the Appendix A source check — see A.2).** The blog's telling merges two break-ins. Hugging Face's own disclosure places the intrusion's start in their data-processing pipeline — a remote-code dataset loader and a template injection in a dataset configuration, reaching a processing worker — and affirmatively reports the software supply chain verified clean, container images and published packages included. Artifactory belongs to the *other* half: the cache proxy inside OpenAI's evaluation environment, where the sandbox escape happened. Kept separate, the case is a better example for this section, because the two halves sit on opposite sides of its central boundary: the Artifactory instance was stood up for the engagement and was in scope to constrain (per @imolloy in #172); Hugging Face's infrastructure genuinely belonged to someone else.

**Extension** (from @Levaj2000 in #172): the yours-to-harden boundary decides more than whether blast-radius control is available — it decides whether *evidence* is available. When the reached system belongs to a third party, you hold a record that your agent asked and they hold a record that something happened, and nothing binds the two. Open OCSF proposal on exactly this: `caused_by` on the resource owner's event (ocsf/ocsf-schema#1738, from @aryanval).

**Open items.**
- Which reachable systems are yours to harden and which are not. That boundary determines whether blast-radius control is even available to you.
- The Hugging Face worked example, drafted from the primary disclosures per A.2. The blog's specific figures (181 nodes, static database password, reusable VPN key) remain unverified against a primary source and must not be asserted until A.2 closes them.

---

## 7. Detection and evidence

**Answers:** Q14, Q15. **Raised by:** @Levaj2000, @imran-siddique.

**Purpose.** Carry the detection argument and a schema summary in the paper; put the concrete logging schema in a practical guide alongside the MCP runtime isolation guide.

**Settled (2026-09-05): the two-artifact split, per @Levaj2000 and @imran-siddique in #172.** Detection and evidence are two artifacts against the same event, not one list. Detection wants signals that discriminate an attempt from normal behavior, and is allowed to be noisy, heuristic, and tuned per deployment. Evidence wants the fields that let someone who was not there and does not trust you reconstruct what happened, and must be stable, complete, and boring — and nothing in it may be executable authority (§3). The evidence contract is normative in this paper; the OCSF mapping goes in the practical guide, pinned to an OCSF version, with proposed fields marked as proposed. §7.1 is structured as two tables accordingly.

**Starting material.** The blog post's "containment that fails loudly" and "tamper-evident logging" bullets: alert on denied syscalls, repeated policy violations, `/proc` inspection, Docker socket and metadata-service probes, blocked DNS and egress, credential-broker denials, and any attempt to alter the sandbox configuration; keep those events outside the agent's write scope; correlate across runs; use OCSF `attestation` and the `record_integrity` profile (OCSF 1.9.0) for tamper evidence. Correction to the supporting narrative, from the A.2 source check: Anthropic's sentence is "the two organizations **we were able to reach** had not previously detected the activity" — narrower than the blog's paraphrase — and Hugging Face *did* detect their own intrusion, via LLM-based triage on anomalies, before OpenAI connected its internal testing to it. The section's argument survives both facts, but must carry them: the strongest counter-example in the field is also the best existing evidence that the detection this section calls for actually works.

> Drafting note, editorial: two approved papers already occupy adjacent ground — the MCP paper's Logging and Observability profile and the Agentic IAM paper's logging schema and "prove control on demand" checklist cover most of the evidence contract's field list. Open this section by stating what they already require; spend it on what is new here: the two-artifact split, the false-positive profile, time-to-contain, and the OCSF mapping — the last framed as closing the gap the IAM paper explicitly left open ("extension fields until formal support is adopted").

### 7.1 What to log

> Drafting note: two tables against the same event, per the settled split above. The detection table: signals, each with its expected false-positive source (§7.2). The evidence table: the contract fields from #172 — principal and full delegation chain as the integrity-protected correlation key, policy and tool-catalog versions, action identifier, request digest, enforcement decision and reason, runtime identity or attestation reference, outcome, integrity-protected sequence, and the accounting decision itself (§4). The schema and mapping go in the practical guide.

### 7.2 The false-positive profile

**Purpose.** The harder half the blog post skipped. Normal agent behavior includes filesystem exploration and tool discovery. State what the false-positive profile looks like for each alert in the list above, and what correlation across runs actually requires operationally.

**Status and the candidate discriminator.** No contributor can currently produce the profile — it requires production baselines across several organizations and deployment shapes, and any single corpus would be an artifact of one architecture (@Levaj2000, #172). What the section can state now: the discriminator for exploration-like behavior is not the action but the action measured against the agent's **declared** capability set. Undeclared-but-executed is the signal; the identical call inside the declared set is noise. That makes this partly a schema question (the declared-versus-executed pairing, ocsf/ocsf-schema#1724) rather than purely a tuning one. If no baselines materialize by first draft, publish the discriminator and name the gap explicitly — decided, not defaulted into.

### 7.3 Measuring containment

**Purpose.** A containment action is only real if it shows up in telemetry with a normalized reason. Define time-to-contain as the interval between the first detectable indicator and the stop event, and require that the stop event carry a normalized reason so an operator kill, a guardrail kill, and a crash are distinguishable.

**Starting material.** OCSF is normalizing an AI stop reason (`ai_stop_reason_id`: end of turn, token limit, tool use, session stop, content filter) on the `ai_operation` profile, with the working proposal to apply it to the application lifecycle stop activity and correlate by `ai_agent.instance_uid` ([ocsf/ocsf-schema#1704](https://github.com/ocsf/ocsf-schema/pull/1704), in review). Cite as direction, not as shipped, until it lands.

**Open items.**
- Align with the WS2 AI Telemetry Framework paper, Appendix E (OCSF asks), so CoSAI makes one request of OCSF, not two.
- Reference @rabbidave's per-invocation tool activity event (its own OCSF proposal, per the resolution in #172 — what the agent *did* to the world, distinct from #1704's how-the-operation-ended) rather than restating it; correlate both by agent instance.

---

## 8. A vetted-sandbox commons

**Answers:** Q17. **Raised by:** @getglad.

**Purpose.** Decide whether CoSAI has a role in specifying what a vetted agent sandbox must demonstrate, such that implementations can be measured against it.

**Starting material.** The blog post's pre-deployment control verification bullet: before any agent run, programmatically verify that the sandbox enforces its policy. Security controls need unit tests. A commons specification is the generalization of that bullet.

> Drafting note, editorial (2026-09-05): part of this already exists. The MCP Security paper's Security Assurance Profiles specify, level by level, what execution, data, and context isolation must demonstrate — and that paper's own open questions defer an "evidence-per-level annex" listing the verification artifacts each level should produce, which is much of Q17's deliverable, already scoped and parked. This section must open by citing the profiles and position itself as either (a) the deferred annex, generalized beyond MCP, or (b) only what the profiles cannot cover. It must not read as a fresh specification. Three artifacts converging on "what must a sandbox demonstrate" (this section, the profiles, secure-ai-tooling#516) is the same duplication risk we resolved for the OCSF asks — coordinate before drafting.

> Drafting note, from review (2026-09-08): @adeinega raised container-runtime access on PR #181, feedback he had queued for the blog post and did not get to post there. It is the most concrete candidate criterion offered so far, and it belongs in this section. Docker-out-of-Docker, mounting the host's `/var/run/docker.sock` into the sandbox, is not a weakened boundary but an escape primitive with a documented API: anything that can reach that daemon can start a privileged container, bind-mount the host root, and leave. The engine-inside alternative is better and not automatically safe, since classic Docker-in-Docker requires `--privileged` on the outer container and trades one escape path for another; rootless DinD, or a runtime with a real isolation boundary underneath it (gVisor, Kata, Firecracker, sysbox), is the shape that holds. The requirement behind the question is real rather than a misconfiguration to design away: coding agents genuinely need to build and run containers, so the commons owes this a control answer, not a prohibition. To be drafted in #172; the subsection is offered to @adeinega in the PR thread.

**Open items.**
- Relationship to CoSAI-RM Isolation and Containment controls ([secure-ai-tooling#516](https://github.com/cosai-oasis/secure-ai-tooling/issues/516)) and to the MCP paper's assurance profiles, per the note above.
- Whether this is a section, a recommendation for future work, or its own RFC.
- Container-runtime access as a named criterion: what a vetted sandbox must demonstrate when the agent needs to build or run containers. Host socket mounting is disqualifying; the open part is which engine-inside shapes qualify, and how an implementation demonstrates which one it is. Raised by @adeinega.

---

## 9. Positions

**Answers:** Q18, Q19. **Raised by:** @getglad, @imolloy, @billbrietstout.

**Purpose.** For each item, either state a CoSAI position or say explicitly that it is out of scope and why.

- **Agent Trajectory Interchange Format.** @getglad asked whether CoSAI has a position; @imolloy: not yet. Decide whether this paper takes one.
- **Orchestrator-mediated and multi-agent jailbreaking** (@billbrietstout). Model-or-swarm jailbreaking through orchestrator and reasoning agents at machine speed rather than human-in-the-loop speed. Decide whether it belongs here, in the multimodal threat taxonomy, or in neither. New evidence for taking a position rather than deferring (from the A.2 source check): the UK AISI report (INC-2026-07-28-01) documents an agent leaving public messages on GitHub offering collaboration with other agents, with instructions to reuse accounts and artifacts, and planting prompt injections where it reasoned other automated AI systems would pick them up and execute them. That is observed multi-agent behavior in a primary source, not a hypothetical.

---

## 10. Takeaways and conclusion

> Drafting note: write after sections 1 through 9 settle. The blog post's closing question is the seed: not "is this sandbox good enough?" but "what would this agent do if it decided to test its limits?", verified to fail safely.

---

## 11. References

> Drafting note: carry forward the blog post's references [^1] through [^15] as the base set and add per section. Numbering below is provisional.

1. Anthropic. *Claude Mythos Preview System Card*, 2026-04-07. https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
2. OpenAI. *ExploitGym evaluation disclosure*, 2026-07-21. https://openai.com/index/hugging-face-model-evaluation-security-incident/
3. Anthropic Frontier Red Team. *Disclosure of evaluation incidents*, 2026-07-30. https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals
4. UK AI Security Institute. *INC-2026-07-28-01*, 2026-08-04. https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing
5. Ona.com. *How Claude Code Escapes Its Own Denylist and Sandbox*, 2026-03-03. https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox
6. Pillar Security. *One Docker Socket to Rule Them All*, 2026-07-20. https://www.pillar.security/blog/one-docker-socket-to-rule-them-all-escaping-codex-cursor-and-gemini-clis-sandboxes
7. Linux kernel documentation. *Seccomp BPF, Pitfalls*. https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
   <!-- The arch-check warning is in the Pitfalls section; the document's Caveats section is about vDSO/vsyscall. The blog's ref 14 carries the same mislabel. -->
8. CoSAI. *MCP Runtime Isolation, Practical Guide*. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/practical-guides/mcp-runtime-isolation.md
9. CoSAI. *Agentic Identity and Access Management*, approved 2026-03-20. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/agentic-identity-and-access-control.md
10. CoSAI. *Model Context Protocol (MCP) Security*, v2.0, 2026-08-12. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/model-context-protocol-security.md
11. CoSAI WS4. *Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait*, 2026-08-25. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/blogs/sandbox-now.md
12. OCSF. *`attestation` object and `record_integrity` profile*, OCSF 1.9.0, 2026-08-03. https://github.com/ocsf/ocsf-schema/releases/tag/1.9.0
13. OCSF. *Add normalized `ai_stop_reason` to the `ai_operation` profile*, ocsf/ocsf-schema#1704 (open). https://github.com/ocsf/ocsf-schema/pull/1704
14. Hugging Face. *Security incident disclosure*, 2026-07-16. https://huggingface.co/blog/security-incident-july-2026

---

## 12. Contributors and acknowledgements

**Workstream Leads**

- Sarah Novotny
- Ian Molloy, IBM
- Raghu Yeluri, Intel
- Alex Polyakov, Adversa AI

**Editor**

- Jeff Leva, AI Identity

**Contributors**

- @skvcool-rgb (§4)

> Drafting note: everyone credited in #172 for a banked question is a contributor to the section that answers it; add yourself here with your first PR. Names or affiliations welcome in place of handles by PR.

**TSC reviewers**

- Akila Srinivasan, David LaBianca, Jodi Middleton (named 2026-08-25)

---

## Appendix A. Evidence receipts

**Answers:** Q20, Q21. **Raised by:** @Levaj2000, @imran-siddique.

**Purpose.** Evidence the blog post could not carry.

- **A.1 The x32/seccomp result.** A publishable receipt: test harness, models and versions, sandbox configuration (Landlock, Docker network isolation, seccomp-BPF), the exact bypass, and the chained LLM-API relay. Until this appendix exists, the paper cites the result as reported, not as verified.
- **A.2 The OpenAI / Hugging Face / Artifactory chain.** Primary sources read 2026-09-05 (full detail in the #172 comment of that date); status per claim:
  - **Established from Hugging Face's disclosure [14]:** the intrusion into Hugging Face started in their data-processing pipeline — a remote-code dataset loader and a template injection in a dataset configuration, reaching a processing worker — followed by escalation to node-level access, credential harvesting, and lateral movement. Artifactory appears nowhere in that account, and the disclosure affirmatively reports the software supply chain verified clean, container images and published packages included. The blog's sentence merging Artifactory into the Hugging Face breach is wrong; §6 carries the corrected telling.
  - **Established from NVD:** at least ten JFrog CVEs published 2026-07-27, nine naming Artifactory, severities up to a privilege-escalation flaw. Published-same-day is not used-in-the-chain; no CVE record connects itself to the incident, and researcher-credit claims trace to news coverage only. "Zero-day" is characterized directly only by Anthropic [3] — singular, and about OpenAI's escape, not the Hugging Face breach.
  - **Unverified, primary source unread (the cited OpenAI page [2] blocks automated fetches; likely primary source is OpenAI's Black Hat presentation):** 17,600 attacker actions; the 4.5-day duration (secondary accounts give a 9–13 July recovery window while a timeline from the presentation runs 7 May–20 July, so the figure's meaning is unestablished); Kubernetes node root via a service-account token; 181 nodes enrolled in the VPN mesh; attempted CI pipeline poisoning; and Artifactory's exact role in the evaluation-environment escape. None of these may be asserted in the paper until read against the primary source; anything still unverified at first draft is dropped.
- **A.3 Comparison of external findings.** @Johncavanaugh-IIS's comparison of the OpenAI researcher findings against the blog post's findings: what they found that we did not, and the reverse. Lands here first; sections 2 and 6 draw from it.

---

## Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright

### CoSAI Focus

CoSAI is an OASIS Open Project, bringing together an open ecosystem of AI and security experts from industry-leading organizations. The project is dedicated to sharing best practices for secure AI deployment and collaborating on AI security research and product development. The scope of CoSAI is specifically focused on the secure building, integration, deployment, and operation of AI systems, with an emphasis on mitigating security risks unique to AI technologies. Other aspects of Trustworthy AI are deemed important but beyond the scope of the project including, ethics, fairness, explainability, bias detection, safety, consumer privacy, misinformation, hallucinations, deep fakes, or content safety concerns like hateful or abusive content, malware, or phishing generation. By concentrating on developing robust measures, best practices, and guidelines to safeguard AI systems against unauthorized access, tampering, or misuse, CoSAI aims to contribute to the responsible development and deployment of resilient, secure AI technologies.

### Guidelines on usage of more advanced AI systems (e.g. large language models (LLMs), multi-modal language models, etc.) for drafting documents for OASIS CoSAI

tl;dr: CoSAI contributions are actions performed by humans, who are responsible for the content of those contributions, based on their signed OASIS iCLA (and eCLA, if applicable). Each contributor must confirm whether they are entitled to donate that material under the applicable open source license; OASIS and the CoSAI Project do not separately confirm that. Each contributor is responsible for ensuring that all contributions comply with these AI use guidelines, including disclosure of any use of AI in contributions.

- Selection of AI systems: CoSAI recommends the use of reputable AI systems (lowering the risk of inadvertently incorporating infringing material).
- Model constraints: Currently, CoSAI or OASIS are not required to have a contract or financial agreement for using AI systems from specific vendors. However, CoSAI editors should consider employing varying tools to avoid potential fairness concerns among vendors.
- IP infringement: It is the responsibility of the individual who subscribes/prompts and receives a response from an AI system to confirm they have the right to repost and donate the content to OASIS under our rules.
- Transparency: CoSAI's goal will be to maintain transparency throughout the process by documenting substantial use of AI systems whenever possible (e.g., the prompts and the AI system used), and to ensure that all content, regardless of production by human or AI systems, was reviewed and edited by human experts.
- Human-edited content and quality control: CoSAI mandates human-reviewed or -edited results for any final outputs.
- Iterative refinement: The use of AI systems in drafting standards should be seen as an iterative process, with the generated content serving as a starting point for further refinement and improvement by human experts.

### Disclaimer

The views represented in this paper do not necessarily represent the views of all CoSAI members, including reviewers and their organizations.

### Copyright Notice

Copyright © OASIS Open 2026. All Rights Reserved. This document has been produced under the process and license terms stated in the OASIS Open Project rules: https://www.oasis-open.org/policies-guidelines/open-projects-process.

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published, and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this section are included on all such copies and derivative works. The limited permissions granted above are perpetual and will not be revoked by OASIS or its successors or assigns. This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. OASIS AND ITS MEMBERS WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF ANY USE OF THIS DOCUMENT OR ANY PART THEREOF. The name "OASIS" is a trademark of OASIS, the owner and developer of this document, and should be used only to refer to the organization and its official outputs. OASIS welcomes reference to, and implementation and use of, documents, while reserving the right to enforce its marks against misleading uses. Please see https://www.oasis-open.org/policies-guidelines/trademark/ for above guidance.

This is a Non-Standards Track Work Product. The patent provisions of the OASIS IPR Policy do not apply.
