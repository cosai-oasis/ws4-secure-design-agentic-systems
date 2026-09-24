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

> Drafting note (2026-09-09): first prose draft, by the editor, implementing the settled frame. Written to the settled audience decision: an executive can read §1 alone and take away the frame and the four failure modes. Three commitments are embedded and open to challenge by PR or comment on #172: the five-layer decomposition (isolation, mediation, authority, accounting, evidence) — the thread's "map each control back to the layer it serves" made concrete; the unpacking of @getglad's corporate-laptop objective; and the boundary statement with the Agentic IAM paper, which resolves this section's open item.

In August 2026, a consumer AI agent booked into a gym class by cancelling a stranger's reservation. It did not break out of anything to do it. It used an API it was legitimately allowed to call, found that the API never checked whose reservation was being cancelled, and noted in its own log that it had tested this on the person at the top of the waitlist — and that it worked [11]. Four months earlier, a frontier model in a security evaluation had done the opposite kind of thing: asked by a simulated user to get a message out of a locked-down environment, it built a multi-step exploit, escaped its container, and emailed a researcher who learned about it over lunch [1].

These are both failures, and they are not the same failure. The second agent reached somewhere it was never supposed to reach: a **containment** failure. The first agent never left the room it was given; the room was simply far bigger than anyone had understood: an **authority** failure. Sandboxing answers the question *can this agent reach a resource*. Bounded authority answers *what is this agent allowed to do once it is there*. The gym incident is what happens when only the first question gets asked — and most of the incidents this paper draws on, including several that made headlines as "escapes," are on inspection failures of the second kind.

This paper's position, reached independently by several reviewers of the blog post it follows [11], is that containment is not a standalone discipline. It is one layer of a larger objective: **an environment in which the agent has bounded authority the way a corporate laptop does.** A well-run corporate laptop is not safe because of any single wall. The employee can reach some systems and not others; what they can *do* on the systems they reach is scoped to their role; unusual behavior is noticed; and when something goes wrong, there are records enough to establish what happened. Nobody calls this "sandboxing the employee." It is several layers, each doing a job the others cannot, and it works because no one layer is asked to do the whole job.

The same decomposition, for agents, runs through this paper:

- **Isolation** — the box around the agent: what it can reach on its host and on the network. This is containment proper, and §2 gives it internal structure along three axes: local, outbound, and inbound.
- **Mediation** — the checkpoint: every consequential action crosses an enforcement point that can say no, expressed in terms of what the action *does*, not just where it goes (§3).
- **Authority** — the grant: what the agent is actually permitted, scoped to whose resources and what limits, carried in its credentials and evaluated per action. This layer is the subject of the WS4 *Agentic Identity and Access Management* paper [9]; this paper takes it as the frame.
- **Accounting** — the fleet view: what a *set* of agents sharing one principal consumes together, which no per-agent control can see (§4).
- **Evidence** — the record: containment that fails loudly, and records sufficient for someone who was not there to reconstruct what happened (§7).

One more piece of shared vocabulary carries through every layer. When a control fails, it fails in one of four ways: the agent **defeated** it (the mechanism broke); the agent **disabled** it (the control was within the agent's own reach); the control was **insufficiently specified** (on, untouched, and wrong); or the control was correct and the agent **used authority it had legitimately been granted**. The gym agent is the fourth. Most of the celebrated incidents are the third or fourth — which matters, because the industry's attention and spending concentrate on the first two. §5 develops this taxonomy; every control in this paper states which failure mode it removes.

**What this paper takes from the IAM paper, and what it leaves there.** It takes the frame — bounded authority as the objective — and two of its principles as given: authority is bound to principal, action, resource, and condition rather than to an endpoint; and delegated authority narrows, never expands, at each hop. It leaves there everything about how identities are issued, authenticated, governed, and revoked. Where §4 of this paper presses on a limit of the per-hop model, it does so explicitly, as an extension. Readers wanting the authority layer in full should read that paper [9]; readers of this one need only the frame.

For the executive who reads no further: the question to put to your teams is not "is this agent sandboxed?" It is the one this paper builds toward — *what would this agent do if it decided to test its limits, and how would we know?* If the answer to *how would we know* is "we wouldn't," nothing else in this paper is working yet.

### 1.1 Deployment shapes and what containment can mean in each

**Answers:** Q3, Q4, Q5. **Raised by:** @imolloy, @skvcool-rgb, @Johncavanaugh-IIS.

Which of the five layers you can actually build depends on where the agent runs and who controls it. Three shapes cover most deployments.

**Built and operated.** The organization runs the agent on infrastructure it controls. Every layer is available, and every requirement in this paper is an engineering requirement.

**Procured and integrated.** The agent arrives inside third-party software, or runs on employee desktops where no container boundary exists at all. Isolation is simply unavailable — there is nothing to put the box around. What survives is exactly as much as you can still interpose at the request layer: mediated tool and MCP calls (§3), bounded and attenuated authority, and accounting across the principal (§4). Where you can interpose nothing — a fully third-party agent — containment is wholly a procurement requirement on the provider, and this paper's requirements should be read as the specification of what to demand, in contracts and in evidence, rather than what to build. The rule throughout: **where the organization controls the principal's authority, the requirement is engineering; where it does not, the identical requirement lands on the provider as procurement.**

**The agent that builds its own boxes.** The coding agent that must create and run containers is a shape in its own right: it has a container boundary, but the workload wants to make more of them, so the question is not whether a boundary exists but what it must look like. Handing such an agent the host's container-runtime socket places the enforcement point inside the agent's reach (§2.1); what a sandbox must demonstrate instead is specified in §8.

Sections that follow are written for the first shape and marked, where the distinction bites, for the second.

**Open items.**
- Per section, mark which requirements are engineering and which become procurement in the procured-and-integrated case.

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

> Drafting note (2026-09-11): first prose draft, by the editor. Two commitments are embedded and open to challenge by PR or comment on #172: the effective-reach invariant is promoted from candidate to this section's normative statement (resolving the open item; credited to @ryjen, with @Levaj2000's receipts refinement), and the "what does the network layer still buy" question is answered with three jobs — closing non-tool paths, backstopping gateway failure, bounding quantity — which is new synthesis, not from the thread. The confused-deputy naming in 3.1 follows @imolloy in #172 and the WS2 Zero Trust paper §3.2.1; the numbered citation lands with the reference consolidation after the open section PRs merge. The x32 case is cited as reported, per Appendix A.1.

Section 2 gave the outbound axis two enforcement points. This section argues that for agent workloads the tool or MCP call — not the network flow — is the primary mediation surface, states the invariant that surface must satisfy, and answers what the network layer still buys once tool-call mediation exists.

**Why the tool call.** A network flow names an endpoint. A tool call names an *action*: a typed operation, with structured arguments, invoked by an attributable principal. Policy can be written against the second in a way it cannot against the first — a named tool call with structured arguments can be authorized, transformed, or refused on its semantics; a TLS stream can only be permitted or blocked on its destination. The blog post's complete-mediation requirement already contains the reason this matters [11]: a reference monitor that answers only *may this agent call this endpoint* still permits the gym cancellation, because the endpoint was permitted and the harm lived in the arguments — whose reservation, not which API. The bound has to reach the authority itself — whose resource, up to what limit — carried in the credential and evaluated per call.

The reference monitor at this surface is the tool or MCP gateway, and the §5 properties apply to it in full: complete mediation over the actions it claims to govern, placement outside the agent's reach, and records sufficient to verify both (§7). The per-tool half of the same position is already CoSAI guidance: the secure tool design practical guide requires that the tool, not the model, enforce security-critical constraints — this section supplies the layer above it, the monitor through which every tool passes. The MCP Security paper's Sandboxing and Isolation and Logging controls specify the how at this surface [10]; this section states what they must jointly achieve, and does not restate them.

**The effective-reach invariant.** What the mediation surface must achieve is stated as an invariant over **effective reach**. For any consequential effect, the agent's effective reach is the union of every path through which it can cause that effect:

- direct network or API access from its runtime;
- mediated tool and MCP invocation;
- gateway- and provider-side fetches and execution performed on its request (§3.1);
- delegated agents or services acting on its behalf (§4);
- alternate endpoints, credentials, or registries that produce the same result.

**The invariant: every path capable of producing an equivalent consequential effect MUST cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary.**

The consequence that gives the invariant teeth: a correctly mediated tool call is not sufficient while the same effect remains reachable through raw credentials, an unrestricted network path, an alternate server, or a provider-side capability. Mediation of *a* path is not mediation of *the effect*. Containment claims are claims about effects, and the honest form of a partial claim is the exclusion clause — stating which paths the assurance boundary does not cover — rather than silence. Per decision, that clause is recorded as the assurance-boundary statement row in §7.1, identified by content digest: it records the claimed scope, and it does not prove enforcement.

One corollary the invariant forces, because agent systems increasingly pass receipts, traces, and completed results between components: **prior evidence never becomes executable authority for the final effect.** A receipt may authorize skipping duplicate work within a single claimed assurance boundary; it may never substitute for a mediation step that boundary claims to enforce. Where a receipt is relied on to skip work, the reliance is recorded — naming the receipt by digest and the boundary it was accepted under. The evidence contract of §7 depends on the same discipline from the other side: nothing in an evidence record may be presentable to an enforcement point to obtain the effect, or to satisfy a mediation step, again. Replay for verification stays in bounds; replay for authority does not.

**What the network layer still buys.** Tool-call mediation does not retire egress control; it changes its job. Three things the network layer does that the gateway cannot:

1. **It closes the non-tool paths.** The gateway sees only what presents itself as a tool call. Generated code opening a raw socket, a runtime's own update check, a library's telemetry — none of these crosses the gateway, and the invariant requires that they cross *something*. Deny-by-default egress is what converts "every path" from an unwinnable enumeration into an allowlist: any path not forced through the gateway is removed at the network layer.
2. **It backstops the gateway's own failure.** If the gateway is defeated, disabled, or under-specified (§5 modes 1–3), the network boundary is the layer that still bounds where the effect can land — which is §6's subject.
3. **It bounds quantity.** Bandwidth, destination-count, and rate limits at the network layer cap what a permitted channel can move even when the channel is being abused (§3.1), and they are enforcement points for the aggregate quantities §4 accounts.

What the network layer cannot express is the authority semantics: whose resource, which action, up to what limit. Endpoint-granularity policy permits the gym cancellation forever. Each of the three jobs above is evidentiary as well as enforcing: the network layer's records — which paths were closed, where the boundary held while the gateway was impaired, what quantities moved — are what let §7 check the assurance-boundary statement's exclusion claims after the fact. The two layers answer different questions — *which endpoints* and *what may happen* (§2.2) — and the invariant needs both held at once.

### 3.1 The permitted channel is the exfiltration path

**Answers:** Q9, Q10. **Raised by:** @imolloy, @getglad.

Effective reach includes every fetch a permitted party will perform on the agent's request. Model-side URL retrieval, web search, code interpreters, retrieval connectors — each is network access the agent holds indirectly, and the agent's egress envelope is the union of its own network policy and all of them. A sandbox audit that stops at the workload's own network policy has measured the smaller of the two terms.

The anchor case, cited as reported pending Appendix A.1: in testing across nine frontier models against a hardened sandbox, agents that discovered the x32 seccomp bypass chained it with the LLM API's own built-in URL retrieval to reach external destinations through an otherwise restricted proxy [11]. The only permitted network channel — the inference endpoint itself — became the relay. In §5's terms this second half is mode 4: no control was defeated; a trusted party, outside the sandbox, holding network access the agent lacked, performed a fetch with a payload the agent controlled. It is a confused-deputy problem, and its structure — the deputy is legitimate, the request is well-formed, the authority is real — is the same structure as the gym incident, one layer down.

The design principle that follows, and this paper states it as one: **where a permitted party will act on the agent's behalf, constrain what it will do — not just whether the agent may ask.** Method-limited channels (a retriever that will only GET), bandwidth- and rate-limited channels, and non-reflective channels (the response returns to the requester, not to a destination the payload names) bound exfiltration even where the channel cannot be removed. These constraints are also what makes the channel accountable in §4's terms: a provider fetch that carries no quantity limits is consumption the accounting authority never sees.

Where the permitted party is a provider the organization does not operate, the constraint is procurement rather than engineering (§1.1): the capability's controls — method, destination, rate — are what to demand, and absent them the capability's full reach counts inside the agent's envelope, because nothing else bounds it.

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
  is refused or held for confirmation, never allowed. Continuous accounting without a fail-safe
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

**Requirements across §7.** An absence that was determined MUST be distinguishable in the record
from an absence that was never established. A determined absence carries an explicit value and
reason; missing visibility or incomplete observation is recorded as `not_established`, with the
missing premise. An omitted field establishes neither absence nor a negative finding.

The observation states are `present` (established), `absent` (absence determined),
`not_established` (the observation could not be established), and `pending` (an
outcome is not yet known). An unknown action outcome is `pending`; it does not
become `not_established` when the reporting window ends. Report that pending
outcome as "not verified by the end of the window", with the window duration.

> Drafting note: §7.2–7.3 and the §7.1 signal qualifications implement the [editor's acceptance on #172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172#issuecomment-5698789739). The explicit-absence and actor/subject requirements implement the [additional rulings on #184](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/184#issuecomment-5704988996) and [provenance enum ruling](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/184#issuecomment-5705703733). These editorial commitments remain open to challenge on #172.

### 7.1 What to log

Two approved WS4 papers already carry most of the field list, and this section should be read as
extending them rather than restarting them. The *Model Context Protocol Security* paper requires,
at L2 and above, structured logging of tool identity, caller identity, policy decision, resource
target, outcome, request metadata and correlation identifiers, with raw parameters logged only
after redaction, hashing or field-level tokenization, rising to immutable tamper-evident logging of
all interactions at L4. The *Agentic Identity and Access Management* paper's Appendix D requires
agent ID, subject ID, tenant, environment, resource and action, decision with reason, scope and
authorization details, policy version, attestation information and a `correlation_id`, and states
the "prove control on demand" obligation: an organization must be able to answer, from logs alone,
which agents were active, what permissions they held at that time, who was involved in each action,
and which policies, attestation evidence and delegated scopes justified each decision.

What this paper adds is the separation. Those lists are single lists serving two readers. Detection
is written for an operator inside the deployment who is trying to notice an attempt in progress, and
it is allowed to be noisy, heuristic and tuned locally. Evidence is written for someone who was not
there and does not trust the operator, and it must be stable, complete and dull. A field that earns
its place in one does not automatically earn its place in the other, and the two have opposite
failure modes: a detection signal that fires too rarely is useless, while an evidence field that is
present only sometimes is worse than absent, because a verifier cannot distinguish "did not happen"
from "was not recorded".

Two constraints apply to the evidence table as a whole. Nothing in an evidence record may be
executable authority (§3): the record states what was decided and on what basis, and a consumer of
the record must never be able to replay a field in it to obtain the decision again. And correlation
is scoped to the shared principal and the delegation subtree it roots, not to one run or one
container (§4); a per-run correlation key cannot show that a set of individually compliant agents
collectively exceeded the intended authority or budget, which is the failure §4 describes.

**Detection signals.** Each row names what the signal is evidence of and where its false positives
come from. §7.2 takes up why the rates themselves cannot be stated yet.

| Signal | What it indicates | Expected false-positive source |
| :---- | :---- | :---- |
| Denied syscalls under the sandbox policy | The workload attempted something the profile forbids | Language runtimes and package managers probe for capabilities they can live without; a denied `clone3` or `statx` is routine startup behaviour on a mismatched libc |
| Repeated policy violations by one agent instance | Systematic probing rather than an incidental denial | A misconfigured tool retrying a legitimately scoped call; retry loops inflate one denial into many |
| `/proc` and cgroup inspection | Sandbox reconnaissance | Ordinary resource introspection: runtimes read `/proc/self/cgroup` and memory limits to size thread pools and heaps |
| Container runtime socket access | Possible access to the host control plane; severity depends on which runtime the socket controls | A build or CI agent may legitimately use a runtime socket in its deployment shape (§1.1). Treat unexpected host-socket access as a high-severity investigation trigger; its false-positive rate and comparative confidence require a deployment-specific baseline |
| Cloud metadata service probes | Attempted credential theft | SDK default credential chains probe the metadata endpoint unconditionally on startup, before any application code decides how to authenticate |
| Blocked DNS resolution and blocked egress destinations | Exfiltration or command-and-control attempt | Telemetry, update checks and dependency resolution reaching destinations nobody put on the allowlist |
| Credential-broker denials | A request for authority beyond the granted scope | An agent legitimately discovering the boundary of its own scope, which is indistinguishable at the broker from probing it |
| Attempted modification of sandbox configuration | Possible self-escalation; assess the caller's authority and the targeted control | Authorized provisioning or maintenance may change configuration. Unexpected agent-originated changes warrant investigation; the false-positive profile depends on the deployment and has not been measured here |
| Attempted or observed aggregate consumption across the delegation subtree crossing the applicable budget | A consumption refused or held by the accounting authority is a preventive-control event; an observed excess is evidence of a control failure (§4) | Legitimate fan-out can produce high consumption within budget or a refused over-budget attempt without malicious intent. Distinguish those cases from an observed excess; the profile depends on the deployment's task and fan-out shape |
| Executed capability outside the agent's declared set | The discriminator named in §7.2: undeclared-but-executed | An incomplete or stale declaration, which is a defect in the declaration rather than noise in the signal |

**The evidence contract.** These are the fields that let a party who was not present and does not
trust the operator reconstruct what happened. Each is REQUIRED unless the row says otherwise. The
mapping to concrete schema fields belongs in the practical guide, pinned to an OCSF version, with
proposed fields marked as proposed.

| Field | What it makes reconstructible | Notes |
| :---- | :---- | :---- |
| Principal and full delegation chain | Who the action was ultimately performed for, and by what path of authority | The integrity-protected correlation key. Scoped to the subtree, not the run, per §4. The whole chain, because the immediate caller alone cannot show that attenuation held at every hop |
| Actor identity (`actor_id`) and establishment provenance | Which agent executed the action and how that identity was established | Required separately from the subject. A connection credential may identify one agent across many requests; it does not establish the principal for each request. Use the closed provenance enum below and preserve the verification outcome |
| Subject identity (`subject_id`) and establishment provenance | The principal on whose authority this request was made, as distinct from the executing agent | Required per request, with the claim's verification outcome and binding to the action. This is §4's accounting principal; an agent-asserted value or a signature alone does not establish that authority. Apply the explicit-absence rule independently to actor and subject |
| Policy version | Which rules were in force at the moment of decision | Identified by a content digest of the policy as it was in force at the decision, not by a label: a label can stay unchanged while the rules behind it change. Without it a later reader evaluates the action against today's policy and reaches a different verdict than the enforcement point did |
| Assurance-boundary statement | Which paths the containment claim covered, and which it excluded, at the moment of decision | Identified by a content digest of the statement as it stood at the decision, for the same reason as policy version: the paths a claim covers can change while its name does not. It sits beside policy version because the two answer different questions: the policy says what was allowed, the boundary statement says on which paths that was enforced and, per the exclusion clause in §3, which paths the claim does not cover. It records the claimed scope; it does not prove enforcement, and a reader must not treat an excluded path as closed or an included path as mediated on the strength of this row alone |
| Tool-catalog version | What the agent could have called at that moment | Distinct from policy version and separately mutable. Identified by a content digest of the catalog as the agent saw it at that invocation, since a server-side catalog can change a tool's description or schema under an unchanged version string. Required for the declared-versus-executed discriminator in §7.2 to be checkable after the fact |
| Action or tool-call identifier | Which specific invocation this record is about | The join key between the detection artifact, the evidence artifact and any downstream effect |
| Request digest | That the recorded request is the request that was made | A digest rather than the parameters, so the record can be retained and shared without carrying the payload. The digest covers the request as it was made, before any redaction, and the record states which fields it covers alongside the canonicalization; two records that digest different fields are incomparable even under the same canonicalization. Where parameters are guessable, a bare digest can permit recovery by enumeration. Use a keyed commitment with a separately protected secret and identify the scheme in the record; a public salt alone does not prevent guessing. Payload redaction and access to commitment verification remain separate controls |
| Enforcement decision and reason | What the enforcement point concluded, and on what basis | Both halves. A decision without a reason cannot be audited, only counted. The decision record is committed to the integrity-protected sequence before the action is dispatched; the outcome is appended later as its own entry that references the decision. Ordered this way, a crash between the effect and the write leaves a decision with no outcome, which the record can show, instead of an effect with no record, which it cannot |
| Runtime identity or attestation reference | What was executing, as opposed to what claimed to be executing | Required. Where attestation is not available in the deployment shape (§1.1), the field carries an explicit `not-available` value with a reason rather than being omitted. An explicit absence is evidence; an empty field is a shrug |
| Outcome | Whether the action took effect | Distinct from the decision: an allowed action can still fail, and a refused one can still have partial effect. Recorded as a later entry that references the decision it resolves. A decision whose outcome entry is missing has an unknown outcome, and stays unknown until an outcome is recorded; it is not read as success, and per §4 it remains charged |
| Integrity-protected sequence with trusted checkpoints | Ordering and detectable gaps within a declared record sequence | Verification needs expected sequence boundaries and trusted checkpoints. A completeness claim also needs a declared collection scope and accounting for actions omitted before recording. A timestamp alone does not establish completeness. |
| The accounting decision | What the aggregate budget stood at, and what was reserved, committed, released or reconciled for this action | Per §4, record the accounting authority's decision and reason, the principal and subtree, applicable budget, aggregate consumed and remaining, and reservation/action references. Preserve refused or held attempts even when no consumption follows. An unknown outcome remains charged until authoritative non-consumption or idempotent reconciliation; post-hoc totals do not establish atomic enforcement |

Where the accounting authority is also the enforcement point for an action, its
accounting decision is that enforcement decision: one record can satisfy both
rows. Where the authorities or decisions differ, preserve each decision and its
relationship to the same action.

**Identity provenance and verification.** Each identity carries one of the closed provenance values
`connection-credential`, `signed-request-claim`, `unsigned-request-claim`, or `absent`. The last means
absence was determined; it must not stand for a collection failure. If provenance could not be
established, record `not_established` as the observation status with its reason, rather than
inventing a fifth provenance value or labeling the identity `absent`.

Provenance describes the source of a claim, not its verification result. A signed request claim
may still be unchecked or rejected; record that outcome separately, including the verifying
authority and request binding where established. An unsigned claim can record what was asserted,
but does not establish the asserted subject's authority. Do not collapse an unregistered signing
key and a bad signature into the same verification reason.

An unverifiable subject claim in this evidence record MUST NOT change the egress decision in
either direction; it changes only what the record may claim. Treating it as permission rewards
forgery; treating an evidence-verification failure as a new denial can turn a key-rotation error
into an outage. This does not bypass the independently enforced authorization and accounting
requirements in §§3–4: recording a claim cannot satisfy a required authorization check.

Coverage of the *Agentic IAM* paper's "prove control on demand" checklist follows from the table
rather than being asserted: which agents were active comes from actor identities and the chain, what
permissions they held from the policy and catalog versions, who was involved in each action from the
actor, subject, their provenance and the action identifier, and what justified each decision from the decision, reason and
attestation reference. The obligation that paper states as a capability, this table states as the
minimum record that makes the capability real.

**Two requirements this section settles.**

- **The runtime identity or attestation reference row is required, not conditional.** Attestation is
  not available in every deployment shape (§1.1), but a conditional evidence field is exactly the
  shape that produces the "did not happen" versus "was not recorded" ambiguity this section exists to
  remove. The field is therefore always present and carries an explicit `not-available` value with a
  reason where attestation is unavailable. When unavailability is established,
  `not-available` is this field's explicit value for the `absent` observation
  state, not a fifth state. Inability to establish availability remains
  `not_established`, with its missing premise.
- **An implementation MUST state which canonicalization its digests use, and the record MUST
  identify it.** Two implementations that digest the same request differently produce records that
  cannot be compared, which defeats the field. The paper requires that a canonicalization be stated
  and identified, so two records are either comparable or honestly incomparable; which
  canonicalizations qualify is practical-guide material, pinned alongside the OCSF mapping.

### 7.2 The false-positive profile

The signals in §7.1 need a baseline for the deployment in which they are used. Filesystem exploration, credential discovery and retries can occur during legitimate work. Their frequency depends on the runtime, available tools, assigned tasks and deployment shape (§1.1). This draft has no measured baseline spanning those conditions. The expected false-positive sources in §7.1 are hypotheses to test; they do not establish rates or comparative detector confidence.

**Compare execution with the authority in force.** For exploration-like behavior, compare the observed invocation with the capability declaration, policy and tool-catalog versions applicable at that invocation. Keep the declaration's source, scope and effective interval available to the reviewer. A declaration generated after the action cannot establish what was declared beforehand.

Executed capability outside the declared set is a discrepancy requiring investigation. It can reflect an unauthorized path or an incomplete declaration. Execution inside the declared set can still misuse an allowed capability, exceed an argument constraint or contribute to an aggregate-budget violation. Declaration membership alone therefore establishes neither authorization nor benign intent. A blocked request establishes an attempted action and an enforcement decision; it does not establish successful execution or the absence of partial effects.

If the applicable declaration, version binding or execution evidence is unavailable, report the comparison as not established, with the missing premise. Do not classify it as a match or as a benign example for tuning. Keep malformed records and unsupported mappings separately visible as processing failures.

**Measure the profile without using the alert as its own label.** Each detector evaluation should identify:

- The deployment shape, task mix, runtime and model versions, policy and catalog revisions, detector version and threshold, and observation window.
- The unit being classified: an invocation, a logical action with retries, or a correlated sequence. Preserve attempt identifiers even when one incident groups several attempts.
- How benign and violating cases were adjudicated, using the applicable policy and outcome evidence. Keep unresolved cases separate; a detector firing is not sufficient to label its input as a violation.
- The counts behind every reported rate and the known collection gaps. Report results by deployment shape before combining them.

For a declared unit, the false-positive rate is alerted adjudicated-benign units divided by all adjudicated-benign units. The fraction of adjudicated alerts that were benign answers a different question: the review burden among alerts. Report both denominators (all adjudicated-benign units and all adjudicated alerts), the unresolved-label count and any sampling or selection limits. A zero denominator yields no rate. A dataset assembled only from alerts cannot measure the false-positive rate or missed detections. Detector tuning and evaluation must use separately identified data so a tuned threshold is not presented as an independent result.

**Correlate across the authority being constrained.** Use the principal, full delegation lineage and action identifiers from §7.1 to join runs and descendants. State identity namespaces and the observation window; identical text identifiers from different tenants or authorities do not establish a join. Deduplicate repeated delivery of the same event while retaining distinct attempts and conflicting versions. A missing lineage link or collection interval limits the resulting subtree claim.

Use §4's distinction for aggregate accounting. A consumption refused or held because it would exceed the budget is a preventive-control event. Consumption observed above the applicable budget is evidence of a control failure. High consumption within that budget can be legitimate. Reconstruct reservations, commits, releases and reconciliations using the accounting authority's decision records; an unknown action outcome remains charged under §4 and must not be treated as a harmless timeout. Post-hoc correlation can detect a failure, but cannot supply the atomic decision required at the consuming action.

Alert thresholds and grouping may be tuned to reduce operational noise. That tuning must not discard the evidence needed to reconstruct the decision, invocation and outcome under §7.1. The collection and retention policy should make any sampling or loss explicit, so a quiet detector does not become a claim of complete observation.

### 7.3 Measuring containment

A containment measurement must name what was contained. Its scope can be one process, an agent instance, a delegation subtree, a credential set or specified provider-mediated actions (§3). State the affected authority and reachable systems, including queued work and delegated actions that may survive the initiating process. A local process stopping does not establish that its children, credentials or remote requests have stopped producing effects.

**Separate detection, response and verification.** Record these milestones with the supporting event identifiers:

| Milestone | Meaning and required evidence |
| :---- | :---- |
| Indicator | Earliest observed event satisfying the stated detector criterion in the declared observation window. Preserve event time and collection time separately. |
| Detection | Time the detector emitted the alert, with its version, criterion and input references. |
| Response request | Time an operator or automated control requested containment, identifying the initiator, target scope and requested action. |
| Enforcement acknowledgment | Time each relevant enforcement point acknowledged applying that action. An acknowledgment alone may not establish its effect. |
| Verification | Time the last required check established the stated containment condition across the declared scope, with outstanding effects, exceptions and unavailable checks recorded. |

The indicator milestone is an observable starting point, not necessarily the first malicious action. If collection started late or lacks coverage, state that limitation. A retrospective criterion may identify earlier events, but it must be labeled as retrospective and must not replace the detector version used in the live measurement.

Report indicator-to-alert latency, alert-to-response latency and response-to-verification latency separately where both endpoints are recorded. For this paper, **verified time-to-contain** is the interval from the indicator milestone to verification of the declared containment condition. Also report time to a local stop when useful, labeled with its narrower scope. A stop acknowledgment must not substitute for the verification endpoint.

Define the verification checks for the claimed boundary. For example, a subtree claim may require blocked new invocations, descendant authority revocation and disposition of already accepted work at the affected providers. The report must distinguish preventing future effects from reversing effects that have already occurred. A refused test request can support a check on one route; it cannot alone establish that every effective route is blocked. Claims based on no further observed activity require collection coverage for the named scope and interval, including sequence boundaries and actions that could be omitted before recording (§7.1).

**Preserve unresolved outcomes.** If a required enforcement point is unreachable, a descendant cannot be accounted for or a provider's pending action has an unknown outcome, containment of that scope is not established. Record verified subscopes and the unresolved remainder. If the observation window ends first, report “not verified by the end of the window” and its duration; do not enter zero, use the last received log as completion or omit the case from the denominator. Reports of completed cases should state the total eligible cases, completed cases, unresolved cases and exclusions. A single average over completed cases hides the failures to complete.

Each timestamp must identify its clock source and relevant uncertainty. Use a common clock or a documented relationship between clocks before subtracting times across systems. Where bounded clock error permits only an interval, report that interval. Where ordering cannot be established, report the duration as unknown. Event sequence can establish some ordering without establishing elapsed time; collection time measures observation delay and must remain distinguishable from event time.

**Record why execution stopped.** Preserve a normalized reason distinguishing an operator-requested containment action, an automated policy response, ordinary completion, a crash and an unknown reason. Record the native reason alongside its mapping and version. A model turn ending, reaching a token limit or yielding to a tool is not sufficient evidence that the agent's authority ended. Correlate stop records, enforcement actions and per-invocation outcomes by agent instance and action identifiers; do not infer a tool's outcome from the model's stop reason.

The accounting verdict (`allowed`, `refused` or `held`) records the accounting
authority's decision; the stop reason records why execution stopped. Keep both
when applicable. A `held` verdict awaits confirmation of the same action; a
containment response request initiates containment of the named scope. Neither
field substitutes for the other. An unknown stop reason can accompany a verified
outcome, and a known stop reason can leave the outcome `pending`.

The practical guide should bind these concepts to the selected OCSF revision and coordinate any schema gaps with the WS2 telemetry work. This section defines the information needed for the measurement without assuming that one existing stop-reason field represents all of it. Evidence of an earlier decision remains evidence; it must not authorize replay or bypass a mediation step (§3).

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
