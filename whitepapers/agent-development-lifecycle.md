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

Secure development assumes five things that do not hold for an AI (artificial intelligence) agent:

- Behavior is fixed when the artifact is built.
- The reviewable artifact is the code.
- Identity is a service account.
- Testing approximates production behavior.
- Retirement means deleting the deployment.

[Section 1.1](#11-five-assumptions-secure-development-rests-on) states how each assumption fails. This paper defines an agent development lifecycle (ADLC) whose phases repair those failures. Each phase states what must be decided in advance, what must be verified through monitoring, and how to find the evidence. An agent's identity and access can change over time. An agent can also acquire access on its own. [Section 3.2](#32-supply-chain) covers components the agent acquires at runtime.

A security team should be able to extend the controls it already runs. For any agent, the team should be able to say which obligations have been met and which gate is next. [Section 4.1](#41-adapting-controls-you-already-run) is that guidance.

### Scope and what we care about

- The lifecycle of an agent as an entity, from the decision to build or acquire one through its retirement.
- The security-relevant decisions, gates, and evidence at each phase.
- Improving the agent itself, as distinct from what must be verified on the platforms the agent depends on.
- Guidance for organizations that have already begun an agent development lifecycle.

### Anti-scope

- **Mechanism design.** How to build an isolation boundary or a policy engine. The paper may give examples. Organizations differ, and the paper tries to rely on maturity matrices as far as it can.
- **Telemetry schema.** The lifecycle requires evidence of certain events. It does not set the format of that evidence.
- **Conventional package and dependency supply chain practice.** "Classic" software development lifecycle (SDLC) practice for ordinary packages is covered in other documents.
- **The security of code or content an agent produces.** That is a property of the agent's output, and it belongs to the lifecycle of whatever consumes that output. This paper covers the security of the agent.
- **Model development.** Training, tuning, and evaluation of foundation models. The agent takes the model as an input.
- **How to deal with AI artifacts.** How to review a large volume of generated code, including the human review bottleneck, is out of scope. This paper covers how agents are released to production.

### Target audience

- **Software developers** who configure agentic systems and care about their security in production.
- **Platform and framework teams** who provide the infrastructure other teams build agents on.
- **Security and risk officers** who set policy for what may be deployed, and under what conditions.
- **Third-party risk teams** who evaluate procured agent products against a checklist they can defend.
- **Enterprise architects** who integrate agents into the security environment the organization already runs.

---

## 1. Why agent development needs its own lifecycle

Agents need the same secure development practices as other software, plus checks for behavior that can change after deployment. Most secure development frameworks were not written for agents. This workstream started from observed failures and built the lifecycle phases around them. The assumptions below are the ones a classic SDLC makes that do not hold for agents.

### 1.1 Five assumptions secure development rests on

#### 1.1.1 Behavior is fixed when the artifact is built

Conventional software primarily runs logic its developers defined at build time, against inputs it receives at runtime. Everything downstream of that build, including signing, scanning, promotion, and change control, protects an artifact whose behavior is already settled. Review the code, and you have reviewed the behavior, subject to the quality of the review.

An agent's behavior is set at runtime. The same objective can produce different behavior from one run to the next. Each run combines:

- the system instructions
- a model whose weights the deploying organization did not author
- content retrieved for that request
- memory from earlier sessions
- the tools that are reachable

The same artifact, deployed unchanged, can behave differently this week than last. The corpus it retrieves may have changed. Or the provider may have updated the model behind an application programming interface (API). Build-time assurance does not transfer to runtime.

**Consequence.** Security assurance is the ongoing verification that an agent still meets its security requirements. It must extend beyond build and deployment into runtime, where the agent makes decisions, invokes tools, and interacts with other systems. These activities must be continuously governed, monitored, and constrained by enforceable security controls, starting at admission.

#### 1.1.2 The reviewable artifact is the code

Code review, static analysis, and dependency scanning focus primarily on the software artifacts in which security decisions are implemented.

For an agent, those decisions sit mostly in prose and configuration:

- the system instructions
- the tool permission manifest
- the memory retention policy
- the trust assignments over retrieval sources
- the conditions under which a human must approve an action

This is the policy surface. Tooling built for code does not see it. A change to an instruction that materially widens an agent's authority can pass every gate that an equivalent change in code would have failed. Reviewing each artifact on its own is not enough. The agent's behavior emerges from how the artifacts combine at runtime.

**Consequence.** The policy surface needs its own authoring, review, versioning, and rollback discipline, at parity with code.

#### 1.1.3 Identity is a service account

In traditional software, applications and services are authenticated and managed through service identities or service accounts. These identities may be shared across workloads.

Agentic systems add a harder problem. Authority, meaning identity and authorization, can be delegated across agents and tools at runtime. A person delegates to an agent. That agent delegates to a sub-agent. The sub-agent calls a tool against a resource. At each handoff, the system must be able to determine who is acting, on whose behalf, and with what delegated authority. A shared service account cannot reliably preserve this context across the delegation chain. Agentic systems require first-class non-human identities [^22], explicit delegation [^23] and authorization boundaries, lifecycle management, and action-level traceability.

**Consequence.** Establishing an agent's identity, binding it to constraints, and making it verifiable at each hop is a gated lifecycle event, not a deployment detail.

#### 1.1.4 Testing approximates production behavior

Traditional software testing assumes that the implementation stays steady under stated conditions, and that observed behavior offers sufficient insight into how the system will perform in production under similar conditions. The same input takes the same path and returns the same result.

For a non-deterministic system that consumes untrusted input, a passing test shows that the system behaved acceptably on the inputs that were sampled. That is evidence that a specific failure was absent. It is not evidence that a property is present. Adversarial input is drawn, by construction, from the part of the distribution a test suite does not sample. The agent's own variability means an identical input may not reproduce the tested path.

**Consequence.** Pre-deployment testing must be supplemented by a recorded behavioral baseline and continuous comparison of live behavior against it.

#### 1.1.5 Retirement means deleting the deployment

Decommissioning conventional software means removing the running instance, revoking its credentials, and disposing of its data under a retention policy. The system leaves no residue beyond what was provisioned for it.

An agent leaves residue that was never provisioned:

- durable memory it chose to write
- credentials and grants it accrued while operating
- webhooks and subscriptions it established
- sub-agents it created
- knowledge it consolidated into retrieval stores that other agents now read as authoritative

Deleting the deployment retracts none of that residue. A kill switch does not retract it either. A kill switch halts the agent and revokes the authority the platform issued. It does not revoke what the agent created. An agent can still shape later behavior through what it left behind.

**Consequence.** Retirement is a verified teardown with its own authorization and its own evidence, not an operational afterthought.

### 1.2 What existing frameworks reach

Each framework below is sound on its own. Together they leave a gap. They divide the problem along lines that do not treat the agent as a subject that persists through time.

The table shortens several names. NIST is the National Institute of Standards and Technology, and SP is Special Publication. SSDF is the Secure Software Development Framework. OWASP is the Open Worldwide Application Security Project, and SAMM is its Software Assurance Maturity Model. An LLM is a large language model. CIS is the Center for Internet Security. ISO/IEC is the International Organization for Standardization and the International Electrotechnical Commission. IETF is the Internet Engineering Task Force. SPIFFE is the Secure Production Identity Framework for Everyone, and a JWT is a JSON Web Token.

| Framework | What it reaches | Where it stops for agents |
|---|---|---|
| NIST SSDF, SP 800-218 [^1] | Practice groups spanning prepare, protect, produce, and respond; a strong baseline for phase alignment | Encodes assumptions 1 and 2: the artifact is code, and its behavior is settled at build |
| NIST SP 800-218A [^2] | Extends secure development practice to model development, including provenance and tuning | Takes the model as subject. The agent that consumes the model is out of frame |
| OWASP SAMM [^3] | Organization-level maturity model for assurance activities | Organizationally oriented; offers no agent-specific assurance activities to mature |
| OWASP LLM Top 10 and Agentic Security Initiative [^4] | Concrete agent-relevant failure modes, including prompt injection and excessive agency | A risk enumeration rather than a lifecycle. Says what goes wrong, not at which gate it is prevented |
| CIS AI Agent Companion Guide [^5] | Architectural decomposition of an agent into layers, with control mapping | Architectural rather than temporal. Answers *what are the parts*, not *when is each obligation met* |
| NIST SP 800-207A [^22] | Zero trust access control for cloud-native applications: unique, cryptographically verifiable identities for services and non-human workloads, such as SPIFFE IDs or JWTs, instead of network location | Takes the workload as subject. Gives an agent an identity, but not the delegation chain it acts through or the lifecycle of its grants |
| IETF RFC 8693, OAuth 2.0 Token Exchange [^23] | A standard way to exchange tokens across a delegation, recording both the subject and the actor acting for it | A protocol rather than a lifecycle. Can carry delegated authority across hops, but not when an agent's grants are approved, reviewed, or retired |
| ISO/IEC 42001 [^6] | Management system requirements for AI at organizational level | Governance altitude; does not reach engineering-phase gates |
| Vendor AI-native development playbooks [^7] | The most operationally concrete material available: policy expressed as version-controlled configuration, an identity for the agent distinct from the engineer who triggered it, and tiered autonomy with explicit human authorization at the production gate | Take the agent as instrument rather than artifact. No provenance or trust-tier gate on the models and tools the agent consumes, and no treatment of retirement |

Three patterns follow.

First, these frameworks divide on the wrong axis for this problem. Some take the model as the subject, some the organization, and some the architecture. None takes the agent across its lifetime.

Second, where agent-specific material exists, it is mostly a list of risks. Those lists are valuable, and this paper depends on them. They do not tell an engineering team which gate should catch a given risk. A lifecycle does that. That is the gap this paper addresses.

Third, the most operationally mature material in the table treats the agent as an instrument, not as the thing being shipped. That is evidence of a difference in subject. The gap will remain until a framework addresses the agent directly. It is not a maturity problem that closes on its own.

---

## 2. Boundaries of the lifecycle

Four boundary claims. Much of the disagreement about how to secure agents is disagreement about which of these claims is true.

### 2.1 A process framework, not an implementation guide

The lifecycle states what must be decided, verified, and evidenced, at which point, and by whom. It does not state how to build the mechanism that meets a requirement.

The limit is deliberate. A document that explains how to build an isolation boundary is a different document, and it is a valuable one. Merging the two produces a framework that is too prescriptive to adopt in steps and too shallow to build from. The lifecycle requires that containment posture be decided before procurement and verified before production traffic. The deploying organization chooses the technology. The choice will differ by risk appetite, platform, and regulatory regime.

### 2.2 Design time is inside the process

If behavior is not fixed at build time, you cannot learn what the agent was allowed to do by reading the code later. Someone has to decide that before anything is bought or built, and write it down. Like any secure development lifecycle, this one designs the agent against stated security requirements and threat-models it against intended and unintended use. [Section 3.1](#31-scoping-and-design) says how.

The written result is the design record. It records intended use, autonomy bounds, blast radius, data classification, the identity and delegation model, containment posture, and the threat model. It is versioned. The accountable owner ([section 2.4](#24-every-agent-has-an-accountable-owner)) approves it. Every later gate measures the agent against it. Admission cannot pass or fail an agent that has no design record.

A support agent may read tickets, draft replies, and post them. Only a human may close a ticket or issue a refund. That is three lines in the design record. Development turns those lines into tool permissions and one approval condition. Admission checks that the permissions and the condition match the record. At runtime, a refund call from the agent fails closed, however the request was worded. That fail-closed outcome is the behavior the proposed Risk Map control "Fail-Closed Agent Authorization" [^19] describes. The agent holds a pruned subset of its principal's permissions. Anything outside that subset is refused.

This paper uses "containment posture" from section 2.1 on. It covers three things:

- what the agent must not be able to reach, on the host, over the network, or through its tools
- what must not be able to reach the agent
- where the boundaries that enforce this sit, outside the agent

Building those boundaries is the subject of the containment paper [^18]. This paper only asks that the posture is decided here and verified at admission.

Design time is the first phase. If it sits outside the numbered phases, it has no gate and no required output. Nothing then stops a team from skipping it.

### 2.3 The agent instance is the unit of scope

An agent exists in two forms. The definition is a reviewed revision of its instructions, policy surface, model binding, tool manifest, and memory policy. An instance is a running realization of that definition. It holds its own identity, composes its own context, accumulates its own memory, exercises its own delegated authority, and leaves its own fingerprints. One definition may produce thousands of instances. Some live for one request. Some live for months.

The lifecycle governs the instance. The definition still matters, because instances inherit from it. Obligations set in scoping, supply chain, and development are recorded against a definition revision. They bind every instance created from that revision. The failures that motivate this paper show up in instances. Assumptions 1, 3, and 5 fail per instance: each instance composes its own behavior, holds and passes on its own authority, and leaves its own residue (sections 1.1.1, 1.1.3, and 1.1.5). A lifecycle that tracked only the definition would certify a template and miss what that template produced.

Within an instance, the lifecycle governs:

- its instructions
- its reasoning core
- its input and output handling
- its identity and delegated authority
- the policies by which it consumes everything else
- the durable memory it accumulates

Memory belongs inside the boundary. It is not an external dependency. The instance writes it, it shapes the instance's later behavior, and it is residue when the instance retires.

Three consequences follow.

1. An instance exists only when it is created from an admitted definition revision. Issuing its identity is what binds it to that revision's constraints.
2. An instance that another instance creates at runtime, such as a sub-agent, is in scope only when the parent's admitted definition bounds what may be spawned, under what identity, and with what authority. Anything outside those bounds is a separate definition and needs its own admission. Nothing created at runtime can pass a gate after the fact.
3. Retiring a definition means retiring every instance of it. That is possible only when the organization knows, at all times, which instances exist.

For the resources an instance depends on, the deploying organization implements consumption controls in the agent and verifies that each platform meets the requirements the design states. Those resources are the model, the orchestration platform, the tools, the data stores, the infrastructure, and any other agent it calls. An agent called as a tool is a dependency of its caller. It is also a unit of scope in its own owner's lifecycle. A procured agent shifts the work toward verification, and little is left to implement. The obligations do not change.

The distinction between implementing and verifying has its practical force at admission. Verification is graded rather than binary. Some dependencies will never produce complete evidence. A model served behind an API can change without notice, and its provider will not open its internals. Where platform evidence is weaker than the design requires, the organization closes the gap with compensating controls in the agent, recorded against the dependency's trust tier (section 3.2). Otherwise the agent does not deploy. A dependency that nobody evaluated is never acceptable. This limit keeps the lifecycle tractable. An organization is not required to re-secure its cloud provider in order to deploy an agent. It is required to know what it depends on, how well it has verified each dependency, and what it did about the gap.

### 2.4 Every agent has an accountable owner

Every agent definition, and every instance created from it, resolves at all times to a named human who is accountable for its existence. An organizational unit may hold ownership, but the chain must resolve to a named individual. When a team dissolves, shared accountability ends. Ownership is explicitly transferred or terminated. It is never allowed to lapse.

Ownership is not the same thing as authority. The two are easy to conflate. The owner is accountable for the agent existing, for the risk accepted when it was admitted, and for its retirement. The principal is the party whose authority a given action exercises. When a user delegates a task to an instance, that user is the principal for the actions that follow. The owner does not change. Delegation moves authority. It does not move ownership. For any action, two questions must be answerable: who authorized it, and who is accountable for the agent that performed it. Section 1.1.3 covers the first question. This section covers the second.

The CoSAI (Coalition for Secure AI) AI Shared Responsibility Framework [^15] divides responsibility for an AI system across five layers, from the business use down to the model provider. It says which party is responsible at each layer. Ownership answers a narrower question inside the deploying organization: which person answers for this particular agent.

Ownership has to be verifiable at runtime. A record written once is not enough. An instance's identity resolves to a registry record that names an active owner. Credential issuance and renewal depend on that owner staying active. An instance spawned by another instance inherits its parent's owner unless it is explicitly reassigned at creation. When an owner leaves, changes role, or is reorganized away, the same joiner, mover, and leaver events that govern human access suspend the agent and its instances. Suspension, rather than deletion, is the safe default, because an orphaned agent's state and traces are evidence its eventual retirement will need.

This assumes an inventory. The owner is a field on every definition record and every instance record. The inventory can be queried when a credential is issued or an action is checked. Few organizations have that inventory. An asset register reconciled each quarter cannot answer a question asked at runtime. Building one that can is engineering work of its own.

The owner is also how the lifecycle answers *by whom*. The owner approves the design record before procurement or implementation (section 3.1), accepts residual risk at admission (section 3.4), sets the conditions under which durable knowledge requires human approval (section 3.6), and authorizes retirement (section 3.8). The work behind each decision can be delegated. The accountability for it cannot.

This is the least technical of the four claims, and the one most often missing in practice. Without an owner, no party has standing to approve retirement, and nobody notices when an agent outlives the purpose it was commissioned for. An ownership lapse is a common precondition for the residue problem in assumption 5, and it is among the cheapest to prevent.

---

## 3. Lifecycle phases

Eight phases. Each phase names the assumption it repairs and the gate that must pass before the agent proceeds.

### 3.1 Scoping and design

*Repairs assumption 1.*

The organization decides what the agent is for, and what it may become. Define permitted goals, prohibited goals, and escalation paths. Set autonomy bounds and the blast radius of a worst-case action. Classify the data the agent may read, write, retain, or disclose. Select the identity and delegation model. The reference model is ODIS (Open Delegation and Identity Standard), whose three layers are passport, bridge, and router [^20]. Set containment posture ([section 2.2](#22-design-time-is-inside-the-process)). Identify which actions require human approval before execution. Produce a threat model.

Write these decisions in the design record, against a definition revision ([section 2.3](#23-the-agent-instance-is-the-unit-of-scope)), so every instance inherits them. Give each decision an identifier. [Development](#33-development) and [admission](#34-admission-and-deployment) point back to those identifiers. The accountable owner approves the record. Someone other than its author reviews it. The amount of detail scales with criticality: blast radius, data classification, and autonomy. A low-risk agent gets a short record. Each human-approval condition names the action, the approver, and how long the approval may take. If the agent cannot wait that long, narrow the action or add a fallback. Do not drop the approval later.

The threat model asks how intended use, and unintended use, could get around those decisions. Name the assets and the assumptions about dependencies. Map the data flows and the control flows among users, tools, memory, retrieval sources, identity providers, other agents, and the orchestration platform. Mark where trust changes hands and where authority changes hands, including where images, audio, or video are decoded, resized, or transcribed. Cover at least:

- identity and privilege abuse
- tool misuse
- hijacking or tampering through content the agent reads or remembers
- disclosure of data through outputs, tools, or memory

Also cover delegation, and chains of permitted actions that add up to a prohibited outcome.

Two practical rules run through the model. The model can be wrong, or be steered by something it read, at any moment. Each constraint on the agent's authority says whether a control outside the model enforces it, or whether the constraint relies on the model following instructions. [Section 3.3](#33-development) carries that choice into the policy surface. The second rule covers an agent that, in one session, reads untrusted content, reaches private data or sensitive systems, and can change state or send data out. That combination turns a prompt injection into real damage [^16] [^17]. Remove one of the three. Or put a control outside the model, or a human, in front of the action.

Each scenario records how harm could happen, what access it needs, the assets, the impact, and its priority. Link the scenario to the decision it threatens and to the planned treatment. For each control requirement, name the owner, the gate that verifies the control, and the evidence that gate takes. At this phase, every control is still a plan. Record the risk you expect to remain, and who has to accept it. The owner accepts residual risk at admission, and does so on evidence. Later gates use the model. They do not restate it. [Admission](#34-admission-and-deployment) verifies the controls and records the behavioral baseline. [Runtime](#35-runtime) ties monitoring to the scenarios. [Maintenance](#37-maintenance) reopens the model when something material changes, including a change upstream.

**Gate.** The accountable owner approves the design record and the threat model before procurement or implementation starts. Both are versioned, reviewed by someone other than their author, and kept where every later gate can read them, under the same change control as the policy surface. Admission checks that the approval came first.

### 3.2 Supply chain

*Repairs assumptions 1 and 2.*

Supply chain is not always treated as its own lifecycle phase. This paper includes it because a secure development lifecycle depends on it. Supply chain attacks remain a primary attack surface for traditional development and for AI and agentic development [^21].

This phase establishes provenance and trust for each external component the agent incorporates:

- models
- tools
- prompt templates
- frameworks
- retrieval sources
- any other agents it may consume

Most of these components can carry or emit content the agent could treat as instructions. Examples are tool descriptions, retrieved content, and the outputs of other agents. For such a component, ask two questions. Is the component authentic? And how much authority may its content exert over the behavior of the agent under development?

Every such external component MUST be inventoried with, at a minimum, an accountable owner, its source, and its version identity. Record whether each version is pinned or floating, for example a model behind a provider-managed alias or a generic API endpoint. For any floating component, record who controls changes to it and what notice the supplier commits to give before a change. That notice is what triggers re-baselining in [maintenance](#37-maintenance).

Do three further things:

- Verify each component's origin and integrity to the extent its supplier makes verification possible, and record the evidence. If a component cannot be inspected, obtain and record supplier-provided evidence and the [platform verification](#23-the-agent-instance-is-the-unit-of-scope) described in section 2.3. Record this gap in the exit gate documentation.
- Assign each component a trust tier. A named owner assigns the tier and states what authority the component's content may influence. If provenance could not be verified, the tier reflects that. Re-evaluate the tier when the supplier, the version, or the evidence changes.
- Test each component's behavior for this application, and record the results. The results feed the behavioral baseline recorded at [admission](#34-admission-and-deployment). A component's suitability is a question about this use, not a general property of the component.

Where an agent can acquire tools or other components at runtime, the design must either prohibit that acquisition or apply this same process at the moment of acquisition.

> [!NOTE]
> Detailed guidance on artifact integrity, provenance, and attestation for models, datasets, and training artifacts is the subject of CoSAI Workstream 1 [AIMM; Signing ML Artifacts]. General supply chain risk management practice is covered by NIST [SP 800-161 Rev 1 Update 1]. This paper does not restate either.

**Gate.** Every component the agent depends on, including non-conventional dependencies listed above, is inventoried with an owner, with its provenance verified or the gap recorded, and with an assigned trust tier.

### 3.3 Development

*Repairs assumptions 1 and 2.*

Author the policy surface as a first-class artifact. Define:

- system instructions, using techniques that resist injection
- the tool permission manifest, with least privilege for each tool
- the memory retention and filtering policy
- trust assignments over retrieval sources
- the conditions that trigger human approval
- instrumentation that will make runtime behavior observable

System instructions MUST be written on the assumption that untrusted content will attempt to override them during runtime.

> [!NOTE]
> No single method fully defends against prompt injection. A defense-in-depth strategy minimizes the risk and the impact of a successful prompt injection. That strategy uses system-prompt techniques, tool permissions, and the other mechanisms listed above, among other measures.

For each constraint on the agent's authority, record whether a control outside the model enforces it, or whether it depends on the model following the prose. Trace each element of the policy surface to a decision recorded in [scoping and design](#31-scoping-and-design). For example, trace a tool permission to a permitted goal, and an approval condition to the blast radius analysis.

Add the instrumentation [decommissioning](#38-decommissioning) will need when it enumerates what the agent created. Emit a signal when the agent creates a resource, such as a webhook, a subscription, a sub-agent, or a durable memory write.

Each artifact, not just the code, MUST be versioned, ideally in an auditable version control system, and revertible independently of the code around it. Changes SHOULD be reviewed by someone other than their author. How much review a change needs is for each organization to set, according to its maturity and risk tolerance. For example, each organization decides whether a change that widens the agent's authority needs a dedicated security review.

The reviewed policy surface, handling logic, and instrumentation MUST carry a single version identity that is verifiable during [admission](#34-admission-and-deployment). Development and test environments MUST use non-production data and credentials, and the policy surface MUST NOT embed credentials.

**Gate.** The policy surface is under change control at parity with code, and a reviewer can answer what authority the agent holds, and why, by reading it. Each reviewed revision is identifiable for [admission](#34-admission-and-deployment).

### 3.4 Admission and deployment

*Repairs assumptions 1, 3, and 4.*

This is the strongest gate in the lifecycle. It turns the earlier work into a decision to deploy or not.

Implement:

- Establish the agent's identity and bind it to the constraints set at design time.
- Register the agent with the identity provider.
- Verify that the deployed components are mutually consistent, so the instructions, handling logic, and instrumentation come from the same reviewed revision.
- Run adversarial tests against known agent failure modes.
- Record the behavioral baseline that runtime will be compared against.

Verify:

- The identity provider issues the agent's credentials and will validate them.
- Serving, storage, and orchestration platforms meet the requirements the agent's design depends on.
- Audit logging is in place, and the logs reach a destination that somebody reads.

**Gate.** Any unmet prerequisite blocks deployment. This is where the implement-and-verify distinction from section 2.3 becomes binding. A gate that cannot block is a report.

### 3.5 Runtime

*Repairs assumptions 1 and 4.*

Enforce, continuously, what admission verified once. The agent presents its identity for each consequential action. Evaluate policy at the point of tool invocation. Do not assume the policy from deployment. Input and output handling apply their filters against live traffic. Record decision traces at a fidelity sufficient to reconstruct why an action was taken. Compare live behavior against the recorded baseline. The comparison is fail-closed: an agent whose monitoring is off, or unread, is outside its admitted state. An intervention capability exists, and it has been exercised rather than merely configured. In the CoSAI Risk Map [^8], the record is the audit record repository. The comparison and the response path are a control [^11].

Verification continues after admission. A prerequisite that passed at admission can regress. A platform that stops meeting a requirement should surface as an alert rather than as an incident.

Observed effects are evidence only inside their recorded coverage. A monitor that attached after a call, was paused, or could not see a channel leaves a gap. A gap cannot establish that nothing happened inside it. The portable result for that check keeps `not_established` (containment clause C7, [#269](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/269)) with its reason and the named gap, such as the interval between the call and the observer attaching. Do not fold that result into a pass. The candidate conformance cases for Request for Comments (RFC) 189 [^13] include this case.

**Gate.** The runtime gate is continuous. An agent that operates without enforcement, evidence, and an intervention capability has left the lifecycle, rather than moved through it. Report a gap in the evidence as `not_established` for that gap, never as clean.

### 3.6 Reflection and knowledge consolidation

*Repairs assumptions 1, 4, and 5.*

This phase governs what an instance is permitted to learn. Information may be promoted out of an instance's ephemeral (short-lived) context into:

- the instance's own durable memory
- memory shared across instances of the same definition
- retrieval sources that other agents read

Promotion is where poisoning becomes persistent, and where future behavior is silently redefined. It is the point at which one instance's compromise becomes the starting condition of every instance that comes after it.

Reflection is not a step between runtime and maintenance. It is a gate on every promotion. The gate runs at the same time as runtime, for as long as an instance writes anything durable.

The governing principle is that a context which may have been influenced cannot authorize its own persistence. An instance that has just processed untrusted content is the party least able to judge whether that content should be remembered. The decision to promote is made outside the context that proposes it. It can be made by deterministic policy, by an evaluator that does not share the proposing context, or, for high-impact knowledge, by a human acting under conditions the owner has set (section 2.4). Where those conditions sit depends on what the agent does. An agent that supports clinical decisions, or that operates a regulated control, warrants human approval for far more of what it retains than an agent that drafts internal documents.

Not all knowledge carries the same risk. A record of a past session informs later behavior. A learned fact shapes conclusions. A learned procedure, which says how to perform a task or use a tool, functions as an instruction. That makes it part of the policy surface, in the sense of assumption 2. Promote a procedure only through the review that section 3.3 requires for any other change to the policy surface.

Writing a statement down does not raise its trust. Promoted content keeps the trust tier of its source. It does not take the tier of the store it lands in. A retrieval source assigned a high tier in section 3.2 cannot become a channel that presents low-trust content as authoritative knowledge. Promotion into a store that other instances or other agents read crosses a trust boundary. Hold that promotion to a stricter requirement than promotion into an instance's private memory.

Enforce the memory-write policy. For anything retained, capture provenance: its source, the source's trust tier, the instance that proposed it, and the decision that admitted it. Record that provenance when the promotion is decided. Do not reconstruct it later. At the moment of the write, attest a hash of the promoted content and a hash of the inputs and tool calls that produced it. Apply the data classification from scoping to what may be retained. Apply retention labels and rollback markers. Keep an audit link from a later decision back to the knowledge that informed it.

Accumulated memory is a change to behavior, made in increments that each pass every check. Promotion volume beyond a threshold set at design time, or the passage of a fixed interval, triggers the re-baselining that section 3.7 requires of any other behavioral change.

**Gate.** Nothing becomes durable without provenance and a policy check made outside the proposing context. Ephemeral context and approved durable memory are distinguishable at the storage layer, not only by convention. Everything derived from a given source over a given period can be identified and purged. The day a source is found to be poisoned is the day that capability is needed.

### 3.7 Maintenance

*Repairs assumptions 1 and 2.*

Changes to a live agent re-enter review rather than accumulating. Treat a change to the policy surface as a change to behavior, because it is one. After any change, run behavioral regression tests, re-establish the baseline, and revert the instructions and the handling logic together rather than letting them drift apart.

Upstream change is the harder half. A model updated behind an API, a patched framework, or a tool whose contract changed: the deploying organization did not start these changes, and each one can change how the agent behaves. Maintenance is the phase that notices.

**Gate.** No change to the policy surface, and no change to a prerequisite, reaches production without re-baselining behavior.

### 3.8 Decommissioning

*Repairs assumption 5.*

Decommissioning ends the agent's authority to act. Whether the agent can return later is a policy choice. If it returns, it comes back through admission as a new entity. Pausing, suspending, or quarantining a live agent belongs to runtime or maintenance, not to this phase. An agent that can resume under the same admitted identity has not been decommissioned. The working group settled this definition in RFC [^10], after withdrawing a longer draft that had "soft" and "hard" modes. What looked like two modes was one phase, with parameters the organization sets.

Every decommissioning does the same things, whatever retention rules the organization uses:

- Record who requested retirement, who approved it, and why.
- Freeze inbound invocation.
- Revoke authenticators, and tombstone the identifier. Do not delete the identifier. A deleted identifier breaks replay detection.
- Revoke delegated authority on every sub-agent the agent created.
- Enumerate its resources across every system it touched. Give each resource a disposition: revoked, deleted, cryptographically shredded, retained until a date, held for legal reasons, handed over to a successor, or an explicit exception with an owner and an expiry.
- Publish the terminal state and its effective time, where a relying party can check both without the retiring organization's help.
- Store the disposition receipt. The receipt names the retired identity, the authorizer, the effective time, each asset's disposition, the evidence references, and the exceptions.

The organization sets what varies, in the way NIST SP 800-53 leaves parameters to the implementer [^9]:

- who may authorize retirement
- whether dual control or a legal-hold check is required
- how each store is disposed of
- how long held assets are kept
- which sanitization technique applies
- how long the tombstoned identifier is retained
- which archived artifacts may enter a later Admission

Archiving one agent's traces and purging that same agent's tool grants is a valid combination.

Two losses are easy to miss. Other systems and people may have come to depend on capabilities the agent was never documented as providing. The agent may hold knowledge that exists nowhere else. Both should be enumerated before the receipt closes. Development should instrument for both, because neither can be recovered afterwards (section 3.3). Decommissioning can also be imposed, as when an upstream provider disappears or a dependency breaks. The steps above still apply. Some confirmations cannot be obtained. The receipt records that missing confirmation as an exception. It does not treat the confirmation as if it had been obtained.

**Gate.** Teardown is evidenced rather than asserted. A decommissioning that cannot show what was revoked, what was retained, and when authority ended has not completed. A verifier that holds a record signed by this identity can place that record before or after that moment. If the published terminal state does not let the verifier decide, it returns `not_established` (containment clause C7). A relying party treats `not_established` as unproven, never as "before".

---

## 4. Applying the lifecycle

### 4.1 Adapting controls you already run

An organization that already runs a secure development lifecycle should not start over. For each control, ask which of the five assumptions it depends on, and then extend the control.

- A control that rests on **assumption 1** needs a runtime counterpart. Build-time gates keep their value for the conventional parts of the system. They gain an admission gate and continuous verification alongside.
- A control that rests on **assumption 2** needs a wider definition of *artifact*. Change control, review requirements, and rollback procedures largely transfer once instructions and configuration sit inside the boundary.
- A control that rests on **assumption 3** needs delegation modeled explicitly. Existing identity infrastructure is usually adequate. What is missing is treating an agent as a principal that holds constrained, traceable authority.
- A control that rests on **assumption 4** needs a baseline. Test suites keep their role. They stop being the only evidence of production behavior.
- A control that rests on **assumption 5** needs an inventory of residue. Existing decommissioning runbooks usually cover resources the organization provisioned. They miss resources the agent created.

Migration cost concentrates in the first and the last of these. Most organizations already have some version of the middle three and have not applied them to agents.

### 4.2 Where each assumption is repaired

| Assumption | Primary phase | Reinforced at |
|---|---|---|
| 1. Behavior fixed at build | Scoping and design | Admission, runtime, maintenance |
| 2. Reviewable artifact is code | Development | Supply chain, maintenance |
| 3. Identity is a service account | Admission and deployment | Runtime |
| 4. Testing approximates production | Admission and deployment | Runtime, reflection and knowledge consolidation |
| 5. Retirement is deletion | Decommissioning | Reflection and knowledge consolidation |

No assumption is repaired by a single phase. A gate is only as good as the evidence produced upstream of it and the enforcement downstream.

---

## 5. Open questions

The questions below are unsettled. They are the working group's agenda. The paper does not treat them as closed. Two questions from the first draft have been answered and moved to section 6: whether observability is a distinct concern, and whether retirement has modes.

1. **Scoping by deployment pattern.** Should lifecycle obligations change with how autonomous a deployment is? The range runs from a model that answers questions, to a model that calls tools, to a single agent, to an agent that coordinates other agents, to an agent that composes its own network. If the obligations change, does low autonomy reduce the obligations themselves, or only the effort of meeting them? A scoping matrix along these lines was proposed in June [^12]. The group's only position so far is that any such matrix is a set of example patterns, not a universal decomposition.

2. **Intervention semantics.** Where does the capability to halt an agent belong? How does termination cascade to work already delegated? How is completion verified across in-flight transactions? There is a reasonable argument that termination is the wrong primitive, and that throttling or falling back to a deterministic path serves better where an abandoned transaction is itself a harm. The behavioral monitoring control [^11] leaves open whether that control owns the halt, or only the decision to halt.

3. **Evidence portability.** Can the evidence a gate produces be portable enough that a third party can evaluate a procured agent against this lifecycle, without access to the supplier's internals? Section 3.5 and the Workstream 4 (WS4) containment paper, clause C7 ([#269](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/269)), name the third answer a verifier gives when evidence is absent: `not_established`, beside `pass` and `fail`. The value carries the reason the property could not be determined. The candidate conformance cases for RFC 189 [^13] exercise that answer. One case is a write the producer reported, with nothing independent observed. That case returns `not_established`. What remains open is which gate records must carry that answer, and in what signed form a relying party can verify it.

4. **What is lost at retirement.** Section 3.8 asks organizations to enumerate undocumented dependencies and undocumented knowledge before an agent retires. Whether the lifecycle should require a handover artifact for these, and what it would contain, is unsettled.

---

## 6. Positions of the working group

This paper is meant to carry the working group's opinions, not only a survey of other people's. Those opinions are recorded in the table below, so a position can be added in one line, dated, and traced to the discussion that produced it.

### 6.1 How a position gets in

A position is a claim the group has argued and settled, at least for now. It enters the table only with a date and a source. The source is a meeting whose minutes record the claim, or a GitHub thread where the group reached it. A position can be reopened. When that happens, the old row stays, and a new row supersedes it. The paper keeps the history of what the group used to think, and why it changed.

The group produces positions in two ways. Some come out of ordinary work, such as an RFC review that converges. Others come from a deliberate exercise. A meeting opens with a short review of one influential paper or post. The presenter states one claim from it to argue with, and the room argues. Each such session ends with a position the group writes here, or with an explicit decision to decline. A position nobody writes down did not happen.

### 6.2 Positions taken

| Date | Question | Position | Source |
|---|---|---|---|
| 2026-07-01 | Are the category sets this paper uses (deployment levels, architecture layers) a universal decomposition? | No. They are examples of patterns. Presenting them as universal creates consensus friction without adding precision | ADLC minutes, 7/1; scoping matrix [^12] |
| 2026-08-12 | Is System Governance a lifecycle phase? | No. Governance supplies authorization; the phases execute it. Dropped from the phase list | ADLC minutes, 8/12 |
| 2026-08-12 | Does this lifecycle restate conventional package and dependency supply chain practice? | No. That belongs to the Supply Chain workstream. This paper covers what goes beyond model signing: provenance and trust tiers for models, prompts, tools, and retrieval sources | ADLC minutes, 8/12; section 3.2 |
| 2026-08-19 | When mapping this lifecycle to the CoSAI Risk Map, widen existing entries or add new ones? | Add new entries, so a control has something specific to attach to. File an RFC or issue before any PR | ADLC minutes, 8/19 |
| 2026-08-27 | Does this paper specify containment mechanisms? | No. Containment is a separate Workstream 4 paper. This paper requires that containment posture be decided and verified, and cites that paper for how | WS4 minutes, 8/27; section 2.1 |
| 2026-09-01 to 09-14 | Is observability a distinct component of an agentic system? | The record is not new: it is the audit record repository the Risk Map already has. What is new is what you do with it: a baseline, drift and anomaly detection, and a response path. That is a control, and it is fail-closed | RFC #175 withdrawn, RFC #195 filed [^11] |
| 2026-09-09 to 09-14 | Is decommissioning reversible? Does it have modes? | Decommissioning ends the agent's authority to act and is terminal. Anything reversible is a Runtime or Maintenance state. There are no modes; there are organization-defined parameters | ADLC minutes, 9/9; RFC #170 as amended [^10] |
| 2026-09-09 | Where does the working group keep its record? | In GitHub. The paper is reviewed on its pull request. Google Docs and Slack are scratch space | ADLC minutes, 9/9 |
| *planned* | Is the harness, rather than the model, where an agent's behavior is determined and changed? If so, do Maintenance and Reflection carry more weight than section 3 gives them? | *To be argued. First paper-review session, scheduled for 2026-09-23, on Weng's harness engineering post [^14]* | |

---

## 7. Takeaways and conclusion

The case for a separate lifecycle rests on the five assumptions in section 1.1. It does not rest on agents being new, important, or fast-moving. Section 4.2 maps each assumption to the phase that repairs it and to the phases that reinforce that repair. Section 4.1 asks which existing controls rest on an assumption that no longer holds.

A reader who disagrees with a phase is invited to attack the assumption it derives from. That is the argument this structure is built to expose. A reader who disagrees with a position in section 6 is invited to reopen it, with a source.

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
[^21]: Dan Lisichkin. *My Agentic Trust Issues: From Prompt Injection to Supply-Chain Compromise on gemini-cli*, 5 May 2026. https://www.pillar.security/blog/my-agentic-trust-issues-from-prompt-injection-to-supply-chain-compromise-on-gemini-cli
[^22]: NIST. *A Zero Trust Architecture Model for Access Control in Cloud-Native Applications in Multi-Cloud Environments, SP 800-207A.* https://csrc.nist.gov/pubs/sp/800/207/a/final
[^23]: IETF. *OAuth 2.0 Token Exchange, RFC 8693.* https://www.rfc-editor.org/info/rfc8693/

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
- Nicolai Nielsen, Thomson Reuters
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
| 1 | Scoping and design | Design record approved by the accountable owner before procurement: goals and escalation paths, autonomy bounds, blast radius, data classification, identity and delegation model, containment posture, human-approval conditions, and a versioned threat model with an owner, a verifying gate, and evidence named for each control requirement |
| 2 | Supply chain | Every component inventoried, with known provenance and an assigned trust tier |
| 3 | Development | Policy surface under change control at parity with code |
| 4 | Admission and deployment | Identity bound, prerequisites verified, baseline recorded. Unmet prerequisites block deployment |
| 5 | Runtime | Continuous enforcement, evidence, and demonstrated intervention capability |
| 6 | Reflection and knowledge consolidation | Nothing becomes durable without provenance and a policy check made outside the proposing context. Everything derived from a source can be traced and purged |
| 7 | Maintenance | No change to the policy surface or a prerequisite reaches production without re-baselining |
| 8 | Decommissioning | Teardown evidenced, not asserted; terminal state and its effective time published |

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
