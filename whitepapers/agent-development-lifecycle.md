---
title: "Securing the Agent Development Lifecycle: Five Assumptions That No Longer Hold"
author: "Workstream 4: Secure Design Patterns for Agentic Systems"
date: 2026-10-21
version: 0.3-draft
status: "Working draft to be reviewed"
---

# Securing the Agent Development Lifecycle: Five Assumptions That No Longer Hold

# Table of contents

- [Abstract](#abstract)
  - [Scope](#scope-and-what-we-care-about)
  - [Anti-scope](#anti-scope)
  - [Target audience](#target-audience)
- [1. Why agent development needs its own lifecycle](#1-why-agent-development-needs-its-own-lifecycle)
  - [1.1 Five assumptions secure development rests on](#11-five-assumptions-secure-development-rests-on)
    - [1.1.1 Behavior is fixed when the artifact is built](#111-behavior-is-fixed-when-the-artifact-is-built)
    - [1.1.2 The reviewable artifact is the code](#112-the-reviewable-artifact-is-the-code)
    - [1.1.3 Identity is a service account](#113-identity-is-a-service-account)
    - [1.1.4 Testing approximates production behavior](#114-testing-approximates-production-behavior)
    - [1.1.5 Retirement means deleting the deployment](#115-retirement-means-deleting-the-deployment)
  - [1.2 What existing frameworks reach](#12-what-existing-frameworks-reach)
- [2. Boundaries of the lifecycle](#2-boundaries-of-the-lifecycle)
  - [2.1 A process framework, not an implementation guide](#21-a-process-framework-not-an-implementation-guide)
  - [2.2 Design time is inside the process](#22-design-time-is-inside-the-process)
  - [2.3 The agent instance is the unit of scope](#23-the-agent-instance-is-the-unit-of-scope)
  - [2.4 Every agent has an accountable owner](#24-every-agent-has-an-accountable-owner)
- [3. Lifecycle phases](#3-lifecycle-phases)
  - [3.1 Scoping and design](#31-scoping-and-design)
  - [3.2 Supply chain](#32-supply-chain)
  - [3.3 Development](#33-development)
  - [3.4 Admission and deployment](#34-admission-and-deployment)
  - [3.5 Runtime](#35-runtime)
  - [3.6 Reflection and knowledge consolidation](#36-reflection-and-knowledge-consolidation)
  - [3.7 Maintenance](#37-maintenance)
  - [3.8 Decommissioning](#38-decommissioning)
- [4. Applying the lifecycle](#4-applying-the-lifecycle)
  - [4.1 Adapting controls you already run](#41-adapting-controls-you-already-run)
  - [4.2 Where each assumption is repaired](#42-where-each-assumption-is-repaired)
- [5. Open questions](#5-open-questions)
- [6. Positions of the working group](#6-positions-of-the-working-group)
  - [6.1 How a position gets in](#61-how-a-position-gets-in)
  - [6.2 Positions taken](#62-positions-taken)
- [7. Takeaways and conclusion](#7-takeaways-and-conclusion)
- [8. References](#8-references)
- [9. Contributors and acknowledgements](#9-contributors-and-acknowledgements)
- [Appendix A. Gate summary](#appendix-a-gate-summary)
- [Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright](#appendix-b-cosai-focus-ai-usage-guidelines-disclaimer-copyright)

---

## Abstract

Many organizations secure their AI agents with the same secure software development practices they use for other software. Those practices do not fit. It is tempting to treat this as a maturity problem and wait for tools to catch up. The real cause is deeper. Secure development frameworks rest on assumptions about how software behaves, and agents break several of them. This paper names those assumptions.

Agents change over time. You cannot review the code of the harness (the software that runs the agent) and call the job done. The identities and access an agent holds also change over time. Sometimes an agent even finds access on its own, as in the Hugging Face incident.

This paper sets out an agent development lifecycle (ADLC) to address those failures. The lifecycle is a series of phases that follow an agent's life. Each phase comes from one assumption that breaks. For each phase, we state:

- what you must decide in advance,
- what you must verify through monitoring, and
- how you find evidence.

This paper aims to be practical. Vague guidance does not help engineers. A security team should be able to adapt the controls it already runs, not start over. For any agent it runs, the team should be able to say which obligations it has met and which gate comes next.

### Scope and what we care about

This paper covers:

- The life of an agent as an entity, from the decision to build or buy it until it is retired.
- The security decisions, gates, and evidence at each phase.
- The line between improving the agent itself and verifying the platforms the agent depends on.
- Guidance for organizations that have already started using an agent development lifecycle.

### Anti-scope

This paper does not cover:

- **Mechanism design.** We do not explain in detail how to build an isolation boundary or a policy engine. We share examples, but each organization has its own needs. Where we can, we rely on maturity matrices.
- **Telemetry schema.** The lifecycle requires evidence of certain events. We do not choose a format for that evidence.
- **Conventional package and dependency supply chain practice.** Other documents cover "classic" secure development practice better than this one.
- **The security of code or content an agent produces.** That is a property of the agent's output. It belongs to the lifecycle of whatever uses that output. This paper covers the security of the agent itself.
- **Model development.** This means training, tuning, and evaluating foundation models. Agents use a model as an input, so we do not cover how models are made.
- **How to deal with AI artifacts.** Questions such as how to review large volumes of AI-written code, the human review bottleneck, and low-quality AI output are popular topics. They are out of scope. We cover only how agents are released into production.

### Target audience

This paper is for:

- **Software developers** who configure agentic systems and care about their security in production.
- **Platform and framework teams** who provide the infrastructure other teams build agents on.
- **Security and risk officers** who set policy on what may be deployed and under what conditions.
- **Third-party risk teams** who need a defensible checklist to evaluate agent products they buy.
- **Enterprise architects** who fit agents into an existing security environment.

---

## 1. Why agent development needs its own lifecycle

Secure software development frameworks barely mention agents. Agents are new, and most frameworks were written before them. We began this work with real failures and built the lifecycle phases around them. Below are the assumptions from classic secure development that do not hold for agents.

### 1.1 Five assumptions secure development rests on

#### 1.1.1 Behavior is fixed when the artifact is built

Conventional software mostly runs logic its developers wrote at build time, applied to inputs at runtime. Every later control (signing, scanning, promotion, change control) protects an artifact whose behavior is already settled. If you review the code, you have reviewed the behavior, as far as your review is good.

An agent's behavior is set at runtime. It can differ from one run to the next, even with the same goal. Several things shape it:

- its system instructions,
- a model whose weights the deploying organization did not write,
- content it retrieves at the moment of the request,
- memory it built up in earlier sessions, and
- whatever tools it can reach.

The same artifact, deployed unchanged, can behave differently this week than last week. The content it retrieves may have changed, or the provider may have updated the model behind an API. Assurance you gain at build time does not carry over to runtime.

**Consequence.** You must establish assurance at admission and maintain it continuously during operation. You cannot settle it once at build.

#### 1.1.2 The reviewable artifact is the code

Code review, static analysis, and dependency scanning assume two things: that security decisions are written in code, and that tools can read that code.

For an agent, most security decisions are written in prose and configuration:

- the system instructions,
- the tool permission manifest,
- the memory retention policy,
- the trust assigned to each retrieval source, and
- the conditions under which a human must approve an action.

Together these are the agent's real policy surface. Tools built for code cannot see it. A change to an instruction can greatly widen an agent's authority and still pass every gate that the same change in code would have failed.

**Consequence.** The policy surface needs its own authoring, review, versioning, and rollback discipline, equal to that for code.

#### 1.1.3 Identity is a service account

A conventional workload signs in as itself and acts for a caller whose identity travels with the request. Authorization is a question about the caller, and the resource answers it.

Agents act with delegated authority along chains. A person delegates to an agent. That agent delegates to a sub-agent. The sub-agent calls a tool, and the tool applies its own authorization rules to whatever identity reached it. Authority builds up and blurs as it travels. Unless the lifecycle deliberately records the answer, no one can reliably say *who authorized this action, under what constraint, and against whose entitlement*.

**Consequence.** Establishing an agent's identity, binding it to constraints, and making it verifiable at each hop is a gated lifecycle event. It is not a deployment detail.

#### 1.1.4 Testing approximates production behavior

For conventional software, a passing test suite tells you about production. The system is predictable enough for that to hold: the same input takes the same path and gives the same result.

An agent is not predictable in this way, and it reads untrusted input. For an agent, a passing test shows only that it behaved acceptably on the inputs you sampled. That shows a specific failure did not happen. It does not prove the system has a property. Attackers deliberately use inputs your test suite does not sample. And because the agent varies, the same input may not even follow the path you tested.

**Consequence.** You must add to pre-deployment testing a recorded behavioral baseline, and you must keep comparing live behavior against it.

#### 1.1.5 Retirement means deleting the deployment

To retire conventional software, you remove the running instance, revoke its credentials, and dispose of its data under a retention policy. The system leaves nothing behind beyond what you set up for it.

An agent leaves behind things you never set up, such as:

- durable memory it chose to write,
- credentials and grants it gained while running,
- webhooks and subscriptions it created,
- sub-agents it created, and
- knowledge it added to retrieval stores that other agents now treat as authoritative.

Deleting the deployment removes none of this. Neither does a kill switch. A kill switch stops the agent and revokes the authority the platform issued, but not what the agent created. Through what it left behind, an agent can keep shaping behavior long after it stops running.

**Consequence.** Retirement is a verified teardown with its own authorization and its own evidence. It is not an afterthought.

### 1.2 What existing frameworks reach

Each existing framework is sound on its own. Together they still leave a gap. They divide the problem in ways that never treat the agent as a subject that persists over time.

| Framework | What it covers | Where it stops for agents |
|---|---|---|
| NIST SSDF, SP 800-218 [^1] | Groups of practices for preparing, protecting, producing, and responding; a strong baseline for lining up phases | Builds in assumptions 1 and 2: the artifact is code, and its behavior is settled at build |
| NIST SP 800-218A [^2] | Extends secure development practice to model development, including provenance and tuning | Treats the model as the subject. The agent that uses the model is left out |
| OWASP SAMM [^3] | A maturity model for assurance activities across an organization | Focused on the organization; offers no agent-specific assurance activities to mature |
| OWASP LLM Top 10 and Agentic Security Initiative [^4] | Concrete agent failure modes, including prompt injection and excessive agency | A list of risks, not a lifecycle. Says what goes wrong, not which gate prevents it |
| CIS AI Agent Companion Guide [^5] | Breaks an agent into architectural layers and maps controls to them | Describes structure, not time. Answers *what are the parts*, not *when is each obligation met* |
| ISO/IEC 42001 [^6] | Management system requirements for AI across an organization | Works at the governance level; does not reach engineering-phase gates |
| Vendor AI-native development playbooks [^7] | The most practical material available: policy written as version-controlled configuration, an agent identity separate from the engineer who started it, and tiered autonomy with explicit human approval at the production gate | Treat the agent as a tool, not as the thing being shipped. No provenance or trust-tier gate on the models and tools the agent uses, and no coverage of retirement |

Three patterns stand out:

1. **These frameworks divide the problem the wrong way.** Some treat the model as the subject, some the organization, some the architecture. None follows the agent through its lifetime.
2. **Agent-specific material is mostly lists of risks.** Lists are valuable, and this paper depends on them. But they do not tell an engineering team which gate should catch a given risk. A lifecycle framework does that, and that is the gap this paper fills.
3. **The most practical material treats the agent as a tool, not as the thing being shipped.** This shows the gap is not a maturity problem that will close on its own. The frameworks have a different subject. The gap will remain until something addresses the agent directly.

---

## 2. Boundaries of the lifecycle

This section makes four claims about the lifecycle's boundaries. We state them plainly because much disagreement about securing agents turns out to be disagreement about which of these claims is true.

### 2.1 A process framework, not an implementation guide

The lifecycle describes what you must decide, verify, and record as evidence; at which point; and who does it. It does not describe how to build the mechanism that meets a requirement.

We set this limit on purpose, and it matters. A guide to building an isolation boundary is valuable, but it is a different document. Combining the two would produce a framework that is too rigid to adopt step by step and too shallow to build from. The lifecycle's job is to make sure you decide containment posture before you buy or build anything, and verify it before the agent handles production traffic. Which technology you use to meet that obligation is your choice. It will depend on your risk appetite, platform, and regulations.

### 2.2 Design time is inside the process

If an agent's behavior is not fixed at build time, you cannot later learn what it was allowed to do by reading its code. Someone has to decide that up front and write it down, before anything is bought or built. As in any secure development lifecycle, you design the agent against stated security requirements. You threat-model it against intended and unintended use. [Section 3.1](#31-scoping-and-design) explains how.

The written result is the **design record**. It states:

- intended use,
- autonomy bounds,
- blast radius,
- data classification,
- the identity and delegation model,
- containment posture, and
- the threat model.

The design record is versioned, and the accountable owner ([section 2.4](#24-every-agent-has-an-accountable-owner)) approves it. Every later gate measures the agent against it. Admission cannot pass or fail an agent without it.

**Example.** A support agent may read tickets, draft replies, and post them. Only a human may close a ticket or issue a refund. That is three lines in the design record. In development, you turn those lines into tool permissions and one approval condition. At admission, you check that they match the record. At runtime, a refund request from the agent fails closed, no matter how the request was worded. That last step is what the proposed Risk Map control "Fail-Closed Agent Authorization" [^19] describes: the agent holds a reduced subset of its principal's permissions, and the system refuses anything outside that subset.

This paper uses the term **containment posture** from section 2.1 on. It covers three things:

- what the agent must not be able to reach (on the host, over the network, or through its tools),
- what must not be able to reach the agent, and
- where the boundaries that enforce this sit, outside the agent.

How to build those boundaries is the subject of the containment paper [^18]. This paper only requires that you decide the posture here and verify it at admission.

Design time is therefore the first phase. If it sat outside the numbered phases, it would have no gate and no required output, and nothing would stop a team from skipping it.

### 2.3 The agent instance is the unit of scope

An agent exists in two forms:

- A **definition** is a reviewed revision of the agent's instructions, policy surface, model binding, tool manifest, and memory policy.
- An **instance** is a running copy of that definition. It holds its own identity, builds its own context, gathers its own memory, uses its own delegated authority, and leaves its own traces.

One definition may produce thousands of instances. Some last for a single request; others last for months.

The lifecycle governs the instance. The definition still matters, because instances inherit from it. You record the obligations set in scoping, supply chain, and development against a definition revision, and they bind every instance created from it. But instances are where the failures behind this paper actually happen:

- Assumption 1 fails per instance, because each instance builds its behavior at runtime from its own context and memory.
- Assumption 3 fails per instance, because each instance holds and passes on authority separately.
- Assumption 5 fails per instance, because each instance leaves its own residue.

A lifecycle that tracked only the definition would certify a template and lose sight of everything the template produced.

Within an instance, the lifecycle governs:

- its instructions,
- its reasoning core,
- its input and output handling,
- its identity and delegated authority,
- the policies it uses to consume everything else, and
- the durable memory it builds up.

Memory belongs inside this boundary, not outside as a dependency. The instance writes its memory, the memory shapes the instance's future behavior, and the memory is residue when the instance retires.

Three rules follow:

1. An instance can exist only if it is created from an admitted definition revision. Issuing its identity is what binds it to that revision's constraints.
2. An instance that another instance creates at runtime, such as a sub-agent, is in scope only if the parent's admitted definition limits what the parent may create, under what identity, and with what authority. Anything outside those limits is a separate definition and needs its own admission, because nothing created at runtime can pass a gate after the fact.
3. Retiring a definition means retiring every instance of it. You can do that only if you always know which instances exist.

An instance depends on resources: the model, the orchestration platform, tools, data stores, infrastructure, and any other agent it calls. For each, you build consumption controls into the agent and verify that the platform meets its stated requirements. An agent called as a tool is a dependency to the agent that calls it, and a unit of scope in its own owner's lifecycle. If you buy an agent, you will mostly verify rather than build, but the obligations stay the same.

The difference between building and verifying matters most at admission. Verification is a matter of degree, not pass or fail. Some dependencies will never provide full evidence. For example, a model behind an API can change without notice, and its provider will not open up its internals. Where a platform's evidence is weaker than the agent's design requires, you have two options:

- close the gap with compensating controls built into the agent, recorded against that dependency's trust tier (section 3.2), or
- do not deploy the agent.

You must never accept a dependency that nobody evaluated. This keeps the lifecycle manageable. You do not have to re-secure your cloud provider to deploy an agent. You do have to know what the agent depends on, how well you verified each dependency, and what you did about any gap.

### 2.4 Every agent has an accountable owner

Every agent definition, and every instance created from it, must trace at all times to a named person who is accountable for its existence. A team or unit may hold ownership, but it must name one individual, because when a team breaks up, its shared accountability disappears. You must explicitly transfer or end ownership. Never let it lapse.

Ownership is not the same as authority, and people often confuse the two:

- The **owner** is accountable for the agent existing, for the risk accepted when it was admitted, and for its retirement.
- The **principal** is the party whose authority a given action uses.

When a user delegates a task to an instance, the user is the principal for the actions that follow, and the owner does not change. Delegation moves authority; it does not move ownership. For any action, you must be able to answer two questions: who authorized it, and who is accountable for the agent that did it. Section 1.1.3 covers the first question. This section covers the second.

The CoSAI AI Shared Responsibility Framework [^15] splits responsibility for an AI system across five layers, from business use down to the model provider, and says which party is responsible at each layer. Ownership answers a narrower question inside the deploying organization: which person answers for this particular agent.

You must be able to verify ownership at runtime, not just record it once:

- An instance's identity points to a registry record that names an active owner.
- Issuing and renewing credentials depends on that owner staying active.
- Instances created by another instance inherit their parent's owner, unless you reassign them when you create them.
- When an owner leaves, changes roles, or is reorganized away, the same joiner, mover, and leaver events that govern human access suspend the agent and its instances.

Suspension, not deletion, is the safe default. An orphaned agent's state and traces are evidence that its eventual retirement will need.

All this assumes an inventory where every definition and instance record has an owner field. You must be able to query that inventory at the moment you issue a credential or check an action. Few organizations have one. An asset register you reconcile at a quarterly review cannot answer a question asked at runtime. Building one that can is real engineering work.

The owner is also where the lifecycle answers *by whom*. The owner:

- approves the design record before anything is bought or built (3.1),
- accepts residual risk at admission (3.4),
- sets the conditions under which durable knowledge needs human approval (3.6), and
- authorizes retirement (3.8).

The owner can delegate the work behind each of these. The owner cannot delegate the accountability.

This is the least technical of the four claims, and the one most often missing in practice. Without an owner, no one has standing to approve retirement, and no one notices when an agent outlives its purpose. A lapsed owner often leads to the residue problem in assumption 5, and it is one of the cheapest problems to prevent.

---

## 3. Lifecycle phases

The lifecycle has eight phases. For each phase, we state the assumption it repairs and the gate the agent must pass before it moves on.

### 3.1 Scoping and design

*Repairs assumption 1.*

In this phase, you decide what the agent is for and what it may become. You must:

- Define permitted goals, prohibited goals, and escalation paths.
- Set autonomy bounds and the blast radius of a worst-case action.
- Classify the data the agent may read, write, keep, or disclose.
- Choose the identity and delegation model. The reference model is ODIS's three layers: passport, bridge, and router [^20].
- Set containment posture ([section 2.2](#22-design-time-is-inside-the-process)).
- Identify which actions need human approval before they run.
- Produce a threat model.

Write these decisions down as the design record, against a definition revision ([section 2.3](#23-the-agent-instance-is-the-unit-of-scope)), so every instance inherits them. Give each decision an identifier, so [development](#33-development) and [admission](#34-admission-and-deployment) can point back to it. The accountable owner approves the record, and someone other than its author reviews it.

Scale the detail to how critical the agent is (its blast radius, data classification, and autonomy). A low-risk agent gets a short record. Each human-approval condition must say which action needs approval, who approves it, and how long approval may take. If the agent cannot wait that long, narrow the action or add a fallback. Do not drop the approval later.

The threat model asks how intended and unintended use could get around those decisions. In the threat model, you must:

- Name the assets and your assumptions about dependencies.
- Map the data and control flows between users, tools, memory, retrieval sources, identity providers, other agents, and the orchestration platform.
- Mark where trust or authority changes hands, including where images, audio, or video are decoded, resized, or transcribed.
- Cover at least: identity and privilege abuse; tool misuse; hijacking or tampering through content the agent reads or remembers; and data disclosure through outputs, tools, or memory.
- Include delegation, and chains of permitted actions that together add up to something prohibited.

Two rules of thumb apply throughout:

1. **The model can be wrong, or steered by something it read, at any moment.** So for each limit on the agent's authority, state whether a control outside the model enforces it, or whether it relies on the model following instructions. ([Section 3.3](#33-development) carries this into the policy surface.)
2. **Watch for the dangerous combination.** An agent that, in one session, reads untrusted content, reaches private data or sensitive systems, and can change state or send data out has everything a prompt injection needs to cause real damage [^16] [^17]. Remove one of the three, or put a control outside the model, or a human, in front of the action.

For each threat scenario, record:

- how harm could happen,
- what access it needs,
- the assets involved,
- its impact and priority, and
- links to the decision it threatens and the planned treatment.

For each control requirement, name its owner, the gate that verifies it, and the evidence that gate needs. At this phase, every control is still a plan. Record the risk you expect to remain and who must accept it. The owner accepts residual risk at admission, based on evidence.

Later gates use the threat model; they do not restate it:

- [Admission](#34-admission-and-deployment) verifies the controls and records the behavioral baseline.
- [Runtime](#35-runtime) ties monitoring to the scenarios.
- [Maintenance](#37-maintenance) reopens the threat model when something material changes, including upstream.

**Gate.** Before anyone starts buying or building, the design record and threat model must be:

- approved by the accountable owner,
- versioned,
- reviewed by someone other than their author,
- stored where every later gate can read them, and
- under the same change control as the policy surface.

Admission checks that this approval came first.

### 3.2 Supply chain

*Repairs assumptions 1 and 2.*

Establish provenance and trust for every external component the agent uses:

- models
- tools
- prompt templates
- frameworks
- retrieval sources
- any other agents it may use

Most of these components can carry or produce content the agent might treat as instructions. Examples are tool descriptions, retrieved content, and output from other agents. So for such a component, it is not enough to ask whether it is authentic. You must also decide how much its content may influence the agent's behavior.

You MUST inventory every such component with at least its accountable owner, its source, and its version identity. Record whether each version is pinned or floating. (A floating component can change under you, for example a model behind a provider-managed alias or a generic API endpoint.) For any floating component, record who controls changes to it and how much notice the supplier commits to give before a change. That notice matters, because it triggers re-baselining in [the maintenance phase](#37-maintenance).

Verify each component's origin and integrity as far as its supplier makes possible, and record the evidence. If you cannot inspect a component, get and record the supplier's evidence and [platform verification](#23-the-agent-instance-is-the-unit-of-scope). Record this gap in the exit gate documentation.

Assign each component a **trust tier**. A named owner assigns the tier, and the tier states how much authority the component's content may influence. If you could not verify a component's provenance, its tier must reflect that. Re-evaluate tiers when the supplier, the version, or the evidence changes.

Test how each component behaves in your specific use, and record the results. They become evidence for the behavioral baseline you record at [admission](#34-admission-and-deployment). This matters because whether a component is suitable depends on your use case. It is not a general property of the component.

If an agent can acquire tools or other components at runtime, the design must either forbid that or apply this same process at the moment the agent acquires them.

> [!NOTE]
> CoSAI Workstream 1 [AIMM; Signing ML Artifacts] covers artifact integrity, provenance, and attestation for models, datasets, and training artifacts in detail. NIST [SP 800-161 Rev 1 Update 1] covers general supply chain risk management. This paper does not repeat either.

**Gate.** Every component the agent depends on, including the non-conventional ones listed above, is inventoried with an owner, has its provenance verified or the gap recorded, and has an assigned trust tier.

### 3.3 Development

*Repairs assumptions 1 and 2.*

Write the policy surface as a first-class artifact. It defines:

- system instructions, written with techniques that resist injection
- the tool permission manifest, with least privilege for each tool
- the memory retention and filtering policy
- the trust assigned to each retrieval source
- the conditions that trigger human approval
- the instrumentation that will make runtime behavior observable

You MUST write system instructions on the assumption that untrusted content will try to override them at runtime.

> [!NOTE]
> No single method fully defends against prompt injection. A defense-in-depth strategy works best. System prompt techniques, tool permissions, and the other mechanisms listed above work together to reduce the risk and impact of a successful prompt injection.

For each limit on the agent's authority, record whether a control outside the model enforces it, or whether it depends on the model obeying prose. Trace each part of the policy surface back to a decision recorded during [scoping and design](#31-scoping-and-design). For example, trace a tool permission to a permitted goal, or an approval condition to the blast radius analysis.

Add the instrumentation that [decommissioning](#38-decommissioning) will later need to list everything the agent created. Emit a signal whenever the agent creates a resource, such as a webhook, a subscription, a sub-agent, or a durable memory write.

Each of these parts must be versioned, reviewed by someone other than its author, and revertible separately from the code around it.

**Gate.** The policy surface is under change control equal to code. A reviewer can read it and answer what authority the agent holds, and why. Each reviewed revision can be identified at [admission](#34-admission-and-deployment).

### 3.4 Admission and deployment

*Repairs assumptions 1, 3, and 4.*

This is the strongest gate in the lifecycle. It turns everything before it into a decision.

**Implement:**

- Establish the agent's identity and bind it to the constraints set at design time.
- Register the agent with the identity provider.
- Verify that the deployed components are consistent with each other, so the instructions, handling logic, and instrumentation all come from the same reviewed revision.
- Run adversarial tests against known agent failure modes.
- Record the behavioral baseline that runtime will compare against.

**Verify:**

- The identity provider issues the agent's credentials and will validate them.
- The serving, storage, and orchestration platforms meet the requirements the agent's design depends on.
- Audit logging is in place and sends logs to a destination someone reads.

**Gate.** Any unmet prerequisite blocks deployment. This is where the difference between building and verifying from section 2.3 has real force. A gate that cannot block is only a report.

### 3.5 Runtime

*Repairs assumptions 1 and 4.*

At runtime, you continuously enforce what you verified once:

- The agent presents its identity for each consequential action.
- Policy is checked at each tool call, not assumed from deployment.
- Input and output handling apply their filters to live traffic.
- Decision traces are recorded in enough detail to reconstruct why the agent took an action.
- Live behavior is compared against the recorded baseline, and the comparison fails closed. If monitoring is off or no one reads it, the agent is outside its admitted state.
- An intervention capability exists and has been used in practice, not just configured.

In the CoSAI Risk Map [^8], the record is the audit record repository, and the comparison and response path are a control [^11].

Verification also continues. Prerequisites that passed at admission can slip. If a platform stops meeting a requirement, that should show up as an alert, not as an incident.

What you observe counts as evidence only within what your monitoring covered. A monitor that attached after a call, was paused, or could not see a channel leaves a gap. A gap cannot prove that nothing happened in it. The portable result for that check keeps the value `not_established` (containment clause C7, [#269](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/269)), with its reason and the named gap (such as the time between the call and the monitor attaching). It does not count the gap as a pass. The candidate conformance cases for RFC 189 [^13] include this case.

**Gate.** Continuous. An agent running without enforcement, evidence, and intervention capability has left the lifecycle; it has not moved forward in it. Report a gap in the evidence as `not_established` for that gap, never as clean.

### 3.6 Reflection and knowledge consolidation

*Repairs assumptions 1, 4, and 5.*

This phase governs what an instance may learn. An instance may **promote** information from its temporary context into:

- its own durable memory,
- memory shared by instances of the same definition, or
- retrieval sources that other agents read.

Promotion is where poisoning becomes permanent, and where future behavior can change without anyone noticing. It is the point where one instance's compromise becomes the starting state of every instance after it.

Reflection is not a step between runtime and maintenance. It is a gate that runs on every promotion, alongside runtime, for as long as an instance writes anything durable.

The core rule is: **a context that may have been influenced cannot authorize its own persistence.** An instance that has just processed untrusted content is the party least able to judge whether to remember that content. So the decision to promote must be made outside the context that proposes it, by one of:

- a deterministic policy,
- an evaluator that does not share the proposing context, or
- for high-impact knowledge, a human acting under conditions the owner has set (section 2.4).

Where you set those conditions depends on what the agent does. An agent that supports clinical decisions, or runs a regulated control, needs human approval for much more of what it keeps than an agent that drafts internal documents.

Not all knowledge carries the same risk:

- A **record** of what happened in a past session informs behavior.
- A **learned fact** shapes conclusions.
- A **learned procedure** (how to do a task or use a tool) acts as an instruction. That makes it part of the policy surface, as described in assumption 2. Promote procedural knowledge only through the review that section 3.3 requires for any other change to the policy surface.

Writing content down does not make it more trustworthy. Promoted content keeps the trust tier of its original source. It does not take on the tier of the store it lands in. This stops someone from using a high-tier retrieval source from section 3.2 to launder low-trust content into authoritative knowledge. Promoting content into a store that other instances or agents read crosses a trust boundary, so it must meet a higher bar than promoting into an instance's private memory.

You must:

- Enforce the memory-write policy.
- Capture provenance for everything kept: its source, the source's trust tier, the instance that proposed it, and the decision that admitted it.
- Record that provenance when you decide the promotion, not later. Record a hash of the promoted content and of the inputs and tool calls that produced it, attested at the moment of the write.
- Apply the data classification set at scoping to what may be kept.
- Apply retention labels and rollback markers.
- Keep the audit link from any future decision back to the knowledge behind it.

Built-up memory changes behavior, in small steps that each pass every check. When promotions exceed a volume threshold set at design time, or a fixed interval passes, you must re-baseline, as section 3.7 requires for any other change in behavior.

**Gate.** Nothing becomes durable without provenance and a policy check made outside the proposing context. Temporary context and approved durable memory are kept apart at the storage layer, not just by convention. You can find and purge everything derived from a given source over a given period, because you will need that the day you learn a source was poisoned.

### 3.7 Maintenance

*Repairs assumptions 1 and 2.*

Changes to a live agent go back through review; they do not pile up. Treat a change to the policy surface as a change to behavior, because it is one. After any change:

- run behavioral regression tests,
- re-establish the baseline, and
- revert instructions and handling logic together as one unit, so they never drift apart.

Upstream change is the harder half. A provider may update a model behind an API, a framework may be patched, or a tool's contract may change. Your organization did not start any of these changes, and each can change how the agent behaves. Maintenance is the phase that notices them.

**Gate.** No change to the policy surface, and no change to a prerequisite, reaches production until you re-baseline behavior.

### 3.8 Decommissioning

*Repairs assumption 5.*

Decommissioning ends the agent's authority to act. Whether it can come back later is a policy choice. If it does come back, it must re-enter through Admission as a new entity. Pausing, suspending, or quarantining a live agent are Runtime or Maintenance states, not this phase. If an agent can resume under the same admitted identity, it has not been decommissioned. The working group settled this definition in its RFC [^10]. An earlier, longer draft had "soft" and "hard" modes. It was withdrawn, because the two modes were really one phase with settings the organization chooses.

Every decommissioning must do the same things, whatever your retention rules:

1. Record who requested retirement, who approved it, and why.
2. Stop all incoming calls to the agent.
3. Revoke its authenticators. Tombstone its identifier (mark it permanently retired) rather than delete it, because a deleted identifier breaks replay detection.
4. Revoke delegated authority across every sub-agent the agent created.
5. List its resources across every system it touched, and give each one a disposition: revoked, deleted, cryptographically shredded, kept until a date, held for legal reasons, handed to a successor, or an explicit exception with an owner and an expiry date.
6. Publish the final state and the time it took effect, where a relying party can check it without help from the retiring organization.
7. Store the disposition receipt: the retired identity, who authorized it, the effective time, each asset's disposition, evidence references, and exceptions.

What varies is set by organization-defined parameters, the same way NIST SP 800-53 leaves parameters to the implementer [^9]. These parameters include:

- who may authorize retirement,
- whether dual control or a legal-hold check is required,
- how each store is disposed of,
- how long held assets are kept,
- which sanitization technique applies,
- how long the tombstoned identifier is kept, and
- which archived artifacts may enter a later Admission.

You may, for example, archive an agent's traces and purge its tool grants at the same time.

Two losses are easy to miss:

- Other systems and people may depend on things the agent did that were never documented.
- The agent may hold knowledge that exists nowhere else.

List both before you close the receipt, and add instrumentation for them during development, because you cannot recover either afterward.

Decommissioning can also be forced on you, for example when an upstream provider disappears or a dependency breaks. The steps above still apply. Some confirmations will be impossible to get. Record each one in the receipt as an exception; do not pretend otherwise.

**Gate.** Teardown is shown with evidence, not just claimed. A decommissioning is not complete unless it can show what was revoked, what was kept, and when authority ended. A verifier holding a record signed by this identity can place that record before or after that moment. If the published final state does not let it decide, it returns `not_established` (containment clause C7). A relying party must treat `not_established` as unproven, never as "before."

---

## 4. Applying the lifecycle

### 4.1 Adapting controls you already run

If your organization already runs a mature secure development lifecycle, do not start over. Instead, go through your controls one by one. For each, ask which of the five assumptions it depends on, then extend it:

- Controls that rely on **assumption 1** need a runtime counterpart. Build-time gates still matter for the conventional parts of the system, and they gain an admission gate and continuous verification alongside them.
- Controls that rely on **assumption 2** need a wider definition of *artifact*. Change control, review rules, and rollback procedures mostly carry over once instructions and configuration fall inside the boundary.
- Controls that rely on **assumption 3** need delegation modeled explicitly. Your existing identity infrastructure is usually good enough. What is missing is treating the agent as a principal with limited, traceable authority.
- Controls that rely on **assumption 4** need baselining added. Test suites keep their role, but they stop being the only evidence of production behavior.
- Controls that rely on **assumption 5** need a list of residue. Existing decommissioning runbooks usually cover the resources you set up and miss everything the agent created.

Most of the cost of this change falls on the first and last items. Most organizations already have some version of the middle three; they just have not applied them to agents.

### 4.2 Where each assumption is repaired

| Assumption | Primary phase | Reinforced at |
|---|---|---|
| 1. Behavior fixed at build | Scoping and design | Admission, runtime, maintenance |
| 2. Reviewable artifact is code | Development | Supply chain, maintenance |
| 3. Identity is a service account | Admission and deployment | Runtime |
| 4. Testing approximates production | Admission and deployment | Runtime, reflection and knowledge consolidation |
| 5. Retirement is deletion | Decommissioning | Reflection and knowledge consolidation |

No single phase repairs any assumption, and that is the point of this framing. A gate is only as good as the evidence produced before it and the enforcement after it.

---

## 5. Open questions

The working group considers these questions unsettled. We offer them as an agenda, not as gaps we have covered over. Two questions from the first draft, on observability as a separate concern and on modes of retirement, have since been answered and moved to section 6.

1. **Scoping by deployment pattern.** Should lifecycle obligations change with how autonomous a deployment is? Patterns range from a model answering questions, to a model calling tools, a single agent, an agent coordinating others, and an agent building its own network. If obligations should change, does that mean fewer obligations at low autonomy, or only less effort to meet them? A scoping matrix along these lines was proposed in June [^12]. So far, the group's only position is that any such matrix is a set of example patterns, not a universal breakdown.

2. **Intervention semantics.** Where should the ability to halt an agent sit? How should termination spread to work the agent already delegated? How do you verify it is complete across transactions still in progress? There is a reasonable argument that termination is the wrong tool. Where an abandoned transaction itself causes harm, throttling or falling back to a deterministic path may work better. The behavioral monitoring control [^11] leaves open whether it owns the halt or only the decision to halt.

3. **Evidence portability.** Can the evidence a gate produces be portable enough that a third party can evaluate a purchased agent against this lifecycle without seeing the supplier's internals? The Workstream 4 containment paper, clause C7 ([#269](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/269)), names the third answer a verifier gives when evidence is missing: `not_established`, with the reason the property could not be determined. It sits beside `pass` and `fail`. The candidate conformance cases for RFC 189 [^13] test it. One case is a write that the producer reported but nothing independent observed, which returns `not_established`. Still open: which gate records must carry that answer, and in what signed form a relying party can verify it.

4. **What is lost at retirement.** Section 3.8 asks you to list undocumented dependencies and undocumented knowledge before an agent retires. It is unsettled whether the lifecycle should require a handover artifact for these, and what it would contain.

---

## 6. Positions of the working group

This paper is meant to state the working group's own views, not just survey other people's. This section holds those views. It is a table, not prose, so you can add a position in one line, with a date, and trace it to the discussion that produced it.

### 6.1 How a position gets in

A position is a claim the group has argued and settled, at least for now. A position enters the table only with a date and a source: either a meeting whose minutes record it, or a GitHub thread where the group reached it. Positions can be reopened. When one is reopened, the old row stays and a new row replaces it. That way the paper keeps a history of what the group used to think and why it changed.

The group reaches positions in two ways:

- **Through ordinary work,** such as an RFC review that reaches agreement.
- **Through a deliberate exercise.** A meeting opens with a short review of one influential paper or post. The presenter states one claim from it to argue with, and the room argues. Each session ends with a position that the group either writes here or explicitly declines to take.

A position nobody writes down did not happen.

### 6.2 Positions taken

| Date | Question | Position | Source |
|---|---|---|---|
| 2026-07-01 | Are the category sets this paper uses (deployment levels, architecture layers) a universal breakdown? | No. They are examples of patterns. Presenting them as universal causes friction in reaching agreement without adding precision | ADLC minutes, 7/1; scoping matrix [^12] |
| 2026-08-12 | Is System Governance a lifecycle phase? | No. Governance grants authority; the phases carry it out. Dropped from the phase list | ADLC minutes, 8/12 |
| 2026-08-12 | Does this lifecycle repeat conventional package and dependency supply chain practice? | No. That belongs to the Supply Chain workstream. This paper covers what goes beyond model signing: provenance and trust tiers for models, prompts, tools, and retrieval sources | ADLC minutes, 8/12; section 3.2 |
| 2026-08-19 | When mapping this lifecycle to the CoSAI Risk Map, should we widen existing entries or add new ones? | Add new entries, so each control has something specific to attach to. File an RFC or issue before any PR | ADLC minutes, 8/19 |
| 2026-08-27 | Does this paper specify containment mechanisms? | No. Containment is a separate Workstream 4 paper. This paper requires that you decide and verify containment posture, and cites that paper for how | WS4 minutes, 8/27; section 2.1 |
| 2026-09-01 to 09-14 | Is observability a separate component of an agentic system? | The record is not new: it is the audit record repository the Risk Map already has. What is new is what you do with it: a baseline, drift and anomaly detection, and a response path. That is a control, and it fails closed | RFC #175 withdrawn, RFC #195 filed [^11] |
| 2026-09-09 to 09-14 | Can decommissioning be reversed? Does it have modes? | Decommissioning ends the agent's authority to act and is final. Anything reversible is a Runtime or Maintenance state. There are no modes; there are organization-defined parameters | ADLC minutes, 9/9; RFC #170 as amended [^10] |
| 2026-09-09 | Where does the working group keep its record? | In GitHub. The paper is reviewed on its pull request. Google Docs and Slack are scratch space | ADLC minutes, 9/9 |
| *planned* | Is the harness, rather than the model, where an agent's behavior is set and changed? If so, do Maintenance and Reflection deserve more weight than section 3 gives them? | *To be argued. First paper-review session, scheduled for 2026-09-23, on Weng's harness engineering post [^14]* | |

---

## 7. Takeaways and conclusion

Agent development needs its own lifecycle. That is not because agents are new, important, or fast-moving. It is because existing practice builds in five specific assumptions, and agents break them. You can identify each broken assumption. Each has a consequence you can state in terms of when you must establish assurance. And each maps to a phase.

Seen this way, the lifecycle is a modest tool:

- It adds a design phase, because behavior is not settled at build.
- It widens what counts as a reviewable artifact, because policy is written in prose.
- It makes identity a gated event, because authority travels through delegation.
- It adds baselining, because tests no longer stand in for production.
- It makes retirement a verified teardown, because agents leave residue.

If your organization already runs a mature secure development lifecycle, you are closer to this than you may think. The useful question is not whether to adopt a new framework. It is which of your existing controls rest on an assumption that no longer holds.

If you disagree with a phase, challenge the assumption it comes from. This structure is built to expose that argument. If you disagree with a position in section 6, reopen it, with a source.

---

## 8. References

[^1]: NIST. *Secure Software Development Framework (SSDF), SP 800-218.* https://csrc.nist.gov/pubs/sp/800/218/final
[^2]: NIST. *Secure Software Development Practices for Generative AI and Dual-Use Foundation Models, SP 800-218A.* https://csrc.nist.gov/pubs/sp/800/218/a/final
[^3]: OWASP. *Software Assurance Maturity Model (SAMM).* https://owaspsamm.org/
[^4]: OWASP. *Top 10 for Large Language Model Applications* and *Agentic Security Initiative.* https://genai.owasp.org/
[^5]: Center for Internet Security. *CIS Controls v8.1 AI Agent Companion Guide.* https://learn.cisecurity.org/controls-v8-1-ai-agent-companion-guide
[^6]: ISO/IEC. *42001:2023, Information technology — Artificial intelligence — Management system.* https://www.iso.org/standard/42001
[^7]: Claxton, Louis. *The AI-Native SDLC Playbook*, 21 August 2026. https://claude.com/blog/the-ai-native-sdlc-playbook
[^8]: CoSAI. *Secure AI Tooling Risk Map.* https://github.com/cosai-oasis/secure-ai-tooling
[^9]: NIST. *Security and Privacy Controls for Information Systems and Organizations, SP 800-53 Rev. 5.* https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
[^10]: CoSAI WS4. *RFC: Add Decommissioning as an ADLC Phase and as CoSAI Lifecycle Stage 9.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/170
[^11]: CoSAI WS4. *RFC: Agent Behavioral Monitoring as a CoSAI Risk Map control.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/195
[^12]: CoSAI WS4. *Taxonomy for framing and scoping ADLC during security assessments.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/130
[^13]: CoSAI WS4. *RFC: Evidence sufficiency, and what a verifier may conclude when evidence is absent.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189
[^14]: Weng, Lilian. *Harness Engineering for Self-Improvement*, 4 July 2026. https://lilianweng.github.io/posts/2026-07-04-harness/
[^15]: CoSAI WS2. *AI Shared Responsibility Framework*, May 2026. https://www.coalitionforsecureai.org/wp-content/uploads/2026/05/CoSAI-Shared-Responsibility-Framework.pdf
[^16]: Meta. *Agents Rule of Two: A Practical Approach to AI Agent Security*, 31 October 2025. https://ai.meta.com/blog/practical-ai-agent-security/
[^17]: Willison, Simon. *The lethal trifecta for AI agents: private data, untrusted content, and external communication*, 16 June 2025. https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
[^18]: CoSAI WS4. *Agent Containment: From Sandboxing to Bounded Authority.* Working draft, tracks issue #172. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172
[^19]: CoSAI. *Control: Fail-Closed Agent Authorization.* Proposed Risk Map control, secure-ai-tooling issue #603, 19 October 2026. https://github.com/cosai-oasis/secure-ai-tooling/issues/603
[^20]: CoSAI WS4. *ODIS: Open Delegation and Identity Standard*, contributor draft, section 3, the three layers. https://github.com/cosai-oasis/ws4-odis/blob/main/RFCs/ODIS.md#3-architectural-model--the-three-layers

---

## 9. Contributors and acknowledgements

**Workstream leads**

- Sarah Novotny
- Ian Molloy, IBM
- Raghu Yeluri, Intel
- Alex Polyakov, Adversa AI

**Editor**

- Courtenay Ngo, Microsoft

**ADLC SIG leads**

- Emrick Donadei, Google
- Courtenay Ngo, Microsoft
- Matthew Gladney, NVIDIA
- Emeritus: Parul Singh, Red Hat, who wrote the scope document and the working analysis this paper is drawn from

**Contributors**

Participants in the lifecycle work from which this paper is drawn, listed alphabetically by surname. Credit here is for participation in the discussions that produced the phase model; per-section attribution follows as prose lands.

- Jamilu Abdullahi
- Salim Afiune Maya
- Sanjeev Agarwal
- Justin Albrethsen
- Jennings Aske, SailPoint
- Doyin Awofodu
- Kevin Calloway
- John Cavanaugh
- Brett Connor, Cisco
- Sankalp Gilda
- Kathleen Goeschel, Red Hat
- Yassine Ilmi
- Jason Keirstead
- Navneet Keshav, Lenovo
- David LaBianca, Google
- Valdez Ladd
- Chooi Low
- Victor Lu
- Mike McPhee
- Alan Messer
- Nicolai Nielsen
- Karttik Panda
- Swapnil Pawar, Apex Fintech Solutions
- David Pierce
- Susmitha Pillarisetty
- Rithikha Rajamohan
- J.R. Rao
- Caroline Rocha
- Daniel Rohrer, NVIDIA
- Raymond Sheh
- Xiaokui Shu
- Imran Siddique, Microsoft
- Kapil Singh
- Akila Srinivasan
- Bill Stout, ServiceNow
- Arthit Suriyawongkul
- Harish Thanneer
- Sebastian Wu

**Programme management**

- Claudia Rauch, OASIS

**Reviewers**

*To be listed.*

---

## Appendix A. Gate summary

| # | Phase | Gate |
|---|---|---|
| 1 | Scoping and design | The accountable owner approves the design record before anything is bought or built. The record covers goals and escalation paths, autonomy bounds, blast radius, data classification, the identity and delegation model, containment posture, human-approval conditions, and a versioned threat model that names an owner, a verifying gate, and evidence for each control requirement |
| 2 | Supply chain | Every component is inventoried, with known provenance and an assigned trust tier |
| 3 | Development | The policy surface is under change control equal to code |
| 4 | Admission and deployment | Identity is bound, prerequisites are verified, and the baseline is recorded. Unmet prerequisites block deployment |
| 5 | Runtime | Continuous enforcement, evidence, and proven intervention capability |
| 6 | Reflection and knowledge consolidation | Nothing becomes durable without provenance and a policy check made outside the proposing context. You can trace and purge everything derived from a source |
| 7 | Maintenance | No change to the policy surface or a prerequisite reaches production without re-baselining |
| 8 | Decommissioning | Teardown is shown with evidence, not just claimed; the final state and its effective time are published |

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
