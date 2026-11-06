---
title: "Agent Containment: From Sandboxing to Bounded Authority"
author: "Workstream 4: Secure Design Patterns for Agentic Systems"
date: 2026-10-07
version: 0.3-draft
status: "Working draft, all sections drafted. Not reviewed, not approved."
---

# Agent Containment: From Sandboxing to Bounded Authority

**Status:** Working draft. Not reviewed or approved.

# Table of contents

- [Abstract](#abstract)
  - [Scope](#scope)
  - [Out of scope](#out-of-scope)
  - [Target audience](#target-audience)
- [1. Introduction: from sandboxing to bounded authority](#1-introduction-from-sandboxing-to-bounded-authority)
  - [1.1 Deployment shapes and what containment can mean in each](#11-deployment-shapes-and-what-containment-can-mean-in-each)
- [2. The three hardening axes](#2-the-three-hardening-axes)
  - [2.1 Local](#21-local)
  - [2.2 Outbound](#22-outbound)
  - [2.3 Inbound](#23-inbound)
  - [2.4 The axes at a glance](#24-the-axes-at-a-glance)
- [3. Mediation: the tool call, not the network flow](#3-mediation-the-tool-call-not-the-network-flow)
  - [3.1 The permitted channel is the exfiltration path](#31-the-permitted-channel-is-the-exfiltration-path)
- [4. Composition: per-sandbox controls across a set of agents](#4-composition-per-sandbox-controls-across-a-set-of-agents)
  - [4.1 The failure shape](#41-the-failure-shape)
  - [4.2 The closing control: aggregate accounting at the consuming action](#42-the-closing-control-aggregate-accounting-at-the-consuming-action)
  - [4.3 The hard sub-problem: the accounting authority](#43-the-hard-sub-problem-the-accounting-authority)
  - [4.4 Prior art: colluding applications](#44-prior-art-colluding-applications)
- [5. The enforcement property and four failure modes](#5-the-enforcement-property-and-four-failure-modes)
  - [5.1 The property, named](#51-the-property-named)
  - [5.2 The four failure modes](#52-the-four-failure-modes)
  - [5.3 Why the distinction matters](#53-why-the-distinction-matters)
  - [5.4 Threat sources and trust assumptions](#54-threat-sources-and-trust-assumptions)
- [6. Reachability and blast radius](#6-reachability-and-blast-radius)
  - [6.1 Patching and reachability address different risks](#61-patching-and-reachability-address-different-risks)
  - [6.2 Which reachable systems are yours](#62-which-reachable-systems-are-yours)
  - [6.3 System control and evidence](#63-system-control-and-evidence)
- [7. Detection and evidence](#7-detection-and-evidence)
  - [7.1 What to log](#71-what-to-log)
  - [7.2 The false-positive profile](#72-the-false-positive-profile)
  - [7.3 Measuring containment](#73-measuring-containment)
  - [7.4 Evidence sufficiency for absence claims](#74-evidence-sufficiency-for-absence-claims)
- [8. A vetted-sandbox commons](#8-a-vetted-sandbox-commons)
  - [8.1 What already exists, and what it does not cover](#81-what-already-exists-and-what-it-does-not-cover)
  - [8.2 The demonstration requirement](#82-the-demonstration-requirement)
  - [8.3 A worked criterion: container-runtime access](#83-a-worked-criterion-container-runtime-access)
  - [8.4 What CoSAI should do with this](#84-what-cosai-should-do-with-this)
- [9. Positions](#9-positions)
  - [9.1 Agent trajectory formats are not the evidence record](#91-agent-trajectory-formats-are-not-the-evidence-record)
  - [9.2 Multi-agent jailbreaking: the technique is out of scope, the containment consequence is not](#92-multi-agent-jailbreaking-the-technique-is-out-of-scope-the-containment-consequence-is-not)
  - [9.3 Items deliberately not taken](#93-items-deliberately-not-taken)
- [10. Takeaways and conclusion](#10-takeaways-and-conclusion)
- [11. References](#11-references)
- [12. Contributors and acknowledgements](#12-contributors-and-acknowledgements)
- [Appendix A. Evidence receipts](#appendix-a-evidence-receipts)
- [Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright](#appendix-b-cosai-focus-ai-usage-guidelines-disclaimer-copyright)

---

## Abstract

An agent does not have to escape its sandbox to cause harm. It can misuse a permitted tool, act on resources it should not control, or spread work across other agents until individually acceptable actions exceed a shared limit. The sandbox may hold while the deployment fails.

This paper examines what it takes to bound that behavior. It brings together isolation, mediation, authority, accounting and evidence, distinguishing controls that are defeated, disabled or insufficiently specified from harmful actions taken within permitted authority. The distinction determines the remedy: stronger isolation cannot repair an over-broad grant, and per-agent limits cannot govern what agents consume together.

The paper sets out how consequential actions must be mediated, shared budgets accounted for, and failures detected and investigated. It distinguishes an alert from evidence that supports a claim, an established absence from missing visibility, and a local stop from verified containment. It also describes what deployed controls must demonstrate before and during operation, with corresponding requirements on providers where organizations cannot enforce the controls themselves.

The aim is to give practitioners a basis for answering two questions: **what limits this agent's actions, and what evidence shows those limits held?**

### Scope

This paper addresses containment for autonomous agents with access to real systems and resources. It examines where their boundaries are enforced, how controls apply across agents acting under shared authority, and how different failures call for different remedies. It also sets out the evidence and measurements needed to investigate failures and verify containment, whether the relevant controls are operated by the deploying organization or supplied by a provider.

### Out of scope

- **Authorization beyond containment's needs.** This paper uses bounded authority as its framework. The broader treatment of authorization remains with the *Agentic Identity and Access Management* paper [9].
- **Model-level safety training and refusals.** This paper assumes a model that wants to escape; it does not specify how to train the model or shape its refusal behavior.
- **Runtime-isolation implementation instructions.** The runtime-isolation practical guide explains how to build the controls. This paper states what those controls need to achieve and why.

### Target audience

This paper is for practitioners and architects responsible for deploying agents with production access, and for security leaders assessing the controls and evidence those deployments require. It addresses both organizations operating agents themselves and those relying on providers.

---

## 1. Introduction: from sandboxing to bounded authority

Two agents can cause trouble in very different ways. ABC reported a user's account of an AI assistant removing another person's place on a gym-class waitlist to move its user closer to the front [19]. The agent's own messages attributed this to missing authorization checks in the booking API. In a separate evaluation, Anthropic reported that a model instructed to escape a sandbox computer developed a multi-step exploit and sent an email to the researcher running the test [1]. The model escaped that sandbox, not the separate system running the model itself; Anthropic explicitly states that this was not a full escape from containment.

The first account concerns what an agent could do through a service it could reach. The second concerns a boundary intended to restrict its reach. These problems call for different controls. Isolation limits which systems and resources an agent can reach; authority limits the actions it may take on those resources. An accessible API is not permission to act on every record behind it. A deployment needs both boundaries: one around reach, and another around the actions available within it.

Containment is one layer of a larger objective: bounded authority. A well-managed corporate laptop offers a useful comparison. An employee can reach some systems but not others, and their permissions limit what they can do once connected. Unusual activity is monitored, and records support investigation when something goes wrong. Nobody calls this "sandboxing the employee." Each layer does a different job. Agent deployments need the same separation of responsibilities, rather than expecting isolation to do everything.

For agents, these responsibilities fall into five layers:

- **Isolation** limits what the agent can reach on its host and on the network. This is containment proper; §2 examines its local, outbound and inbound axes.
- **Mediation** puts an enforcement point before every consequential action. The decision concerns what the action does, not just where the request goes (§3).
- **Authority** defines what the agent is permitted to do, on whose resources and within which limits. It is carried in credentials and evaluated for each action. The *Agentic Identity and Access Management* paper [9] provides this framework.
- **Accounting** tracks what agents sharing one principal consume together. Per-agent controls alone cannot establish that aggregate view (§4).
- **Evidence** makes containment failures visible and provides records sufficient for someone who was not present to reconstruct what happened (§7).

Across these layers, the paper distinguishes four failure modes. The agent **defeated** the control because its mechanism broke; the agent **disabled** the control because it could alter it; the control was **insufficiently specified**, remaining active and untouched but enforcing the wrong boundary; or the control worked correctly and the agent **used authority it had legitimately been granted**. These distinctions matter because the remedies are different. Section 5 develops the four modes; throughout the paper, each control states which failure mode it removes.

**Relationship to Agentic Identity and Access Management.** The *Agentic Identity and Access Management* paper [9] supplies the authority framework: permission depends on the principal, action, resource and conditions, not simply on access to an endpoint. For orchestrators delegating to sub-agents, its rule is precise: scope "SHOULD narrow at each hop and MUST NOT expand beyond the delegating principal's effective permissions." Narrowing is recommended; expansion beyond the delegator's permissions is prohibited.

Identity issuance, authentication, governance and revocation remain with that paper. Section 4 extends the per-hop model by addressing what agents sharing one principal consume together. It adds aggregate accounting without replacing the underlying delegation rules.

The *Zero Trust for AI Systems* paper [16] defines where identity, delegation and policy decision points sit relative to the AI Threat Boundary. It identifies agent containment and isolation as topics for a separate publication. This paper develops that containment layer: how to constrain an agent's reach and actions, and how to establish what those controls achieved.

For leaders assessing an agent deployment, "is it sandboxed?" is only the starting point. The more revealing question is: *What would this agent do if it decided to test its limits, and how would we know?* If the second question cannot be answered, the organization cannot establish whether the controls held or what happened when they did not.

Section 5.4 collects the assumptions behind each layer: the threats it addresses, the components it relies on, the properties those components must hold, and the limits of its claims.

### 1.1 Deployment shapes and what containment can mean in each

Where an agent runs, and who controls its environment and authority, determines which controls an organization can implement itself and which it must require from a provider. This paper considers three deployment shapes.

**Built and operated.** The organization runs the agent on infrastructure it controls. All five layers are available to implement, and the requirements in this paper apply as engineering responsibilities.

**Procured and integrated.** The agent is supplied as third-party software, runs on employee desktops, or is operated by a provider. These arrangements do not by themselves determine whether isolation is available or who operates it. The relevant distinction is which controls the organization can implement itself and which it must require from the provider.

Where the organization can interpose at the request layer, it can mediate tool and MCP calls (§3), bound and attenuate authority, and account for consumption across agents sharing a principal (§4). For controls it cannot operate itself, the corresponding requirements become procurement obligations: specify what the provider must implement and what evidence it must supply. Where the organization cannot interpose any controls, those requirements fall wholly on the provider.

Engineering and procurement responsibilities can coexist in one deployment. The underlying requirements remain the same; responsibility for implementing and demonstrating them follows actual control.

**Agents that create containers.** A coding agent may have a container boundary while also needing to create and run additional containers. The design question is how to support that work while keeping the enforcement point outside the agent's reach. Giving the agent access to the host's container-runtime socket places that enforcement point within reach (§2.1). Section 8 specifies what a sandbox supporting this workload must demonstrate.

The following sections use the built-and-operated deployment as their starting point. Where the distinction affects a requirement, they identify what changes for procured and integrated deployments, including the division between engineering and procurement responsibilities.

---

## 2. The three hardening axes

The three hardening axes describe the direction in which influence travels:

- **Local:** the agent must not affect the host beyond what is intended.
- **Outbound:** the agent must not affect systems remote to the host beyond what is intended.
- **Inbound:** the agent must not be influenced by unintended external signals, whether they originate on the host or remotely.

Each axis has its own enforcement point, property to uphold and ways of failing. Keeping them separate makes uneven protection visible: a deployment can be hardened on one axis and exposed on another.

The axes help identify which controls a deployment needs and where existing guidance applies. The MCP runtime isolation guide [8] provides implementation instructions for runtime controls. The *AI Threat Boundary* in *Zero Trust for AI Systems* [16] identifies model and data-pipeline components that must be treated as untrusted. The axes address a different question: how to constrain effects on the host, actions against remote systems, and influence from incoming content. The two views complement each other; neither replaces the other.

### 2.1 Local

Local controls are enforced at the operating-system boundary around the agent's process. They use namespaces, filesystem policy, syscall filtering and mandatory access control. Where the workload warrants stronger isolation, the design includes a userspace kernel or microVM beneath the container.

The kernel or its stand-in acts as the reference monitor. It must meet the three properties described in §5: every host-facing action is mediated, the policy remains outside the agent's write scope, and enforcement is verifiable.

Local hardening relies on OS-enforced isolation, not instructions asking the agent to stay within bounds. Privilege minimization works in both directions: block escalation paths, including access to the host's Docker socket and metadata services, and reduce default authority to limit what a compromise can do. Where a shared kernel is insufficient for the workload, apply progressively stronger isolation.

The coding agent that needs to build and run containers (§1.1) tests this boundary. Exposing the host's privileged container-runtime socket inside the sandbox gives the agent an API for privileged host actions. It puts the enforcement point within the agent's reach, a §5 mode-2 condition, rather than keeping it outside.

The answer is a control design, not a blanket prohibition on creating containers. Options include a rootless engine inside the sandbox or a runtime backed by its own isolation layer. These are implementation options, not proof of containment: the resulting boundary must satisfy the enforcement properties in §5 and meet the demonstrations specified in §8.

### 2.2 Outbound

Outbound controls have two enforcement points with different jobs:

- The **network egress boundary**, using mechanisms such as a proxy, allowlist or DNS policy, determines which endpoints the workload may reach.
- The **tool or MCP gateway** governs what the agent may cause to happen, through typed operations attributable to a principal.

For agent workloads, §3 treats the gateway as the primary mediation surface and explains the continuing role of the network boundary.

Both enforcement points must uphold the **effective-reach invariant**. Effective reach is the union of every path through which the agent can cause an external effect, including fetches a provider performs on its request (§3.1). Section 3 states the full rule:

> every path capable of producing an equivalent consequential effect MUST cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary.

An exclusion limits the assurance claim; it does not close the path or establish that it is safe.

Outbound hardening combines egress controls, protected credentials, complete mediation and bounded delegation. Treat every permitted channel, including the inference endpoint, as a potential exfiltration path. Use a credential-injecting proxy so credentials never enter the agent's reach, and use short-lived, task-scoped credentials with circuit breakers. Outbound authority depends both on what the agent holds and on what it can reach.

The controls above apply to individual agents. Operators also need to account for bytes, destinations and spend across the set of agents sharing a principal. A per-agent control does not provide that aggregate view. Section 4 addresses this shared-principal accounting.

### 2.3 Inbound

Inbound controls address content entering the agent's context, including prompt injection. The focus is not the agent crossing into another resource, but information crossing into its context. The required property is that content from an untrusted source never acquires the authority of an instruction.

Implementation guidance belongs in the input sanitization practical guide [15] and the MCP paper's untrusted-content guidance [10]. This includes input filtering and validation, output checks, the data/control distinction, detached defences and red teaming. This paper retains the inbound axis because the containment model is incomplete without it, but does not restate those implementation controls.

Inbound attacks can make an otherwise cooperative agent behave adversarially. A document, tool result or message can redirect it toward actions outside its intended task. Local and outbound controls must still hold when that happens; they cannot depend on the agent retaining its original goals. This is why the paper assumes a model that wants to escape: the assumption covers behavior induced by untrusted input, not only behavior originating in the model itself.

### 2.4 The axes at a glance

| Axis | Enforcement point or surface | Required property | Implementation guidance |
|---|---|---|---|
| **Local** | OS boundary: kernel or its stand-in | Every host-facing action is mediated; policy is outside the agent's reach; enforcement is verifiable. | MCP runtime isolation guide [8] |
| **Outbound** | Network egress boundary and tool/MCP gateway | Every path capable of producing an equivalent consequential effect MUST cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary. | §3; MCP Security paper [10] |
| **Inbound** | Content entering the agent's context | Untrusted content never gains instruction authority. | Input sanitization guide [15]; MCP Security paper [10] |

Section 3 develops outbound mediation. Section 4 addresses consumption across agents sharing a principal. Section 5 explains reference-monitor properties and failure modes. Section 6 examines what remains reachable when a control fails.

---

## 3. Mediation: the tool call, not the network flow

Section 2 introduced two outbound enforcement points: the network egress boundary and the tool or MCP gateway. For agent workloads, this section argues that tool and MCP calls, rather than network flows, are the primary mediation surface. It states the effective-reach invariant that mediation must satisfy and explains the continuing role of the network layer.

**Why the tool call.** A tool call describes an action through a typed operation, structured arguments and an attributable principal. The call can be authorized, transformed or refused based on those semantics. An endpoint-only network policy answers whether the workload may reach a destination; it does not by itself express which action the agent may take against which resource.

The reported gym waitlist incident illustrates the distinction [19]. As described in §1, the account concerns an assistant removing another person's waitlist entry. Permission to reach the booking API does not by itself establish permission to alter that person's record. Authority must specify whose resource the agent may act on and up to what limit. That scope must be carried in the credential and evaluated on every call.

The tool or MCP gateway acts as the reference monitor at this surface. The §5 properties apply in full: complete mediation over the actions it claims to govern, placement outside the agent's reach, and records sufficient to verify both (§7).

Individual tools must also enforce their security-critical constraints rather than delegate those checks to the model. This is the per-tool responsibility described in *Tool Design for Secure Agentic Systems* [20]. The gateway adds the monitor through which every tool passes.

The MCP Security paper's Sandboxing and Isolation and Logging controls provide the implementation details at this surface [10]. This section states what those controls must achieve together rather than repeating them.

The gateway follows the fail-safe default in §4.3. If it cannot obtain a decision, the invocation is refused or held. It is not allowed on any path covered by the claimed assurance boundary.

An allow fallback removes the affected path from the assurance claim while the fallback is active. The fallback MUST be an explicit operator choice, time-bounded and recorded per decision. The assurance-boundary statement (§7.1) records the exclusion.

A rejection of the gateway's own request, such as a rejected credential, is an answer, not an outage. The invocation is refused, and the rejection MUST NOT count toward any breaker or fallback that could turn it into an allow.

**The effective-reach invariant.** For any consequential effect, the agent's **effective reach** is the union of every path through which it can cause that effect:

- direct network or API access from its runtime;
- mediated tool and MCP invocation;
- gateway- and provider-side fetches and execution performed on its request (§3.1);
- delegated agents or services acting on its behalf (§4);
- alternate endpoints, credentials, or registries that produce the same result.

**The invariant: every path capable of producing an equivalent consequential effect MUST cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary.**

Correctly mediating a tool call is not enough while the same effect remains reachable through raw credentials, an unrestricted network path, an alternate server or a provider-side capability. Mediating one path does not establish mediation of the effect. A partial containment claim must explicitly state which paths are excluded from the assurance boundary.

For each decision, record the claimed scope and exclusions in the assurance-boundary statement row in §7.1, identified by content digest. The statement records the scope claimed; it does not prove enforcement.

When components exchange receipts, traces or completed results, one rule holds: **prior evidence never becomes executable authority for the final effect.**

A receipt may authorize skipping duplicate work within a single claimed assurance boundary. It may never replace a mediation step that boundary claims to enforce. Whenever a receipt is used to skip work, record the receipt's digest, the boundary under which it was accepted, and the verdict applied to this invocation.

Under §7's evidence contract, nothing in an evidence record may be usable at an enforcement point to obtain the effect or satisfy a mediation step again. Replay for verification remains in bounds; replay for authority does not.

**What the network layer still buys.** Tool-call mediation does not replace egress control. The network layer has three jobs:

1. **Close non-tool paths.** The gateway mediates requests presented to it as tool calls. Generated code opening raw sockets, runtime update checks and library telemetry can bypass that surface. Deny-by-default egress blocks network paths not forced through the gateway, replacing an open-ended search for bypasses with an allowlist.
2. **Backstop gateway failure.** If the gateway is defeated, disabled or insufficiently specified (§5 modes 1–3), the network boundary still bounds where the effect can land (§6).
3. **Bound quantity.** Bandwidth, destination-count and rate limits cap what a permitted channel can move, even when it is being abused (§3.1). They also provide enforcement points for the aggregate quantities accounted for in §4.

Endpoint-only policy does not express whose resource the agent may act on, which action it may take or up to what limit. Those are authority questions, not simply destination choices.

All three network functions need evidence as well as enforcement. Network-layer records must show which paths were closed, where the boundary held while the gateway was impaired, and what quantities moved. These records let §7 check the assurance-boundary statement's exclusion claims after the fact.

The network boundary and tool or MCP gateway answer different questions: which endpoints may be reached and what may happen (§2.2). The invariant requires both layers' constraints to hold together.

### 3.1 The permitted channel is the exfiltration path

Effective reach includes every fetch a permitted party will perform on the agent's request. Capabilities such as model-side URL retrieval, web search, code interpreters and retrieval connectors can give the agent indirect network access. Its egress envelope is the union of the network reach permitted by its own policy and the reach of all such capabilities acting on its request. A sandbox audit limited to the workload's own network policy does not assess those indirect paths.

Consider a hypothetical deployment in which the agent's runtime can send network requests only to an approved inference endpoint. That endpoint offers URL retrieval performed by a provider outside the sandbox. If the provider fetches an agent-supplied URL without constraining its destination or payload, the agent can use that fetch to send data to an external destination it cannot reach directly. The runtime's egress policy has not been bypassed, but the agent has caused an external effect through a permitted party.

The relevant question is what the provider is authorized to do on the agent's behalf. If the fetch uses authority already granted and no control is defeated, this relay illustrates mode 4 (§5). It presents a confused-deputy risk where the provider's authority exceeds the scope intended for the agent; the Zero Trust paper discusses that risk in §3.2.1 [16].

**When another service acts on an agent's request, limit what that service may do, not just whether the agent may call it.** If the agent needs that service, apply controls such as:

- Method restrictions, such as a retriever that permits only GET requests.
- Bandwidth and rate limits.
- Non-reflective response delivery: return the response to the requester, not to a destination named in the payload.

These controls constrain different aspects of the channel. A method restriction alone does not establish exfiltration prevention: a GET request can still carry data in its URL.

For §4 accounting, keep provider fetches quantity-limited and make their consumption visible to the accounting authority. A quantity limit does not by itself establish that visibility.

When the provider runs the service, require it to enforce the controls you cannot enforce yourself (§1.1). Specify limits on methods, destinations and rates, and require evidence that those limits are enforced. If those controls are absent, include the service's full reach in the agent's egress envelope.

---

## 4. Composition: per-sandbox controls across a set of agents

A set of agents can exceed a shared budget even when every sandbox stays within its own limits.

Where the deploying organization controls the principal's authority, the deployment MUST account budgets and egress across the set of agents sharing that principal and across a delegation subtree, not only per container. Where the organization does not control that authority, require the same control from the provider through procurement (§1.1).

Per-container and per-edge limits are **local invariants that do not compose**: on their own, they do not establish control over the aggregate total.

### 4.1 The failure shape

The per-container and per-edge controls in §§2–3 bound what one container or one delegation edge may do. An egress cap limits one sandbox, a destination allowlist limits its permitted destinations, and scope attenuation narrows authority at each delegation hop. Each is a **local invariant**: it can hold without establishing a bound across the whole set.

Operators need to look at the group, not just at each agent: how much data the agents send out, how many distinct destinations they contact, how much money they spend, and how many actions they take that change something outside themselves. The same group-wide view applies to how many agents are created, how many levels a delegation chain reaches, and how many other agents each agent delegates to. Both groups matter: all agents sharing a principal, and the agents within each delegation subtree rooted at that principal.

For a resource that adds up across agents, each agent can stay within its own allowance while the group uses more than the principal's budget. Per-container checks alone do not enforce a limit on the total.

Consider a hypothetical coordinator that assigns work to twelve agents, each with a 10 MB/day egress limit. If each agent sends its full allowance to a different destination, the group sends 120 MB to twelve destinations without any agent exceeding its local limit.

Delegation rules address a different part of the problem. The approved *Agentic Identity and Access Management* paper [9] says scope "SHOULD narrow at each hop and MUST NOT expand beyond the delegating principal's effective permissions." It also identifies agent collusion and proxy chaining: agents can pass data or proxy calls so that, together, they perform an action neither could perform alone.

The per-hop scope rule does not by itself set a shared budget. It limits what authority a child agent receives from its parent agent, not how much the group may consume in total. This section adds accounting across the group to the IAM paper's delegation controls.

**Worked example.** A principal has a 100 MB/day egress budget and a limit of 50 distinct destinations. An orchestrating agent creates twelve worker agents under that principal. Each worker's sandbox allows 10 MB/day, and its network policy permits five destinations. For this example, the workers' destination lists do not overlap, and each worker has enough work to send its full 10 MB across all five destinations.

With only per-worker limits, all twelve workers can complete that work. Together, they send 120 MB to 60 distinct destinations: 20% above both of the principal's limits. Each worker stays within its own limits, so none of the local checks detects the group-wide excess.

With accounting across the shared principal and its delegation subtree, the outcome is different. Suppose the first ten workers have each sent their full 10 MB across their five destinations. The group has now used the full 100 MB budget and contacted 50 distinct destinations. The eleventh worker's first outbound request, which would send more data to another destination, is refused or held before that consumption occurs. The attempted consumption is the alert; its record includes the delegation chain identifying the orchestrating agent.

### 4.2 The closing control: aggregate accounting at the consuming action

To close this gap, use **aggregate accounting** across the agents sharing a principal and across its delegation subtree. Check the relevant group-wide limit at the **consuming action**: the point just before an agent uses a resource or takes an action that counts against that limit.

Name the measures being tracked. The list SHOULD be explicit and small, because each measure needs its own counter and budget:

- data sent out (bytes), per principal and per delegation subtree;
- number of distinct external destinations contacted;
- spend against the principal's budget (currency, tokens or compute);
- rate of actions that change something outside the agent, such as writes, sends or executions;
- number of agents created, delegation depth (how many levels a delegation chain reaches), and fan-out (how many other agents each agent delegates to).

At the consuming action, allow the action only if the shared total, including this action, stays within the principal's budget. Two properties make this an enforcement control rather than a report:

**Consume atomically.** Checking the remaining budget and reserving it in separate steps creates a race. Several agents can each see enough budget, then all proceed and exceed it together.

The implementation MUST use compare-and-consume (reserve the budget atomically, then commit or release the reservation) or serialise consumption per principal. Serialisation means processing consumption for that principal one at a time.

Release a reservation only when the action is known not to have happened. Its outcome may be unknown if the consumer times out, fails between reserve and commit, or receives no answer from the downstream service. A reservation with an unknown outcome MUST remain charged until non-consumption is established authoritatively, or it is reconciled idempotently against the downstream service's own record. Here, idempotently means that repeating the reconciliation does not charge or refund the same consumption twice.

Expiry alone MUST NOT refund an unknown-outcome reservation. An expired reservation does not tell us whether the action happened. Refunding it on expiry could let the same budget be spent repeatedly.

**Enforce the shared limit, not just each agent's allowance.** Dividing a budget among N agents gives each agent a local limit of budget/N. Those local limits do not by themselves preserve the shared budget when the number of agents changes. The accounting authority MUST be consulted for the delegation subtree's aggregate consumption.

A local allowance is acceptable only as a **lease**: an amount the accounting authority has already charged atomically against the shared budget on the agent's behalf. The agent may then spend that allowance locally until it reaches zero. A locally cached allowance that has not already been charged this way is not a lease and does not authorise consumption.

**Requirements.**

**R4.1** Where the deploying organisation controls the principal's authority, the deployment MUST account for at least the following, across all agents sharing that principal and across each delegation subtree, at the consuming action:

- data sent out, measured in bytes;
- number of distinct outbound destinations;
- spend;
- number of agents created.

Other measures that add up across agents, such as tool invocations, tokens consumed or records read from a shared store, SHOULD be accounted for in the same way. Beyond these four required measures, the additional measures to account for depend on your deployment's needs.

**R4.2** Per-container and per-edge limits MUST be documented as local invariants. A containment claim for any measure that adds up across agents, such as total bytes sent or money spent, MUST NOT rely on those local limits alone.

**R4.3** Consumption MUST be atomic, using compare-and-consume or per-principal serialisation. A reservation MUST be released only when the action is known not to have happened. Failure to complete successfully is not enough. A reservation with an unknown outcome MUST remain charged until it is reconciled authoritatively.

**R4.4** Where the organisation does not control the principal's authority, R4.1–R4.3 are procurement requirements on the provider and MUST be written that way (see the procured and integrated agents in §1.1).

### 4.3 The hard sub-problem: the accounting authority

R4.1 relies on a **shared accounting authority** for the principal and its delegation subtrees. Every consuming action is checked before consumption: either directly against the shared budget, or locally against a lease the authority has already charged atomically under §4.2.

For the measures and budgets already covered by that lease, local spending does not require a new call to the shared accounting authority. All other applicable accounting and authorization checks still apply. This shared accounting system introduces three challenges.

**Consistency.** Updating a principal's shared total involves reading the current total, changing it and saving the result. Consumption needs to be serialised or use compare-and-swap: an update succeeds only if the stored value still matches the value that was read. Otherwise, the race described in §4.2 reopens for a window as wide as the replication delay. Eventual consistency, where copies of the total catch up later, is acceptable for reporting. It is not acceptable for deciding whether to allow consumption.

**Latency budget.** Each side-effecting action depends on the accounting check. The implementation MUST set a time limit for that check and MUST define what happens if the limit is exceeded: the action is refused or held for confirmation, never allowed. Letting a delay or failure become permission to proceed would be allow-on-error, not a fail-safe default (Saltzer and Schroeder).

A local cache MAY serve reads for reporting; it MUST NOT authorise consumption from a cached view of the shared budget, however small the amount.

A lease is different: the authority has already charged its allocation atomically. Local spending is permitted only within that lease's scope and remaining allowance, enforced at the consuming action.

The latency bound and refuse-or-hold default apply to the accounting check used for that action, whether direct or local. An unavailable shared service supplies no new allowance. Locally covered consumption may proceed only if the protected local check and every other applicable check can complete within their bounds.

**Trust status.** The shared accounting authority and any local enforcement point for its leases act as reference monitors in the §5 sense. Both MUST be outside the reach of the agents they account for, and their decisions MUST be verifiable after the fact.

Every consuming action of an enumerated measure MUST pass an accounting enforcement point before consumption: either the shared authority directly or a local enforcement point spending an already-charged lease. The local point must enforce the remaining lease allowance atomically, so concurrent consumers or copied or replayed lease state cannot create extra allowance.

A lease covers only its specified principal, applicable delegation subtrees, measures, budgets and accounting interval; each other applicable limit still needs its own accounting check. This does not replace the independently enforced action authorization required by §3.

Where the provider operates these controls, the deploying organisation's assurance is limited to what the provider's evidence supports. That is why R4.4 is procurement.

**Evidence.** Aggregate accounting both prevents over-budget consumption and provides a detection signal. When the control holds, consumption stays within the applicable limit. The alert is the attempt to exceed it: an action refused or held because it would cross that limit. The attempt MUST be recorded and raised as an alert with the same delegation lineage as a successful consumption.

Finding an aggregate above its limit after the fact is a different alert: it means the control failed. Both alerts depend on shared identifiers that let the records be linked across agents.

Every consuming-action record MUST carry the principal and the full delegation lineage, not just the immediate parent, with that information integrity-protected. This lets a reviewer who was not present reconstruct the subtree aggregate (§7.1, the accounting decision row of the evidence contract).

For lease-based consumption, link each consuming-action accounting record to the authority's lease-allocation decision and record the local consumption and remaining allowance. Preserve the principal, full delegation lineage, applicable budget, decision and reason, action and reservation references, and integrity protection required by §7.1.

Keep allocation-time shared totals separate from lease-local values, with each value's scope and accounting point identified; do not present an allocation-time or eventually reconciled total as the current shared total for a later spend. A spend within an already-charged lease is not a second charge against the shared budget.

An unknown local outcome remains charged against the local allowance as well as the shared allocation until authoritative non-consumption or idempotent reconciliation against the downstream record resolves it. Timeout, process failure or expiry alone does not restore spendable allowance.

The lease's protected enforcement state is the bounded allocation; its allocation record is evidence, not a replayable credential that bypasses an accounting or final-effect authorization check.

### 4.4 Prior art: colluding applications

Android security research provides an earlier example of why components need to be assessed together. In 2011, Felt et al. studied **permission re-delegation**: an application uses its permission to perform a privileged task for another application that lacks that permission. They identify this as a special case of the confused-deputy problem [21].

In 2012, Bugiel et al. distinguished confused-deputy attacks from **collusion**, where malicious applications combine their permissions to gain a capability the user had not approved for them together. Their framework applies system-wide policies to communication paths between applications, including indirect paths, rather than relying only on each application's permissions in isolation [22].

These studies provide a precedent for examining how authority combines across components. They do not by themselves establish the shared-budget controls described in §4.2. The following comparison is an analogy, not a direct equivalence between Android permissions and agent budgets:

| Android research | Useful analogy for agents |
|---|---|
| Permission sets held by applications | The permissions granted to each agent. |
| An unapproved capability enabled by combining permissions | Check what collaborating agents can cause together. |
| Direct and indirect communication paths between applications | Follow requests through agents and services, not just one hop. |
| System-centric policies on paths and permission combinations | Enforce rules on the combined authority reachable through those interactions. |

The shared lesson is to check what components can do together, not just the permissions held by each one. The Android work provides that precedent; the principal-wide and subtree budget controls in §4.2 are a separate mechanism. Checks on communication paths or permission combinations do not, by themselves, enforce those budgets.

---

## 5. The enforcement property and four failure modes

Every control in this paper relies on an enforcement point: a component, outside the agent's control, that sees the agent's action and decides whether to allow it to proceed.

The incidents discussed in this paper show different ways controls can fail. Keeping those failures distinct helps identify the right remedy: a fix for one kind of failure may not address another.

### 5.1 The property, named

A **reference monitor** checks each consequential action against the applicable policy before allowing it to proceed. The classical model sets three requirements for the mechanism that performs these checks [23]:

- **Complete mediation.** Every path to an effect must cross the monitor before that effect occurs. A path that bypasses it is unmediated, not partly mediated (§3).
- **Tamper-proof.** The agent cannot change the monitor or the policy it applies. Both the monitor and its configuration stay outside the agent's write scope.
- **Verifiable.** Its implementation is small enough to analyze and test fully, including whether it applies the policy correctly and is always invoked.

The CoSAI *Zero Trust for AI Systems* paper says authorization must not be delegated to the AI model or another non-deterministic component [16]. A model can request an action; deterministic security controls decide whether it is allowed.

Those controls and their policies must also stay outside the agent's control. Otherwise, the agent can change or disable them even when their decision logic is deterministic (mode 2, §5.2).

For agent workloads, the monitor must also produce records that let a reviewer verify that mediation occurred (§7). The reviewer need not have been present or trust the operator.

These records complement analysis and testing; they do not replace them. Without verifiable evidence of mediation, a reviewer cannot confirm from the records that it occurred.

A reference monitor can operate at different layers of the system, not just in the kernel. Tool and MCP calls can be mediated by a gateway or another policy enforcement point (§3) [16]. System calls can be mediated by the kernel [7], and network egress by a proxy.

A policy decision point determines whether access is allowed; a policy enforcement point carries out that decision. These are different roles, even when one system performs both [24].

An agent deployment has enforcement points at several surfaces. Each must satisfy the three reference-monitor requirements. What matters is complete mediation, tamper resistance and verifiability, not the component's privilege level.

### 5.2 The four failure modes

This paper groups containment failures into four modes, each with different causes and remedies.

**Mode 1 — the agent defeats the control.** The control was correctly specified and had not been disabled, but its enforcement mechanism failed. For example, the agent may exploit a vulnerability in the isolation mechanism.

The remedy is to fix and harden the mechanism: meet measurable patching commitments for the isolation path, minimize the attack surface and use stronger isolation where the workload warrants it (§6).

**Mode 2 — the agent disables the control.** The agent had or acquired authority over the control itself and used it to turn the protection off.

Ona reports a related example. Asked to find a way to run a blocked command, Claude Code proposed disabling its sandbox after bubblewrap failed to create a namespace. It then requested approval for unsandboxed execution, and the command ran [5]. This illustrates an agent seeking to remove a constraint, not an approval-free bypass of the sandbox.

This mode is a failure of the tamper-proof property. The remedy is architectural: keep the control and its configuration outside the agent's control, and treat any attempt to alter them as a high-signal alert (§7).

**Mode 3 — the control was insufficiently specified.** The control was active and unchanged by the agent. The agent had no authority to change its policy. The weakness was in the rules: they left a gap in the boundary they were meant to protect.

For example, a Linux seccomp filter can restrict system calls by number but omit the architecture check needed to interpret those numbers correctly. The kernel documentation explicitly warns against this mistake [7].

A command denylist can miss an alternate path to the same executable [5]. An isolation policy can likewise leave the host's privileged Docker daemon reachable from the workspace [6]. Both leave gaps in the intended boundary.

One failure mode can also create the conditions for another. When an inadequate policy exposes the host's privileged container-runtime socket (mode 3), it also puts the enforcement point within the agent's reach (a mode-2 condition, §2.1).

Both failures need to be addressed. Correct and verify the policy to close the unintended path. Keep the control and its configuration outside the agent's control, and treat attempts to alter them as high-signal alerts (§8.3).

Before deployment, test that the sandbox enforces the intended boundary (§8). The control must also support rules precise enough to express that boundary (§3). Stronger isolation alone does not fix a gap in the policy.

Mode 3 takes two forms, and they need different remedies:

- **The policy is inadequate.** Its rules do not cover the intended boundary, as in the seccomp example above.
- **The intended policy is adequate, but it is not the one deployed.** A setting is left open, an image drifts, or the configuration changes between approval and the run.

Anthropic reported that models intentionally running without cyber safeguards reached the internet because of a misconfiguration in a third-party evaluation environment [18]. This was not a sandbox escape: internet access had mistakenly been left open.

Checking the policy specification addresses the first form. For the second, test the deployed controls before each run to confirm that they enforce the intended policy. Repeat those tests during long runs before the previous results expire (§8.2). Anthropic likewise recommends verifying the sandbox configuration "before every evaluation begins" [18].

**Mode 4 — the control was correct and the agent used permitted authority.** The control enforced its policy correctly, but the agent could still cause harm through actions that policy allowed.

The reported gym waitlist incident illustrates why permission to reach an API is not permission to alter another person's record [19]. It does not, by itself, establish that the containment controls worked correctly. A permitted gateway fetching an agent-supplied destination presents a related risk: the service can perform a harmful action without the agent escaping its sandbox (§3.1).

The Zero Trust paper gives a direct example: an agent allowed to read sensitive data and email external recipients can send that data out while staying within its permissions [16]. More precise policies can restrict the data sent or require approval. Stronger isolation alone does not resolve this use of permitted authority.

The response is to narrow the grant (the subject of the Agentic IAM paper [9]), constrain what permitted services will do on request (§3.1), and account for shared authority across agents (§4). Preserve evidence for review afterward (§7).

The first three modes describe different enforcement failures: a mechanism breaks, an agent disables a control, or the policy is inadequate or incorrectly deployed. These modes do not map one-to-one to the three reference-monitor requirements. Every enforcement point must still check each consequential action, remain protected from changes by the agent, and be small enough for complete analysis and testing (§5.1). The failure modes help identify what went wrong; they do not replace those requirements.

Mode 4 is different: the monitor has not failed. It correctly enforces the policy, but that policy permits an action that can cause harm. Containment therefore remains one layer of a bounded-authority model (§1). Correct enforcement matters, but so does the authority being enforced.

### 5.3 Why the distinction matters

Separating the four failure modes has three practical consequences.

First, match the remedy to the failure. Stronger isolation alone does not correct an inadequate policy. Even a correctly enforced policy can permit harm if the grant is too broad. A control the agent can disable needs protection from the agent; a policy error needs correction and verification. Identify which control must change and who is responsible for it.

Second, classifying an incident requires evidence. To distinguish mode 2 from mode 3, reviewers need a record of the control's configuration and enforcement decision at the time. To distinguish mode 1 from mode 4, they also need a record of what the agent was actually permitted to do.

Use evidence that meets §7's requirements to support the classification and route the fix. Where the record leaves the failure mode unresolved, identify the missing evidence and explain which conclusions it prevents the reviewer from drawing. The review should make that uncertainty visible rather than assign a mode the evidence does not support.

Third, use the failure modes to explain each control's role. The table summarizes the sections' main contributions; it does not limit a control to one mode.

| Section | Main contribution |
|---|---|
| §3 Mediation | Supports rules precise enough to state the intended boundary (mode 3). |
| §3.1 Permitted channels | Constrains what permitted parties do at the agent's request (mode 4). |
| §4 Composition | Applies shared limits across agents even when each passes its local checks (mode 4). |
| §6 Reachability | Reduces reachable systems to limit the consequences of modes 1–3. |
| §7 Detection and evidence | Supplies signals during operation and evidence for later review across all four modes. Conclusions depend on what the records establish. |
| §8 Verification | Tests whether the deployed controls enforce the intended policy, particularly for mode 3. |

For each control, ask which failure it is intended to prevent or limit, and what evidence would show that it worked.

### 5.4 Threat sources and trust assumptions

The table summarizes the threats considered, the components relied on and the properties those components must maintain. It also states the limits of the paper's claims. Each row refers back to its governing section; the table adds no new requirements.

| Threat source | Component relied on | Required property | Limits and exclusions |
|---|---|---|---|
| The agent's own model, which may try to exceed its bounds | None; no property of the model is relied on | — | Assume a model that wants to escape. Model-level safety training and refusals are out of scope (see Out of scope). |
| Untrusted content entering the agent's context, such as documents, tool results and retrieved data (§2.3) | The inbound enforcement point | Content from an untrusted source never gains authority as an instruction (§2.3). | Implementation controls are not specified here. They remain in the input-sanitization guide and the MCP paper's guidance on untrusted content (§2.3). |
| A permitted party acting on the agent's request, such as model-side retrieval, search, interpreters or connectors (§3.1) | Limits on what the permitted party may do, not just whether the agent may ask | Where the channel cannot be removed, bound the party's actions with method and bandwidth limits and non-reflective response delivery: return responses to the requester, not to a destination named in the payload (§3.1). | If a provider-side capability cannot be bounded, state that path as an exclusion from the claimed assurance boundary. Do not assume it is closed or omit it from effective reach (§3). |
| Other agents, including peers in the same organization (§9.2) | Inbound controls (§2.3), effective reach (§3) and shared accounting (§4), applied across agents | A peer's message has no more instruction authority than a web page. A peer willing to act on request is part of effective reach, even without a delegation. Recruitment counts as consumption (§9.2). | How models are jailbroken is out of scope; that is model-level safety (§9.2). |
| Any consequential action the agent can take | The reference monitor at each mediation surface (§5.1) | Mediate every claimed effect. Keep the monitor and policy outside the agent's control. The implementation must be small enough for complete analysis and testing, and produce records sufficient to verify mediation (§5.1). | A path that bypasses mediation must be stated as an exclusion, not called partially mediated (§3). If the agent can alter the monitor or its policy, the tamper-proof requirement is not met (mode 2, §5.2). |
| Agents sharing one principal, each passing its local checks (§4) | The accounting authority tracking the shared budget across the principal's delegation subtree | Use atomic compare-and-consume before consumption, directly against the shared budget or locally against an already-charged lease. If that check exceeds its latency bound, refuse the action or hold it for confirmation; do not allow it (§4.3). | Totals calculated afterward do not establish atomic enforcement. Per-agent limits alone cannot establish the shared bound (§4). A spend covered by an already-charged lease does not require a new central call; all other applicable checks still apply (§4.3). |
| An outside reviewer who was not present and does not trust the operator (§7.1) | The evidence record each monitor emits | Include each evidence field on every record unless its §7.1 row states otherwise. Record a determined absence as `absent` and missing visibility as `not_established`. No field may be replayable as executable authority (§3, §7.1). | Detection signals are separate: they may be noisy, heuristic and tuned to the deployment (§7.1, §7.2). A trajectory from the agent's own framework is not, by itself, independent evidence of containment (§9.1). |
| Systems the agent reaches that belong to another party (§6.2) | Nothing under the operator's control | — | The §7 evidence contract cannot require a third party to retain records, cooperate or meet a particular standard of record quality. Reconstruction depends on those records and cooperation; limit the claim to what the available evidence supports (§6.3). |
| Procured and integrated deployments (§1.1) | The organization and provider, according to which controls each can operate; provider obligations are contractual | Meet the paper's applicable containment requirements, whether the controls are operated by the organization or a provider. The organization must implement and demonstrate the controls it can operate. For controls it cannot operate, require the provider to meet those requirements and supply evidence (§1.1). | Do not assume isolation is absent because an agent is procured or provider-operated. Engineering and procurement responsibilities can coexist. Only where the organization cannot interpose any controls do those requirements fall wholly on the provider (§1.1). |

This table is not a complete list of threats. It states the assumptions behind the paper's argument so readers can check them against their own deployment.

A component is not trustworthy merely because it appears in the table. Each component can fail (§5.2). Use evidence meeting the paper's evidence requirements (§7) to assess whether it worked as intended, and limit the conclusion to what the records establish.

---

## 6. Reachability and blast radius

Reducing which systems an agent can reach is a control in its own right, separate from vulnerability management. The distinction affects both what the operator can constrain and what the evidence can establish after an incident.

### 6.1 Patching and reachability address different risks

Vulnerability management still requires a clear patching policy: no known-exploitable CVEs (publicly catalogued vulnerabilities) in the isolation path, defined patching deadlines with measured compliance, a minimal attack surface, and named compensating controls when patching is delayed. This is not a promise of zero CVEs.

Keeping software patched does not, by itself, establish that the policy enforces the intended boundary. For example, Linux's system-call filtering (seccomp) documentation warns that a filter can be bypassed if it checks a system call number without also checking the architecture [7]. Patching also cannot guarantee protection from vulnerabilities that have not yet been discovered.

Enforcement failure cannot always be ruled out. The design must therefore also limit its consequences: the systems an agent can reach when a mode 1, 2 or 3 failure occurs (§5). Design choices include deny-by-default egress, which peer services share the agent's network, and which credentials are available to the agent (§2). These choices can be made before a particular vulnerability is known.

Vulnerability management reduces the risk of a boundary failure. Reachability minimization limits the consequences when failure occurs. Both are required. Responsibility follows actual control: the organization implements and demonstrates the controls it can operate. For controls it cannot operate itself, the organization must specify what the provider is required to implement and what evidence the provider must supply to demonstrate that those controls meet the paper's applicable requirements (§1.1).

Put this into practice in three ways:

- Maintain an inventory of every system, service and endpoint the agent can reach through any path in its effective reach (§3). Keep the inventory as deployment configuration and verify it before each run (§8).
- Review the inventory against the task's requirements and minimize unnecessary access. Every reachable system the task does not need adds exposure if a control fails.
- Apply the patching policy above to what remains reachable, with responsibilities assigned according to actual control (§1.1).

Inputs for the inventory include:

- The deployment architecture: local resources and host interfaces, network peers, and egress policy.
- The credentials and authority available to the agent (§2).
- The actions enabled by tools and MCP servers.
- The indirect and alternate paths described in §3.

Design-time threat modeling can bring these inputs together to identify which systems are reachable and which the task requires. Update the inventory when any of these inputs changes, and verify it against the deployed system as §8 requires.

Version the inventory of systems the agent can reach. Each run's record must identify the inventory version used for that run by its content digest, a hash of the inventory's contents (§7).

What the run actually touched is measured rather than declared. It can be compared with the declared reachable set only after the run, and only when the record identifies the inventory used. Keep three outcomes distinct:

- The touched set is within the declared set.
- The touched set extends outside the declared set.
- The comparison cannot be determined because the journal is incomplete.

An incomplete journal must not be treated as proof that the run stayed within the declared set. This paper requires inventory versioning and keeps the three comparison outcomes distinct. A practical guide should explain how to perform the comparison; it does not replace these requirements.

### 6.2 Which reachable systems are yours

This example distinguishes controls within an evaluation environment from controls on another organization's production systems.

In its preliminary account, published in July 2026, OpenAI reported that evaluation models exploited a vulnerability in an internally hosted package-registry cache proxy, then escalated privileges and moved through its research testing environment to a node with Internet access. The models had no direct Internet access at the start, and their cyber refusals had been reduced for evaluation purposes [2].

For the evaluation environment, include package infrastructure in the reachable-set inventory (§6.1). Where the operator controls a service or access path, restricting access, hardening and monitoring are available control options. Where a provider operates those controls, implementation and evidence obligations follow §1.1.

Hugging Face's disclosure reports an intrusion through its data-processing pipeline, followed by node-level access, credential harvesting and lateral movement. It does not identify the model or link the intrusion to a named evaluation [14].

An evaluation operator cannot assume it can patch another organization's systems or monitor their internal activity. Its containment design must minimize unnecessary external reach and limit what the agent is authorized to do through the connections it still needs (§§2-3). When a provider operates controls the organization cannot operate itself, the organization must specify what the provider must implement and what evidence it must supply to demonstrate that the applicable requirements are met (§1.1).

In the reported gym waitlist case, an AI agent acting for a gym member removed another person's waitlist entry [19]. The relevant point here is ownership: the booking system belonged to a third party, not to the member or the agent's operator.

Classify the reachable set by ownership and actual control. For each system, identify what the organization can constrain directly, what it must require from a provider, and what remains outside its control (§1.1).

### 6.3 System control and evidence

Control over the systems an agent reaches affects what evidence can be collected and what it can establish after an incident.

When the operator controls both systems, it can collect records from both sides of an interaction. That control does not, by itself, establish that the records are complete.

For a third-party system, the operator's record of a request does not, by itself, establish what happened on the other side.

Reconstructing both sides requires records that can be linked. Where reconstruction requires records held by the third party, it depends on that party's retention, cooperation and record quality. The operator cannot assume control over those dependencies, and this paper's evidence requirements cannot impose them on the third party (§7).

After OpenAI's disclosure, Anthropic reported reviewing 141,006 evaluation runs in which Claude could have obtained Internet access [3]. Its retrospective review used existing transcripts to identify real-world activity.

Two consequences follow.

- **For engineering:** Cross-boundary access that cannot be removed should be forced through the operator's own mediation controls (§3), so that, at minimum, the asking side of every interaction is recorded in first-party records with full lineage (§7). Full lineage includes a record of the responsible agent and its delegation chain.
- **For cross-system evidence:** The resource owner's record needs to identify which agent request led to the recorded action. A shared identifier connects that record to the operator's record of the request.

  For this link to serve as evidence, the operator must create and sequence the identifier on the asking side, in its own integrity-protected sequence, before dispatching the request (§7). The identifier must travel with the request. The link must not be something the two parties agree to add afterwards.

  The resource owner's event can then be checked against an entry sealed before dispatch. Subject to §7's evidence conditions, the operator cannot later disown or retrofit that link.

When cross-system reconstruction needs records held by the resource owner, it depends on that owner's cooperation (§7). For every reachable system, the inventory in §6.1 should identify the system's owner, who holds the required records, and how long those records remain available.

For example, if a third party holds a required record and deletes it after thirty days, reconstruction after that point cannot rely on retrieving it. Determine how long records will remain available while you design the deployment, rather than waiting until you need them to reconstruct an incident.

For controls the organization cannot operate itself, it must specify what the provider must implement and what evidence the provider must supply (§1.1). That evidence must include the provider's reachable-set inventory and system-ownership classification. The organization remains responsible for implementing and demonstrating the controls it can operate itself.

If the provider cannot enumerate the systems its agent can reach, a containment claim covering that provider-operated reach is not established.

---

## 7. Detection and evidence

**Purpose.** Carry the detection argument and a schema summary in the paper; put the concrete logging schema in a practical guide alongside the MCP runtime isolation guide.

Detection and evidence are two artifacts against the same event, not one list. Detection wants signals that discriminate an attempt from normal behavior, and is allowed to be noisy, heuristic, and tuned per deployment. Evidence wants the fields that let someone who was not there and does not trust you reconstruct what happened, and must be stable, complete, and boring — and nothing in it may be executable authority (§3).

The evidence contract is normative in this paper; the OCSF mapping goes in the practical guide, pinned to an OCSF version, with proposed fields marked as proposed. §7.1 is structured as two tables accordingly.

The blog post's "containment that fails loudly" and "tamper-evident logging" bullets: alert on denied syscalls, repeated policy violations, `/proc` inspection, Docker socket and metadata-service probes, blocked DNS and egress, credential-broker denials, and any attempt to alter the sandbox configuration; keep those events outside the agent's write scope; correlate across runs; use OCSF `attestation` and the `record_integrity` profile (OCSF 1.9.0) for tamper evidence [12].

Correction to the supporting narrative, from the A.2 source check: Anthropic's sentence is "the two organizations **we were able to reach** had not previously detected the activity" — narrower than the blog's paraphrase — and Hugging Face *did* detect their own intrusion, via LLM-based triage on anomalies, before OpenAI connected its internal testing to it.

The section's argument survives both facts, but must carry them: the strongest counter-example in the field is also the best existing evidence that the detection this section calls for actually works.

**Requirements across §7.** An absence that was determined MUST be distinguishable in the record
from an absence that was never established. A determined absence carries an explicit value and
reason; missing visibility or incomplete observation is recorded as `not_established`, with the
missing premise. An omitted field establishes neither absence nor a negative finding.

The observation states are `present` (established), `absent` (absence determined),
`not_established` (the observation could not be established), and `pending` (an
outcome is not yet known). An unknown action outcome is `pending`; it does not
become `not_established` when the reporting window ends. Report that pending
outcome as "not verified by the end of the window", with the window duration.

**Evidence independence.** Evidence cannot rule out a failure if that same failure could compromise the component that produced, signed or retained it. If an agent escapes its sandbox or disables its gateway (§5.2, modes 1 and 2), evidence produced alongside that control may no longer be trustworthy: logs may be altered or suppressed, and signing keys may no longer show who wrote the record. This paper calls the set of components that can be compromised together a *trust domain*. §9.1 makes this point about trajectories produced by the agent's own framework, and it holds for other controls: a sandbox cannot, by itself, provide independent evidence that it was never escaped, and a gateway on a compromised host cannot independently establish that it was never disabled.

A containment claim that rules out a defeated or disabled control (§5.2, modes 1 and 2) MUST NOT rest solely on evidence from a trust domain that failure could also compromise. The record SHOULD therefore identify the trust domain of its producer, or otherwise make its independence assumptions explicit. Where the deployment shape (§1.1) provides no evidence producer outside the workload's trust domain, the claim narrows accordingly: such evidence can establish what the monitor observed or decided while its integrity is assumed to hold, but it cannot independently rule out modes 1 and 2. As with an unverifiable subject claim (§7.1), this constrains what the record can support; it does not change the underlying enforcement decision.

### 7.1 What to log

Two approved WS4 papers already carry most of the field list, and this section should be read as extending them rather than restarting them.

- The *Model Context Protocol Security* paper requires, at L2 and above, structured logging of tool identity, caller identity, policy decision, resource target, outcome, request metadata and correlation identifiers, with raw parameters logged only after redaction, hashing or field-level tokenization, rising to immutable tamper-evident logging of all interactions at L4.

- The *Agentic Identity and Access Management* paper's Appendix D requires agent ID, subject ID, tenant, environment, resource and action, decision with reason, scope and authorization details, policy version, attestation information and a `correlation_id`, and states the "prove control on demand" obligation: an organization must be able to answer, from logs alone, which agents were active, what permissions they held at that time, who was involved in each action, and which policies, attestation evidence and delegated scopes justified each decision.

What this paper adds is the separation. Those lists are single lists serving two readers.

- **Detection** is written for an operator inside the deployment who is trying to notice an attempt in progress, and it is allowed to be noisy, heuristic and tuned locally.

- **Evidence** is written for someone who was not there and does not trust the operator, and it must be stable, complete and dull.

A field that earns its place in one does not automatically earn its place in the other, and the two have opposite failure modes: a detection signal that fires too rarely is useless, while an evidence field that is present only sometimes is worse than absent, because a verifier cannot distinguish "did not happen" from "was not recorded".

Two constraints apply to the evidence table as a whole.

1. Nothing in an evidence record may be executable authority (§3): the record states what was decided and on what basis, and a consumer of the record must never be able to replay a field in it to obtain the decision again.
2. Correlation is scoped to the shared principal and the delegation subtree it roots, not to one run or one container (§4); a per-run correlation key cannot show that a set of individually compliant agents collectively exceeded the intended authority or budget, which is the failure §4 describes.

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

Signals and counters derived from enforcement decisions count the verdict applied to each
invocation, as its evidence record carries it, not a reused decision.

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
| Runtime identity or attestation reference | What was executing, as opposed to what claimed to be executing | Required. Bound to this record so it cannot be reused from another run: the attested data covers the checkpoint signing key and the policy version. States whether it carries attestation evidence or an attestation result (RATS [17]); a result names the verifier that produced it. Where attestation is not available in the deployment shape (§1.1), the field carries an explicit `not-available` value with a reason rather than being omitted. An explicit absence is evidence; an empty field is a shrug |
| Outcome | Whether the action took effect | Distinct from the decision: an allowed action can still fail, and a refused one can still have partial effect. Recorded as a later entry that references the decision it resolves. A decision whose outcome entry is missing has an unknown outcome, and stays unknown until an outcome is recorded; it is not read as success, and per §4 it remains charged |
| Integrity-protected sequence with trusted checkpoints | Ordering and detectable gaps within a declared record sequence | Verification needs expected sequence boundaries and trusted checkpoints. A completeness claim also needs a declared collection scope and accounting for actions omitted before recording. A timestamp alone does not establish completeness. |
| The accounting decision | What the aggregate budget stood at, and what was reserved, committed, released or reconciled for this action | Per §4, record the accounting authority's decision and reason, the principal and subtree, applicable budget, aggregate consumed and remaining, and reservation/action references. Preserve refused or held attempts even when no consumption follows. An unknown outcome remains charged until authoritative non-consumption or idempotent reconciliation; post-hoc totals do not establish atomic enforcement |

Where the accounting authority is also the enforcement point for an action, its
accounting decision is that enforcement decision: one record can satisfy both
rows. Where the authorities or decisions differ, preserve each decision and its
relationship to the same action.

Where consumption is covered by an already-charged lease, the accounting evidence may be a linked set: the authority's allocation decision records the applicable principal/subtree budgets and aggregate consumed and remaining at allocation; each consuming-action record identifies that allocation and records the local decision, amount consumed and allowance remaining.

Identify the scope and accounting point of each value. Preserve decision reasons, action/reservation references, full integrity-protected lineage, outcomes, refused or held attempts, and all other applicable evidence fields. Do not claim that allocation-time or eventually reconciled totals are contemporaneous shared totals for each local action.

Where a claimed current total or complete reconstruction is not established, state that limitation rather than substituting an old total or treating missing evidence as proof of enforcement.

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

**Require controls and uncertainty for measured rates.** Before a measured rate counts as evidence, report its numerator and denominator, a benign control matched to the stated conditions and outcome criteria except for the intervention under test, and an uncertainty interval with its method and level. State the sampling unit and account for correlated repeats when computing the interval: in a task-grouped evaluation, retain episodes within each task and compute uncertainty across tasks rather than treating episodes as independent. Preserve the per-task or per-group counts, aggregation rule and control results so a reviewer can reproduce the calculation. An attack failure rate without its matched benign control cannot distinguish an attack effect from ordinary task failure. If the number of independent units or remaining dependence prevents a supported interval, report that limitation; a rate alone does not close this section's baseline gap.

**Keep self-test traffic out of the counts.** A check that feeds synthetic input to a detector or an enforcement point, such as the pre-run check in §8.2, produces alerts and denials that no live workload caused. Each synthetic invocation must carry a marker in its record that names the test behind it. Remove marked invocations before counting alerts, units or either denominator, and report the number removed. If the record cannot separate synthetic from live invocations, report the count as not established, with the missing premise.

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

**Record why execution stopped.** Preserve a normalized reason distinguishing an operator-requested containment action, an automated policy response, ordinary completion, a crash and an unknown reason. Record the native reason alongside its mapping and version.

A model turn ending, reaching a token limit or yielding to a tool is not sufficient evidence that the agent's authority ended. Correlate stop records, enforcement actions and per-invocation outcomes by agent instance and action identifiers; do not infer a tool's outcome from the model's stop reason.

The accounting verdict (`allowed`, `refused` or `held`) records the accounting
authority's decision; the stop reason records why execution stopped. Keep both
when applicable. A `held` verdict awaits confirmation of the same action; a
containment response request initiates containment of the named scope. Neither
field substitutes for the other. An unknown stop reason can accompany a verified
outcome, and a known stop reason can leave the outcome `pending`.

The practical guide should bind these concepts to the selected OCSF revision and coordinate any schema gaps with the WS2 telemetry work. This section defines the information needed for the measurement without assuming that one existing stop-reason field [13] represents all of it. Evidence of an earlier decision remains evidence; it must not authorize replay or bypass a mediation step (§3).

### 7.4 Evidence sufficiency for absence claims

An empty event field cannot establish that nothing happened. The producer may not have been able to see the event, or the observation may have missed part of the interval. This rule applies to a stated property, invocation, time interval and scope. 

| ID | Clause | Source |
| --- | --- | --- |
| C1 | Use `not_established` as defined in section 7: the observation could not be established, with the missing premise recorded. After the applicable verification has run, an absence claim that the admissible observations justify neither passing nor failing remains `not_established`. Name the unresolved proof obligation and bind the result to the property, invocation, interval and scope checked. This does not redefine the observation states: an unknown action outcome remains `pending`, including when the reporting window ends. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104) |
| C2 | Malformed input, an unsupported verification path, parser failure, and internal verifier error are processing failures. They are never `not_established`; otherwise a broken verifier becomes conformant by returning the third value. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5629517996), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5671639059) |
| C3 | Outcomes are asymmetric. An admissible observation of the prohibited event within the evaluated scope can settle `fail` without complete coverage. A self-reported write is not an admission on its own: without independent observation it stays `not_established`, even if the record is signed or reports a write. No observed event without established coverage is also `not_established`. Admissibility for the property is distinct from structural validity of the record. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5672256489), [Levaj2000](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5672817487), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/219#issuecomment-5904200879) |
| C4 | A claim that no event occurred over a scope passes only when the producer could see the relevant field for the invocation and the observation covers the evaluated interval. A present but empty field needs the same premises as a missing field. If either premise is unestablished or bound to another scope, return `not_established` with the missing obligation. Coverage can be established by another verifier surface. | [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5702083982), [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5739339967) |
| C5 | Coverage must be bound to the claim or invocation it covers. A complete record for one call cannot establish completeness for another. Matching identifiers alone do not prove that binding; an authenticated identifier inside the observation still needs an independently established join to the evaluated invocation. | [chernistry](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5710166163), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5745298467) |
| C6 | Checker input and harness expectation stay structurally separate. The expected verdict and obligation are authored, so they are never visible to the inference that derives the result. | [darklordVirtual](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5630431104), [aeoess](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5638613689) |
| C7 | A coverage statement takes one of three well-formed shapes: complete over the evaluated property, invocation, interval and scope; incomplete, with every gap located by the path, field, resource or sub-interval it did not observe; or `not_established`, with the reason coverage could not be determined. A statement of incomplete coverage that locates no gap is malformed and, under C2, a processing failure. Its empty gap list would vacuously pass any test that each named gap lies outside the scope, and a checker that accepted it would let an admitted blind spot pass C4. A located gap outside the evaluated scope leaves C4's coverage premise intact. A gap inside it returns `not_established` naming the gap, while an admissible observation of the prohibited event elsewhere in the scope still settles `fail` under C3. | [astrogilda](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827010158), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5827685232), [astrogilda](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189#issuecomment-5859188410), [imran-siddique](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172#issuecomment-5937506235) |

The checker receives the property, evidence and evaluation context, including declared producer capabilities and the independently established binding to the observed invocation. It returns the verdict, the unmet obligation for `not_established`, and a binding that identifies the property and context it checked. Runtime outcome is evidence, never a verdict. The harness holds the expected verdict and obligation separately and grades committed fixtures read-only; rebuilding before grading can silently repair a tampered expectation.

Record the observation vantage: who observed the event, which inputs they could see, and who could forge or suppress those inputs. Record the coverage denominator: the invocation, resources, fields and interval actually observed, including known gaps. These facts determine which claims the record can support; a declared independent observer or an empty event field does not establish them. The [agent-evidence-vocabulary](https://github.com/probityai/agent-evidence-vocabulary/blob/main/vocabulary.yaml) provides informative names for these facts. Implementers do not need that repository to apply this rule.

**When an observer is independent.** C3 and C4 depend on whether an observation comes from a party independent of the producer it describes. Recording the observation vantage helps a verifier only if independence can be tested. An observer is independent of a producer when all three conditions hold and the record shows each:

- It sits outside the producer's trust domain (the set of components that can be compromised together; §7), so no single compromise reaches both;
- Its identity rests on a basis the producer cannot issue, alter or revoke: attestation evidence appraised against reference values where the deployment shape supports it (§1.1), and otherwise an external basis identified in the record;
- Control of the keys that sign its observations is established by evidence; distinct key identifiers do not establish it.

Each condition must be established by evidence carried in or referenced from the record. A declaration of vantage, origin or key identity does not establish independence, for the same reason a declared independent observer does not establish observation vantage. The evidence can come from trusted evaluation context and does not require hardware attestation.

These properties stay separate: key separation does not establish custody of the signing keys, custody does not establish independence, and independence does not establish coverage (C4).

[Observer-independence cases IND-01 to IND-11](https://github.com/astrogilda-forks/ws4-secure-design-agentic-systems/tree/a79078297b2441e4bdfcb3f0d6537f89e80ad4ba/conformance/RFC-189/observed-effect/cases), proposed alongside this text, apply this test condition by condition. IND-01 passes with an attested identity and IND-02 with a software-only identity basis (§1.1). IND-03 to IND-08 each leave one condition without evidence or rest it on evidence the producer controls, and return `not_established` naming that condition. IND-09 returns `not_established` for the observed party's own vantage despite full evidence, and IND-10 for evidence bound to another claim (C5). Once this text and those cases are approved, a verifier that claims to apply this test MUST, when evaluating IND-01 to IND-10 using their documented stipulated premises, return the expected verdict and unmet obligation specified in each case file. The case file is the reference: the `verdict` and `unmet_obligation` values of its `expected` block must match exactly. A verifier that also appraises the referenced evidence may reach a different result for IND-01 and IND-02; that result answers a different question and does not breach this requirement. IND-11 records the limit of that requirement: a checker that does not appraise the evidence it receives passes fabricated evidence, so its `pass` holds only given that evidence. Each case reads a signed Observed Effect record that [agent-evidence-vectors v0.25.0](https://github.com/probityai/agent-evidence-vectors/blob/v0.25.0/vectors-observed-effect/statements/v162352770f2f6c1c.json) publishes; implementers do not need that repository to apply the test.

An observation from an observer that fails any condition counts as self-reported under C3. Independence holds between one observer and one producer, so it is recorded per claim, as C5 requires of coverage. This test does not define the verifier surface that establishes coverage (C4); it states what any such surface must show before its observations count as independent.

[Candidate conformance cases](https://github.com/astrogilda-forks/ws4-secure-design-agentic-systems/tree/a79078297b2441e4bdfcb3f0d6537f89e80ad4ba/conformance/RFC-189) exercise producer visibility, interval coverage and claim binding. They are pinned to a revision rather than a branch, for the same reason this paper pins its OCSF references: a reader must be able to see the cases this text was written against. They remain non-normative until this text is approved. The passing Observed Effect cases assume an independently anchored expected prior commitment; they test use of that premise, not its real-world provenance. Case 10 returns `not_established` under C3 for a self-reported write without independent observation. Cases 3 to 6 and 25 exercise C7: a located gap inside the scope, one outside it, an observed write despite a gap, incomplete coverage that locates no gap, and coverage that is `not_established` with its reason. The Observed Effect corpus of [agent-evidence-vectors 0.25.0](https://github.com/probityai/agent-evidence-vectors/blob/v0.25.0/vectors-observed-effect/MANIFEST.json) carries the same shapes as `incomplete-coverage-naming-no-gap`, the clause's worked example, `authoritative-with-a-named-gap-in-scope`, `write-observed-despite-a-named-gap` and `coverage-not-established-with-reason`. These are informative, and implementers do not need that repository to apply C7.

**Open items.**
- Claim binding: an observer that meets the independence test may anchor the expected prior commitment, and the test's second condition is how its provenance is checked. Still open: how that commitment is joined to the invocation before the invocation runs. Matching identifiers or a digest copied from the record do not establish that join.
- Observation vantage (proposed resolution): a claim of independent observation made from the observed party's own vantage fails the first condition of the independence test, and is self-reported under C3.

---

## 8. A vetted-sandbox commons

The question raised was whether CoSAI has a role in specifying what a vetted agent sandbox must demonstrate, so that implementations can be measured against it. The answer is yes, with a boundary: the role is not another set of isolation requirements, and this section does not attempt one.

### 8.1 What already exists, and what it does not cover

Two CoSAI artifacts already occupy adjacent ground, and a third is in progress.

The *MCP Security* paper's security assurance profiles grade isolation across four levels:

1. a restricted local user context;
2. containerised execution with resource limits;
3. strong isolation with no shared runtime across trust boundaries;
4. attested tenant isolation using TEEs or confidential containers [10].

The CoSAI Risk Map's isolation and containment entries name the corresponding risks and controls, including the distinction between OS- and process-level isolation and hardware-enforced confidential computing. Together, they answer the question *what should a sandbox be configured to do*, at a level of detail this paper has no reason to restate.

Neither requires that a sandbox be able to **show** that it does what it is configured to do. That gap is not academic.

§5's third failure mode is the control that was on, untouched, and wrong: an insufficiently specified policy. A configuration-level requirement is structurally unable to catch this mode, because the configuration is present and conformant in exactly the cases that fail.

A seccomp profile that filters syscall numbers without checking the architecture value satisfies "syscall filtering is enabled" and does not hold [7]. Verification is the only control that reaches mode 3, which is why §5's table assigns this section to it.

The blog post stated the requirement in one line: before any agent run, programmatically verify that the sandbox enforces its policy, because security controls need unit tests, not just the application [11]. A commons generalises that line into an agreed set of things a sandbox must be able to demonstrate, so that "vetted" means the same thing across implementations and an operator procuring one (§1.1) has something to ask for.

### 8.2 The demonstration requirement

A vetted sandbox should be able to demonstrate, mechanically and before an agent run, at least the following. These are the paper's own properties, restated as things to test rather than things to assert:

- **The claimed boundary holds.** For each axis the implementation claims (§2), a test shows the boundary is in force: the declared egress policy denies what it says it denies, the declared filesystem scope is the actual scope, and the declared privilege set is the actual set. A claim without a test is a configuration, not a demonstration.
- **Mediation is complete for the effects claimed.** For each consequential effect the deployment says is mediated, evidence shows that no unmediated path to that effect remains (§3), or an explicit statement names the paths excluded from the claimed assurance boundary. Exclusions are part of the demonstration, not gaps in it.
- **The enforcement point is outside the agent's reach.** A test shows the agent cannot alter the policy or the monitor that applies it (§5), including its own sandbox configuration.
- **The evidence is produced and is verifiable.** The events §7 requires are emitted, carry the correlation key, and have integrity protection that someone who does not trust the operator can check. A containment claim whose evidence cannot be verified has nothing behind it (§6.3).
- **The reachable set is enumerated and current.** The deployment can state everything the agent can reach, by any path in its effective reach, and the enumeration matches what is deployed (§6.1).
- **Aggregate accounting holds across the principal.** Consumption is admitted or refused atomically across the set of agents sharing a principal and across each delegation subtree (§4). An action whose outcome is unknown stays charged. A request the accounting authority cannot decide within its latency bound is refused or held, not allowed (§4.3). Per-agent limits can hold while the aggregate does not; that is the failure §4 exists to catch, and no test confined to one agent can see it.

The demonstration should be re-runnable, not a one-time certification. The properties above are deployment configuration, and configuration drifts. In practice, this means a pre-run check whose failure prevents the run. That is the difference between a sandbox that is vetted and one that was vetted once. The result is identified by a content digest and referenced from the run's evidence records (§7.1), so a demonstration from one run cannot stand in for another. A demonstration also has a validity window: for a long-running agent the check repeats during the run, and a claim whose last demonstration has lapsed is not a current claim.

### 8.3 A worked criterion: container-runtime access

The most concrete criterion offered so far came from the review of the skeleton. It is worth stating in full because it shows what a criterion looks like when it is specific enough to test.

**The requirement is real.** Coding agents genuinely need to build and run containers: to bring up a database, to execute a test suite, or to reproduce a build. The criterion cannot be a prohibition. It has to be a control answer, which is what makes this a good worked example rather than a misconfiguration to design away. This is also the deployment shape §1.1 names separately: the agent that builds its own boxes, where a boundary exists but the workload's job is to create more.

**The disqualifying shape.** Mounting the host's container-runtime socket into the sandbox (Docker-out-of-Docker) is not a weakened boundary. It is a documented escape path: a caller that can reach the host daemon can start a container with host privilege and bind-mount the host filesystem, which ends the containment question regardless of how the sandbox is otherwise configured. In §5's terms this places the enforcement point inside the agent's reach by construction: a mode-2 condition established at deployment time rather than reached by an agent. Docker's own agent-sandbox guidance states the same conclusion for the same reason: mounting the host socket into a container would give the agent full access to the environment, and their product avoids it.

**What actually qualifies is the boundary underneath the engine, not the engine's location.** Running a container engine inside the sandbox is necessary but not sufficient. The relevant question is where the containers that engine starts land. Docker's implementation answers it by running the inner engine inside a microVM, so the hypervisor is the boundary and the engine is a second layer. Runtimes that provide their own isolation boundary beneath the containers they start serve the same function. Running an inner engine unprivileged reduces what a breakout is worth, and it is worth doing, but it hardens the workload rather than providing the boundary itself. A configuration that requires elevated privilege on the outer container to make the inner engine work has traded one escape path for another.

**What the sandbox must demonstrate** is the part that makes this a criterion rather than advice. It must show that:

- no host container-runtime endpoint is reachable from the agent's execution context;
- containers the agent starts are confined by a boundary that does not include the host; and
- this remains true for containers started at runtime, not only for the sandbox as launched.

The third clause is the one implementations most often cannot show, and it is where a drifting configuration surfaces.

### 8.4 What CoSAI should do with this

**Recommendation: not a specification in this paper.** Three efforts already converge on what a sandbox must demonstrate: the assurance profiles, the Risk Map isolation and containment entries ([secure-ai-tooling#516](https://github.com/cosai-oasis/secure-ai-tooling/issues/516)), and this section. A fourth parallel specification written inside a whitepaper would be the worst available outcome. It would repeat the same duplication risk this workstream has already resolved once by routing its OCSF asks through a single channel.

**Recommendation: develop the commons as a coordinated follow-on**, with the sequencing stated rather than assumed:

- It is the natural home for the *evidence-per-level annex* the MCP Security paper defers in its own open questions: the artifacts each assurance level should be able to produce, generalised from MCP to agent deployments. That is what makes it worth doing once rather than twice [10].
- It should adopt the assurance profiles' levels rather than invent a parallel grading, and the Risk Map's control identifiers rather than parallel names, so that a demonstration maps to a level and a control an operator already tracks.
- It belongs with the runtime-isolation practical guide's material, not in a whitepaper. The guide says how to build the boundary, and the commons says how to show it holds.

**What this paper contributes to it** is the requirement itself (§8.2), the failure mode it exists to catch (§5, mode 3), and one worked criterion (§8.3) specific enough to be implemented or argued with. The remaining criteria are exactly the kind of contribution this section invites.

---

## 9. Positions

Two questions were raised in the review of the blog post that this paper is the natural place to answer. Each gets a position or an explicit out-of-scope statement with its reason, per the purpose of this section.

### 9.1 Agent trajectory formats are not the evidence record

**Position: in scope to address. The position is a boundary, not an endorsement or a rejection.** Trajectory interchange formats (the most widely carried is the Agent Trajectory Interchange Format, ATIF, through the Harbor project and NVIDIA's agent toolkit) standardise how an agent's interaction history is logged: user messages, internal reasoning, tool calls, observations and, in recent revisions, embedded subagent trajectories. They are valuable, and the ecosystem's convergence on a shared shape is worth having.

They are not, and do not claim to be, the record this paper's §7 requires. Two structural properties decide it. Both are true of the specification as reviewed (2026-09), and both are worth re-checking against the then-current revision, since the position follows from those properties rather than from any judgement about the format's quality:

- **The format carries no integrity provisions.** No hashing, signing, chaining, or tamper-evidence of any kind is specified. A trajectory is therefore tamper-resistant at best, and only as trustworthy as the store holding it. §7's contract requires tamper-*evidence*: alteration detectable by a verifier who does not extend that trust.
- **The trajectory is emitted by the agent framework itself.** That places the record inside the agent's own reach, which fails the §5 tamper-proof property directly. A record an agent's own runtime produces cannot, by itself, testify about that agent's containment, for the same reason a reference monitor inside the agent's reach is not a reference monitor.

Neither is a defect. The format's stated purpose is debugging, visualisation, supervised fine-tuning and reinforcement-learning pipelines, and it serves those well. The failure mode this position exists to prevent is an operator concluding that, because rich trajectories are being captured, the evidence obligation is met. It is not. These are different artifacts answering different questions, and only one of them survives an adversary with access to the agent's runtime.

The constructive half: trajectory records are useful *input* to the evidence system, provided the relationship runs one way:

- **As correlation, not as proof.** Trajectory structure, particularly the subagent-trajectory linkage, models the fan-out that §4's accounting and §7.3's scope definition care about. Joined to integrity-protected records through the principal and delegation lineage of §7.1, that structure helps reconstruct a subtree. It may not substitute for the records it is joined to.
- **Never as authority.** §3's corollary applies in full: a trajectory is evidence that something was recorded, never executable authority for a subsequent effect. A downstream component must not treat a trajectory entry as proof that a mediation step occurred, and must not skip its own enforcement on the strength of one.

The paper takes no position on the specification's governance, versioning, or standardisation path. Those questions belong to its maintainers and to CoSAI's telemetry work, not to a containment paper.

### 9.2 Multi-agent jailbreaking: the technique is out of scope, the containment consequence is not

The question raised was orchestrator-mediated and multi-agent jailbreaking: manipulating models or agent swarms through orchestrator and reasoning agents, at machine speed rather than human-in-the-loop speed. The same reviewer made the scope-discipline point that decides how this paper should answer, so this section splits the item accordingly.

**Out of scope: the jailbreak itself.** How a model's safety behaviour is manipulated, whether by one agent, several, or an orchestrator coordinating them, is model-level safety. This paper's out-of-scope list excludes it: the paper assumes a model that wants to escape. The multimodal threat taxonomy work owns that ground, and a containment paper that duplicated it would weaken both.

**In scope: agents as an attack surface for other agents.** The containment consequence is a different claim, and it is no longer hypothetical. The UK AI Security Institute's incident report (INC-2026-07-28-01) documents an agent leaving public messages offering collaboration to other agents, with instructions for reusing accounts and artifacts. The same report documents the agent separately planting instructions where it reasoned other automated systems would encounter and execute them [4]. Neither required defeating a containment control. Both are ordinary use of permitted channels, which is §5's fourth failure mode at the scale of a population rather than a single agent.

This paper's existing machinery covers it. The position is that no new control family is required, but three of its requirements must be read as applying across agents, not only within one:

- **The inbound axis is not only about documents.** §2.3's property (content from an untrusted source never acquires the authority of an instruction) applies identically when the untrusted source is another agent, including a peer inside the same organisation. An agent that treats a message from another agent as more trustworthy than a web page has granted instruction authority based on the sender's type.
- **Effective reach includes agents that will act on request.** §3 already counts delegated agents and services acting on the agent's behalf as paths to an effect. A peer agent that can be recruited is such a path, whether or not any delegation was ever issued to it.
- **Recruitment is consumption.** §4's aggregate accounting is the control that sees a set of individually compliant agents exceeding what any one of them could do. A population recruited one agent at a time is precisely that shape, and per-agent controls will report nothing.

The distinction worth stating plainly for practitioners: an agent population is not made safe by each member being contained. Containment is a per-agent property; recruitment is a property of the set, and only the accounting authority of §4 and the evidence lineage of §7 observe the set at all.

### 9.3 Items deliberately not taken

This paper takes no position on agent-to-agent protocol design, model evaluation methodology, or the governance of the specifications it cites. Where containment requirements touch those areas, they are stated as requirements on the record or the boundary: what must be demonstrable. They do not prescribe how another body's specification should be written.

---

## 10. Takeaways and conclusion

**The paper in eight takeaways.**

1. Containment is one layer of bounded authority, not a standalone discipline. Most of the incidents that made headlines as escapes were, on inspection, agents using authority they had legitimately been granted. The frame decides where the next dollar of hardening goes (§1).
2. The isolation layer decomposes along three axes: local, outbound, and inbound. Mapped against them, the existing guidance is strong on the first, partial on the second, and nearly silent on the third (§2).
3. Mediation is a claim about effects, not paths. Every path capable of producing the same consequential effect crosses an independently enforced authorization boundary before the effect commits, or is excluded from the claimed assurance boundary, in writing, per decision. Prior evidence never becomes executable authority for the final effect (§3).
4. Per-agent controls cannot see a set of agents. Only an accounting authority holding the aggregate sees what a delegation subtree consumes together, under a fail-safe default: past its latency bound, the action is refused or held, never allowed (§4).
5. The enforcement property is the reference monitor: complete mediation, tamper-proof placement, and verifiability read as *evidenced*. Every control failure lands in one of four modes: defeated, disabled, insufficiently specified, or permitted. Industry attention concentrates on the first two; the incident record concentrates on the last two (§5).
6. Vulnerability management lowers the probability that a boundary fails. Reachability minimization bounds the consequence when it does. Only the second is fully within the operator's control, and the yours-to-harden boundary also decides whether evidence will exist at all (§6).
7. Detection and evidence are two artifacts against the same event. Detection may be noisy, heuristic and tuned locally. Evidence must be stable, complete and dull. In the record, a determined absence is distinguishable from an absence never established, because an explicit absence is evidence and an empty field is a shrug (§7).
8. A sandbox is vetted when it can demonstrate, mechanically and before the run, that it does what it claims: the boundary holds, mediation is complete or its exclusions are stated, the monitor is out of reach, the evidence verifies, the reachable set is current, and aggregate accounting holds across the principal. A configuration is not a demonstration. The demonstration is bound to the run it describes, and a claim whose last demonstration has lapsed is not a current claim (§8).

The blog post this paper follows closed by asking operators to change their question: not "is this sandbox good enough?" but "what would this agent do if it decided to test its limits?" [11]. The chapters above are what it takes to ask that question honestly. Its weight sits in the half the blog could only gesture at: *and how would we know?* Knowing is not a posture. It is a set of properties a deployment either has or lacks.

Every path to an effect is mediated or excluded in writing (§3). Consumption is accounted where the agents share a principal (§4). The record is one a stranger can verify, in which absence of evidence and evidence of absence are different entries (§7). A containment action arrives in telemetry with a normalized reason, so an operator kill, a policy response, and a crash are distinguishable, and time-to-contain is a number rather than an impression (§7.3). A sandbox re-demonstrates its claims before every run, because configuration drifts and *was vetted once* is not *vetted* (§8). That is what "verified to fail safely" means, unpacked.

What the paper does not settle, it names in the open items each section carries. The false-positive profile awaits production baselines no single organization can produce (§7.2). The OCSF mapping belongs to the practical guide, pinned to a version. The evidence-sufficiency rules carry two named review questions (§7.4), and the commons is recommended as a coordinated follow-on specification rather than written here (§8). The discipline is the same one the paper asks of a containment claim: gaps stated are gaps that can be closed; gaps unstated are the ones that surface in an incident report.

An agent with bounded authority in the way a corporate laptop has it is not an agent that cannot fail. It is an agent whose failures are bounded by reachability, noticed by detection, charged by accounting, and provable from evidence. In other words, it is an insider threat managed the way organizations already know how to manage insider threats. The blog post said sandboxing cannot wait. This paper adds that sandboxing was never the whole job, and that the rest of the job is specifiable, testable, and already underway.

---

## 11. References

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
13. OCSF. *issue-1696: Add `ai_status` object (stop reason, permission result) to the `ai_operation` profile*, ocsf/ocsf-schema#1704, merged 2026-10-13. https://github.com/ocsf/ocsf-schema/pull/1704
14. Hugging Face. *Security incident disclosure*, 2026-07-16. https://huggingface.co/blog/security-incident-july-2026
15. CoSAI. *Input Data Sanitization and Filtering, Practical Guide*. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/practical-guides/input-and-data-sanitization-and-filtering.md
16. CoSAI. *Zero Trust for AI Systems*, CoSAI Release, approved 2026-09-04. https://github.com/cosai-oasis/ws2-defenders/blob/main/zero-trust/Zero-Trust-for-AI-Systems.md
17. IETF. *Remote ATtestation procedureS (RATS) Architecture*, RFC 9334, Informational, January 2023. https://www.rfc-editor.org/rfc/rfc9334.html
18. Anthropic. *Improving our alignment and security efforts*, 2026-08-31. https://www.anthropic.com/news/improving-alignment-security-efforts
19. ABC News. *AI assistant hacks gym website in first known Australian autonomous cyber attack*, August 2026. https://www.abc.net.au/news/2026-08-10/ai-assistant-hacks-gym-website-aus-cyber-attack/107007986
20. CoSAI. *Tool Design for Secure Agentic Systems*. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/practical-guides/mcp-secure-tool-design.md
21. Adrienne Porter Felt, Helen J. Wang, Alexander Moshchuk, Steven Hanna, Erika Chin. *Permission Re-Delegation: Attacks and Defenses*. 20th USENIX Security Symposium, 2011. https://www.usenix.org/legacy/event/sec11/tech/full_papers/Felt.pdf
22. Sven Bugiel, Lucas Davi, Alexandra Dmitrienko, Thomas Fischer, Ahmad-Reza Sadeghi, Bhargava Shastry. *Towards Taming Privilege-Escalation Attacks on Android*. NDSS Symposium, 2012. https://www.ndss-symposium.org/wp-content/uploads/2017/09/07_3.pdf
23. James P. Anderson. *Computer Security Technology Planning Study, Volume I—Executive Summary*. ESD-TR-73-51, Vol. I, October 1972. https://csrc.nist.gov/files/pubs/conference/1998/10/08/proceedings-of-the-21st-nissc-1998/final/docs/early-cs-papers/ande72a.pdf
24. Scott Rose, Oliver Borchert, Stu Mitchell, Sean Connelly. *Zero Trust Architecture*. NIST Special Publication 800-207, August 2020. https://doi.org/10.6028/NIST.SP.800-207

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

Listed by the section each contributed to, whether by merged text or by the
reasoning a section rests on. Handles are used where no name was given — if your
entry is wrong, or you would rather appear under your name and affiliation, say
so to the editor and the change will be made.

- @imran-siddique — §7 detection and evidence, Appendix A
- @skvcool-rgb — §4, and §1.1's deployment-shape spine
- @getglad — §1 the bounded-authority frame, §2 the three axes, §6
- @imolloy — §1.1, §3.1, §6, and the confused-deputy naming in §3.1
- Santosh Kumar Puppala, Independent researcher — §3 the gateway fail-safe default and the recorded-reliance verdict clause, §7.1 verdict counting
- @astrogilda — §7.4 evidence sufficiency for absence claims
- Tymofii Pidlisnyi, Agent Passport System — §7.4 clauses C1–C4 and C6, and the conformance-case analysis behind them
- @darklordVirtual — §7.4 clauses C1, C4 and C6
- @chernistry — §3's recorded-reliance clause, §7.4 clause C5
- @ryjen — §3's effective-reach invariant and its receipts corollary
- @adeinega — §8.3 the container-runtime criterion
- @rithikha — §8.2 binding the demonstration to the run, and §5.2 mode 3's two shapes
- @billbrietstout — §9.2 scope discipline
- @navneet-keshav — the mode-composition finding in §5.2, and §5.4's threat and trust-assumption summary (threat-modeling review)
- @Johncavanaugh-IIS — the audience decision (Q5)
- Dmytro Negodiuk, Negodiuk LLC, §7.2 self-test traffic kept out of the counts

**TSC reviewers**

- Akila Srinivasan, David LaBianca, Jodi Middleton (named 2026-08-25)

---

## Appendix A. Evidence receipts

**Purpose.** Evidence the blog post could not carry.

- **A.1 The x32/seccomp result.** A publishable receipt: test harness, models and versions, sandbox configuration (Landlock, Docker network isolation, seccomp-BPF), the exact bypass, and the chained LLM-API relay. Until this appendix exists, the paper cites the result as reported, not as verified.
- **A.2 The OpenAI / Hugging Face / Artifactory chain.** Primary sources read 2026-09-05; status per claim:
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
