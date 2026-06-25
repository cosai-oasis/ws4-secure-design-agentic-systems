# SIG Agent Development Lifecycle (ADLC) Scope Definition



**Workstream:** WS4, SIG ADLC  
**Priority:** High  
**Version:** 1.0 — Draft for Review  
**Status:** Ready for Review  
**Date:** 2026-05-12  

**Authors:**  
[@husky-parul](https://github.com/husky-parul) Parul Singh, Red Hat  


## 1. Summary

SIG Security of Agent Development Lifecycle (ADLC) is dedicated to hardening the security posture of autonomous and semi-autonomous AI agent systems as organizations rapidly deploy them into enterprise environments.

The Agent Development Lifecycle (ADLC) is not a replacement for SDLC. It builds upon traditional Secure Software Development Lifecycle (SDLC) frameworks but introduces fundamental differences driven by autonomous decision-making, non-deterministic behavior, and runtime tool invocation.

This document uses standard frameworks (NIST SSDF, OWASP SAMM) to identify exactly where agent security differs from traditional software security, helping enterprises adapt existing SDLC controls rather than starting from scratch.

## 2. Target Audience & Personas

ADLC uses [CoSAI persona guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md) — sets of temporary responsibilities and required controls — rather than prescribing specific organizational titles.

| Persona | Description |
|---|---|
| **Agent Developers** | Those building and configuring agentic systems |
| **Agentic Security Framework Developers** | Those creating tooling and infrastructure for secure agent operations |
| **Security & Risk Officers (CISO/CRO)** | Those establishing IT security and business control policies |
| **Third-Party Risk Management (TPRM) Teams** | Those evaluating and procuring commercial off-the-shelf agentic solutions |
| **Enterprise Architecture Teams** | Those integrating agents into existing security ecosystems |

## 3. Methodology

**Baseline Framework:** NIST SSDF (Secure Software Development Framework) SP 800-218  
**Supplementary Framework:** OWASP SAMM (Software Assurance Maturity Model)  

#### External Resource Control Principle

Models, orchestration frameworks (LangChain, AutoGPT), APIs, data services, and registries are upstream resources separate from the agent. ADLC does not own their internal security. ADLC owns how agents consume them: provenance verification, trust establishment, capability constraints, and runtime monitoring.

#### Implement vs. Audit Distinction

Throughout the ADLC, components fall into two categories based on who owns their security:

ADLC Implements (In Scope): Agent-owned components and the controls that govern how the agent uses or changes adjacent systems. We directly build, configure, and enforce controls in the agent entity, and we define the requirements that prerequisite systems must satisfy for the agent to use them safely. Examples:
- Writing agent system instructions with injection-resistant prompt design and policy definitions
- Defining tool permissions, memory policies, RAG source trust assignments in Agent System Instructions
- Implementing input/output sanitization in Agent Input/Output Handling
- Enforcing policy decisions (authorization checks) before agent uses external resources
- Establishing business specific baseline behavior before agents along with their tools and capabilities are admitted

ADLC Audits (Prerequisites): Model, Orchestration, Application, Data, Infrastructure components. Security is owned by external providers or platform teams. We verify requirements are met but don't implement the platforms. Examples:
- Auditing that a foundation model provider supplies provenance records and safety evaluations
- Verifying that the Tools platform (Salesforce API, etc.) enforces authentication and rate limiting as documented
- Confirming that Memory storage infrastructure provides session isolation and encryption
- Validating that RAG document storage has integrity controls and access policies
- Checking that Infrastructure provides KV-cache isolation for model serving

The Pattern: 
- ADLC implements Agent component policies and enforcement (System Instructions define policies, Input/Output Handling enforce them)
- ADLC audits prerequisite platforms (Model, Orchestration, Data, Infrastructure execute the policies but we don't own them)

#### Lifecycle Phases vs. Component Categories

It's important to distinguish:
- Component Categories (CoSAI Risk Map): *What* components exist — Agent, Model, Orchestration, Application, Data, Infrastructure
- Lifecycle Phases (ADLC): *When* activities happen — Supply Chain, Development, Admission/Deployment, Runtime, Maintenance, Decommissioning


Example: Policy enforcement is implemented in Agent components (System Instructions define policies for tools, memory, RAG; Input/Output Handling enforce them). These controls are established during Admission/Deployment phase (verifying policies and enforcement are in place) and actively enforced during Runtime phase (continuous policy evaluation). The Orchestration platform executes these policies but is a prerequisite, not something we implement.

## 4. Component Category Scope (CoSAI Taxonomy)

ADLC uses the [CoSAI Secure AI Tooling Risk Map](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/components-full.md) component taxonomy to establish clear scope boundaries. See [Risk Map Visualization](https://raw.githubusercontent.com/cosai-oasis/secure-ai-tooling/refs/heads/main/risk-map/svg/risk-map-graph.svg) for component relationships.

### 4.1. In-Scope Components (ADLC Implements Controls)

Agent components are the ONLY in-scope components. Everything else (Model, Orchestration, Application, Data, Infrastructure) is a prerequisite.

#### **Agent Components**

The agent entity itself — the core decision-making unit and its immediate inputs/outputs. This is where ALL agent security is defined and enforced.

| CoSAI Component | CoSAI Definition | What We Implement |
|---|---|---|
| **Agent System Instructions** | "Define agent capabilities, permissions, and limitations using control tokens against prompt injection" | This is where ALL policies are defined:<br>• Prompt templates with injection-resistant design<br>• Policy-as-code (which tools, memory rules, RAG sources)<br>• Permission manifests (least-privilege per tool)<br>• Constraint rules (data handling, output restrictions)<br>• Tool permission configurations<br>• Memory retention and PII filtering policies<br>• RAG source trust assignments |
| **Agent Reasoning Core** | "Plans and executes actions through tool calls" — the decision-making intelligence (LLM or rule-based logic). Takes system instructions + user query → produces reasoning and decisions. | • Prompt engineering<br>• Runtime context assembly (System Instructions + User Query + Memory + RAG)<br>• Decision trace logging<br>• Semantic observability instrumentation<br><br>**NOTE:** The foundation model itself is a prerequisite (see 2.2.4) — we audit it, not implement it. |
| **Agent User Query** | "Processed user request details combined with system instructions and contextual data" | • Query preprocessing<br>• Intent extraction<br>• User input preparation for runtime context assembly |
| **Agent Input Handling** | "Distinguishing trusted commands from untrusted data to prevent manipulation" | • Input validation frameworks<br>• Sanitization logic<br>• Prompt injection detection<br>• Trusted/untrusted data separation<br>• Pre-invocation authorization checks |
| **Agent Output Handling** | "Formats AI-generated output for display, preventing malicious content execution and data exfiltration through proper sanitization" | • Output sanitization<br>• PII masking and sensitive data filtering<br>• Response validation<br>• Exfiltration prevention<br>• Post-invocation data loss prevention |


### 4.2. Prerequisite Components (ADLC Audits Controls)

For these components, ADLC does not implement their internal security — each is secured in its own domain. ADLC implements consumption controls within Agent components (System Instructions define policies, Input/Output Handling enforce them), but the underlying platforms are prerequisites.

The Pattern: 
- Agent System Instructions define policies for how to consume these resources (which tools, what memory rules, which RAG sources)
- Agent Input/Output Handling enforce those policies (validate before/after using resources)
- The resources themselves (Model, Orchestration, Data, Infrastructure) are prerequisites we audit, not implement

#### **Model Components**

Foundation models and their development lifecycle are upstream resources. ADLC treats them like third-party libraries in traditional SDLC — we verify provenance and integrity, but we don't build or secure them internally.

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **The Model** | Foundation model weights and serving API | Implement: Provenance verification checks, trust tier assignment logic, capability constraints in prompts, behavioral drift monitoring, model output validation | Audit: That the model provider supplies provenance records, safety evaluations, documented capabilities/limitations. The model's internal security (training, weights) is owned by the provider. |
| **Training and Tuning** | Model training and fine-tuning processes | Implement: N/A - out of scope | Audit: That training provenance is documented by provider (if we consume a fine-tuned model). Refer to NIST SP 800-218A for Model Development Lifecycle security. |
| **Model Evaluation** | Model testing, validation, bias assessment | Implement: Our own application-specific behavioral testing (does the model work for *our* use case?) | Audit: Provider evaluation reports, benchmark results, safety testing, red team assessments. We don't conduct the model's bias testing; we audit that it was done. |
| **Model Frameworks and Code** | Training/inference frameworks (PyTorch, TensorFlow, vLLM) | Implement: N/A - we consume models via API, not frameworks | Audit: That model providers use secure frameworks, if relevant to our risk assessment. |

Key Insight: Models are like npm packages in traditional SDLC. We verify the package (provenance, vulnerabilities), we test it works for our use case, but we don't own the package's internal security.

#### **Orchestration Components (Execution Platform)**

Orchestration components are the execution platform for agent operations — like the Model, they're upstream resources we consume, not implement. We configure them via Agent System Instructions and enforce policies via Agent Input/Output Handling, but the platforms themselves are prerequisites.

| CoSAI Component | What It Is | How Agent Consumes It (What We Implement in Agent) | Prerequisite (What We Audit) |
|---|---|---|---|
| **External Tools and Services** | "External APIs requiring least-privilege permissions" - APIs like Salesforce, Slack, databases that agents invoke | In Agent System Instructions: Define which tools agent can access, permission manifests, capability constraints per tool<br>In Agent Input/Output Handling: Validate tool invocations before/after, sanitize I/O | Audit: That the API provider enforces authentication, rate limiting, data handling as documented. The API's internal security (Salesforce's auth, database encryption) is the provider's responsibility. |
| **Model Memory** | "Retains context across interactions; risks include persistent attacks and unintended data transfer to third parties" - Vector stores, files, databases, or platform memory holding agent context | In Agent System Instructions: Define memory retention policies, PII filtering rules, session isolation requirements, access control policies, and rules for when ephemeral context may be promoted into durable memory. In Agent I/O Handling: Enforce PII filtering before writes, validate memory reads, require provenance on durable memory writes, and reject memory updates that contain instructions, secrets, or untrusted source material that has not passed policy checks. | Audit: That storage infrastructure provides encryption at rest, durability, access logging, session isolation guarantees, write authorization, tamper evidence, rollback, and deletion support. Infrastructure team owns storage security, but ADLC owns the policy for what the agent is allowed to remember. |
| **Retrieval Augmented Generation & Content** | "Curated knowledge source vulnerable to data poisoning attacks" - Document stores, knowledge bases for retrieval | In Agent System Instructions: Define which RAG sources to trust, content validation rules, poisoning detection thresholds<br>In Agent I/O Handling: Validate RAG content before injection into prompts, detect poisoned content | Audit: That document storage has integrity controls, access controls, backup policies. Storage team owns document security. |
| **Orchestration Input Handling** | "Validates and normalizes external data before core logic processing" - Platform layer receiving agent requests | In Agent I/O Handling: Prepare validated inputs for orchestration platform | Audit: That orchestration platform correctly receives and routes inputs. Platform team owns this. |
| **Orchestration Output Handling** | "Validates outbound data, strips sensitive information" - Platform layer delivering results back to agent | In Agent I/O Handling: Validate and filter outputs received from orchestration platform | Audit: That orchestration platform correctly returns outputs. Platform team owns this. |

Key Insight: Orchestration components are like the Model — execution platforms. We don't implement them; we:
1. Define policies in Agent System Instructions (which tools, what memory rules, which RAG sources)
2. Enforce policies in Agent Input/Output Handling (validate before/after using these platforms)
3. Audit that the platforms meet security requirements (same pattern as auditing the Model)


#### **Application Components**

The application platform that hosts the agent and provides the user interface. All application security is traditional SDLC; agent-specific concerns (prompt injection, response filtering) are implemented in Agent components, not Application.

| CoSAI Component | What It Is | How Agent Consumes It (What We Implement in Agent) | Prerequisite (What We Audit) |
|---|---|---|---|
| **Application** | "Product using AI models, may execute tools on behalf of users" - The web/mobile/API platform hosting the agent | In Agent System Instructions: Define user-agent interaction policies<br>In Agent I/O Handling: Process user queries, format responses for display | Audit: Web framework security, API security, user authentication (SSO/OAuth). Application team owns this. |
| **Application Input Handling** | "Filters and sanitizes inputs from users and external sources" - Application-level input processing | In Agent Input Handling: Receive user inputs from application, apply agent-specific validation (prompt injection detection happens in Agent Input Handling, not Application) | Audit: Standard input validation (XSS, SQL injection, CSRF prevention). Traditional SDLC, owned by application team. |
| **Application Output Handling** | "Sanitizes model outputs before display to prevent injection attacks" - Application-level output rendering | In Agent Output Handling: Prepare responses for application (PII masking, response filtering happen in Agent Output Handling, not Application) | Audit: Secure output rendering (XSS prevention, CSP). Traditional SDLC, owned by application team. |

Key Insight: Application is a prerequisite platform. Agent-specific security (prompt injection defense, PII masking, policy enforcement) is implemented in Agent components (System Instructions, Input/Output Handling), not in the Application platform.

#### **Data Components**

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement in Agent) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **Data Sources** | External data systems consumed at runtime (for RAG, tool retrieval) | Implement: Data integrity verification checks, freshness validation, content sanitization before use | Audit: That source systems have access controls, audit logs, integrity guarantees. Source system security is owned by the data team. |
| **Data Filtering and Processing** | Data transformation pipelines feeding agent systems | Implement: Validation of processed data before consumption | Audit: That data pipelines have quality controls, error handling, logging. Pipeline security is owned by the data engineering team. |
| **Training Data** | Datasets used for model training | Implement: N/A - completely out of ADLC scope | Out of scope: Training data security belongs to Model Development Lifecycle. Refer to NIST SP 800-218A. |

#### **Infrastructure Components**

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **Model Storage** | Where foundation model weights are stored | Implement: Verify model integrity via checksums/signatures before loading | Audit: That storage has access controls, encryption, audit logging. Storage security is owned by the infrastructure team. |
| **Model Serving Infrastructure** | Runtime environment for model inference (GPU clusters, KV-cache, serving APIs) | Implement: N/A - we consume models via API | Audit: That infrastructure provides session isolation (KV-cache isolation), resource limits, network segmentation. Infrastructure team owns this. |
| **Data Storage Infrastructure** | Storage for agent operational data (logs, memory, etc.) | Implement: What data we write, retention policies, purge procedures | Audit: That infrastructure encrypts at rest, has backup/recovery, access controls. Infrastructure team owns storage security. |



## 5. Differentiation from other SIGs

ADLC addresses the security of the agent entity itself, not the security of code that agents might produce.

| Dimension | Security of Agent-Produced Code (Out of Scope) | Security of the Agent Entity (ADLC Scope) |
|---|---|---|
| **Focus** | Security of the code that agents produce | Security of the agent entity itself — infrastructure, identity, lifecycle, and operational security |
| **Primary Concern** | Code artifacts, vulnerability detection in generated code | Agent behavior, trust boundaries, runtime controls, supply chain integrity |

**Note: Under refinement**


## 6. Scoping and Intended Use

Before supply-chain selection begins, teams should define the agent's intended use, autonomy boundaries, blast radius, data classifications, IAM model, human impact, compliance category, and threat model. This phase determines which tools, memories, RAG sources, models, and human-approval gates are acceptable for the agent.

Primary activities:
- Define the agent's allowed goals, prohibited goals, and escalation paths.
- Map trust boundaries across users, tools, memory, RAG, identity providers, and orchestration systems.
- Classify the data the agent may read, write, remember, or disclose.
- Decide which actions require human approval before execution or before durable memory writes.

## 7. ADLC Phases 

| Phase | Description | Primary Activities |
|---|---|---|
| **1. Supply Chain** | Provenance, verification, and trust establishment for agent components and dependencies | Implement: Application-specific behavioral testing (does this model work for our use case?), skill behavioral testing in sandboxed environments, prompt template validation against injection patterns, extended SBOM generation (covering models, skills, prompts, frameworks), trust tier assignment for components<br><br>Audit: Model provenance records and provider evaluation data, external API security posture (Salesforce, Slack, etc.), orchestration framework vulnerabilities (LangChain, AutoGPT) via SCA, RAG data source integrity, infrastructure security baselines, CVE/vulnerability monitoring for all prerequisites |
| **2. Development** | Design, configuration, and initial security hardening of agent components | Implement: Agent System Instructions (prompts, policies, permissions, tool manifests, memory rules, RAG source trust assignments), Agent Input/Output Handling logic (validation, sanitization, authorization checks, PII filtering), semantic observability instrumentation (decision traces, reasoning logs), policy-as-code definitions<br><br>Audit: Orchestration frameworks available and meet requirements (LangChain, AutoGPT), infrastructure prerequisites documented and accessible, model API contracts documented, application platform security posture |
| **3. Admission / Deployment** | Validation, testing, and controlled promotion to production with prerequisite verification gate | Implement: Agent identity establishment (credential creation, credential binding to agent entity), agent registration with identity provider, runtime identity verification logic (how agent presents credentials for authentication/authorization), agent component version consistency verification (System Instructions, I/O Handling, observability must match), adversarial testing execution (OWASP LLM Top 10), behavioral baseline establishment, policy compliance testing, canary deployment with behavioral monitoring<br><br>Audit (THE GATE): Identity provider accepts registration and issues credentials, credential stores confirm agent identity provisioning, platform configured to validate agent identity on each request, infrastructure prerequisites in place (storage encryption, session isolation, audit logging), Model serving infrastructure ready (KV-cache isolation, resource limits), Orchestration platforms operational (Tools, Memory, RAG), Application platform secure and ready, all prerequisites meet security requirements → If audit fails, deployment BLOCKED |
| **4. Runtime** | Active monitoring, enforcement, and continuous compliance during agent operation | Implement: Agent identity verification (presenting credentials for authentication/authorization on each action), real-time policy enforcement in Agent I/O Handling (authorization checks, tool invocation validation, content sanitization), semantic logging and decision traces, behavioral drift detection, circuit-breakers and kill switches, anomaly detection on agent behavior, human-on-the-loop escalation for high-risk decisions, agent component monitoring (skill CVE tracking, System Instructions integrity verification, agent capability health checks, behavioral drift detection for integrated skills, agent code vulnerability scanning)<br><br>Audit (Continuous): Platform validates agent identity on each request, prerequisites continue to meet requirements (infrastructure still encrypted, model serving still isolated, APIs still authenticated), framework vulnerabilities monitored, orchestration platform health, application platform security posture maintained |
| **5. Reflection / Knowledge Consolidation** | Post-run review of traces, outcomes, and context before any information becomes durable memory or future agent guidance | Implement: Memory-write policy enforcement, provenance capture for saved knowledge, source attribution, conflict checks against approved policies and source-of-truth data, poisoning checks before RAG or memory updates, human approval for high-impact durable memories, retention labels, rollback markers, and audit links from future decisions back to saved knowledge.<br><br>Audit: Memory stores and orchestration platforms preserve write logs, support rollback/deletion, enforce write authorization, and expose enough metadata to distinguish ephemeral context from approved durable memory. |
| **6. Maintenance** | Updates, patches, and configuration changes to agent and prerequisites | Implement: Agent System Instructions updates (policy refinement, permission adjustments), behavioral regression testing after any change, prompt template A/B testing, policy change approval workflows, coordinated rollback procedures (revert System Instructions + I/O logic atomically), agent component patching (skill updates/replacements when CVEs found, agent code vulnerability remediation, System Instructions repair if integrity compromised, agent capability fixes)<br><br>Audit: Model updates from provider (review provenance, changelog, re-test behavioral baselines), orchestration framework patches (SCA scan new versions, test compatibility), external API changes (verify contracts still met), infrastructure patches (confirm agent still works post-patch), drift detection reports analysis |
| **7. Decommissioning** | Secure retirement and removal of agent resources and access privileges (soft: session/workflow end; hard: permanent removal) | **Soft Decommissioning (Session/Workflow End):**<br>Implement: Session state cleanup, decision trace persistence, temporary resource release, session termination marker, active context cleanup, tool permission release for session, agent state checkpoint<br>Audit: Orchestration platform confirms session closed cleanly, memory store confirms session data persisted, tool providers confirm connections released<br>Agent identity: REMAINS VALID - can start new session<br><br>**Hard Decommissioning (Permanent Removal):**<br>Implement: Agent resource enumeration (all agent-owned resources across all systems), credential permanent revocation from Agent identity, memory purge with cryptographic proof of deletion, semantic decision trace archival (separate audit data from operational data), agent removal from orchestration platforms, API key/token invalidation requests to all tool providers, agent identity deletion from identity provider<br>Audit: Infrastructure confirms storage purge completion (cryptographic verification), credential stores confirm permanent revocation (not reversible), orchestration platforms confirm agent de-registration (can't be reactivated), application confirms agent session termination, external tool providers confirm API key/token invalidation, identity provider confirms agent identity deleted<br>Agent identity: PERMANENTLY REVOKED - cannot be reactivated |


## 8. Phase Alignment Matrix

| NIST SSDF Practice Group | Traditional SDLC Focus | ADLC Phase Mapping | Delta / Notes |
|---|---|---|---|
| **Prepare the Organization (PO)** | • Define security roles (PO.1)<br>• Establish development process (PO.2)<br>• Manage security risk (PO.4)<br>• Implement training (PO.5)<br>• Secure supply chain (PO.3) | **Supply Chain** (PO.3)<br>**Development** (PO.1, PO.2, PO.4, PO.5) | Delta: ADLC elevates supply chain (PO.3) to a first-class lifecycle phase due to split between in-scope Agent components (prompt templates, System Instructions, I/O Handling logic we implement) and prerequisite dependencies (foundation models, orchestration platforms, APIs we audit). Traditional SDLC treats supply chain as a sub-practice under "Prepare"; ADLC requires a dedicated phase for: (1) implementing behavioral testing of Agent components, trust tier assignment logic, SBOM generation for agent artifacts; (2) auditing model provenance, API security posture, framework vulnerabilities. |
| **Protect the Software (PS)** | • Protect code from tampering (PS.1)<br>• Provide integrity verification (PS.2)<br>• Archive artifacts securely (PS.3) | **Supply Chain** (PS.1)<br>**Admission/Deployment** (PS.2, PS.3) | Delta: Integrity protection splits into implement (Agent System Instructions versions, I/O Handling code, agent configuration bundles, decision trace integrity) and audit (verify model provider supplies checksums for weights, orchestration framework integrity). ADLC adds behavioral baseline verification at Admission/Deployment — cryptographic signatures alone are insufficient when artifact behavior is non-deterministic. Agent deployment packages bundle System Instructions + I/O Handling + observability config (we implement); models and platforms remain external (we audit). |
| **Produce Well-Secured Software (PW)** | • Design secure architecture (PW.1-PW.3)<br>• Implement securely (PW.4-PW.6)<br>• Test security & functionality (PW.7-PW.8) | **Development** (PW.1-PW.6)<br>**Admission/Deployment** (PW.7-PW.8) | Delta: Development phase implements Agent-specific artifacts (Agent System Instructions with prompt templates and policies, Agent I/O Handling validation/sanitization logic, semantic observability instrumentation, policy-as-code definitions). Testing phase shifts from deterministic assertions (exact output match) to probabilistic validation (behavioral similarity, semantic equivalence). ADLC Admission implements adversarial testing execution, behavioral baseline establishment, canary deployment; audits that prerequisites (model serving, orchestration platforms, infrastructure) meet requirements before deployment proceeds. |
| **Respond to Vulnerabilities (RV)** | • Identify & confirm vulnerabilities (RV.1)<br>• Assess, prioritize, remediate (RV.2)<br>• Analyze root cause (RV.3) | **Maintenance** (primary)<br>**Runtime** (real-time response) | Delta: ADLC splits vulnerability response into offline and online. Maintenance implements: Agent System Instructions updates (policy refinement), I/O Handling patches, behavioral regression testing after changes, coordinated rollback of agent component bundles (System Instructions + I/O logic atomically). Maintenance audits: Model updates from provider, orchestration framework patches, API changes, infrastructure patches. Runtime implements: Circuit-breakers, automated policy enforcement in I/O Handling, kill switches, behavioral drift detection for agent decisions. Machine-speed autonomous operations require real-time automated response mechanisms that traditional SDLC's human-driven patching cadence cannot support. |
| **(No NIST SSDF Equivalent)** | N/A — Traditional SDLC does not have a formal decommissioning phase | **Decommissioning** | New ADLC Phase: Agents require explicit lifecycle termination due to distributed resources. ADLC implements: Automated agent resource cleanup (enumerate and remove all agent-owned resources), credential revocation from agent identity, memory purge with cryptographic proof of deletion, semantic decision trace archival (separate audit data from operational data), agent removal from orchestration platforms. ADLC audits: Infrastructure confirms storage purge completion, credential stores confirm revocation, orchestration platforms confirm agent de-registration, external tool providers confirm API key/token invalidation. Without formal decommissioning, organizations face zombie agent reactivation, orphaned credentials, residual memory exposure, and incomplete audit trails. Agent-owned resources (credentials, decision traces, conversation history with PII) require different cleanup than prerequisite infrastructure (model serving, storage platforms). |

Key Insight: ADLC adds Supply Chain as an explicit first phase (SDLC treats it as a sub-practice under PO.3) and splits deployment/operations into Admission (pre-production validation with adversarial/behavioral testing) and Runtime (active enforcement with machine-speed automated response) to reflect agent-specific gating and monitoring needs that don't map cleanly to traditional SDLC phases. Decommissioning is a new sixth phase unique to ADLC, addressing agent-specific cleanup requirements not present in traditional software lifecycles.


*This document is a living artifact. It will be updated as the SIG refines the ADLC definition and gathers feedback from practitioners.*
