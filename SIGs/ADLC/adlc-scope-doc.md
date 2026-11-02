# SIG Agent Development Lifecycle (ADLC) Scope Definition

**Workstream:** WS4, SIG ADLC  
**Priority:** High  
**Version:** 2.0 — Draft for Review  
**Status:** Ready for Review  
**Date:** 2026-10-29  

**Authors:**  
Parul Singh, Red Hat  


## 1. Summary

The SIG Security of Agent Development Lifecycle (Agent Development Lifecycle, ADLC) defines security controls for autonomous and semi-autonomous AI agent systems. The ADLC extends traditional Secure Software Development Lifecycle (SDLC) frameworks to address autonomous decision-making, non-deterministic behavior, and runtime tool invocation.

This document maps agent-specific security requirements onto NIST SSDF and OWASP SAMM to show where agent security differs from traditional software security.

**v2.0 additions:**

Modality-specific security measures for images, video, and audio inputs use Rouge/Bleu-like thresholds. Event-driven architecture supports JSON-RPC plus URI eventing for decision models. Decision model integration uses llama.cpp's non-autoregressive classification models. Agent Manifest serves as a signed pre-execution declaration binding deployment artifacts. Fail-Closed Agent Authorization control applies per-turn permission pruning.

## 2. Target Audience & Personas

ADLC uses the [CoSAI (Common Sense AI) persona guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md) to define temporary responsibilities and required controls rather than prescribing organizational titles.

| Persona | Description |
|---|---|
| **Agent Developers** | Those building and configuring agentic systems |
| **Agentic Security Framework Developers** | Those creating tooling and infrastructure for secure agent operations |
| **Security & Risk Officers (CISO/CRO)** | Those establishing IT security and business control policies |
| **Third-Party Risk Management (TPRM) Teams** | Those evaluating and procuring commercial off-the-shelf agentic solutions |
| **Enterprise Architecture Teams** | Those integrating agents into existing security ecosystems |

## 3. Methodology

**Baseline Framework:** NIST SSDF (National Institute of Standards and Technology Secure Software Development Framework) SP 800-218  
**Supplementary Framework:** OWASP SAMM (Open Web Application Security Project Software Assurance Maturity Model)  

#### External Resource Control Principle

Models, orchestration frameworks (LangChain, AutoGPT), APIs, data services, and registries are upstream resources. ADLC does not own their internal security. ADLC owns how agents consume them: provenance verification, trust establishment, capability constraints, and runtime monitoring.

#### Implement vs. Audit Distinction

Components fall into two categories based on who owns their security:

ADLC Implements (In Scope): Agent-owned components and the controls that govern how the agent uses or changes adjacent systems. We directly build, configure, and enforce controls in the agent entity, and we define the requirements that prerequisite systems must satisfy for the agent to use them safely. Examples:
- Writing agent system instructions with injection-resistant prompt design and policy definitions
- Defining tool permissions, memory policies, retrieval augmented generation (RAG) source trust assignments in Agent System Instructions
- Implementing input/output sanitization in Agent Input/Output Handling
- Enforcing policy decisions (authorization checks) before agent uses external resources
- Establishing business-specific baseline behavior before agents along with their tools and capabilities are admitted

ADLC Audits (Prerequisites): Model, Orchestration, Application, Data, Infrastructure components. Security is owned by external providers or platform teams. We verify requirements are met but do not implement the platforms. Examples:
- Auditing that a foundation model provider supplies provenance records and safety evaluations
- Verifying that the Tools platform (Salesforce API, etc.) enforces authentication and rate limiting as documented
- Confirming that Memory storage infrastructure provides session isolation and encryption
- Validating that RAG document storage has integrity controls and access policies
- Checking that Infrastructure provides KV-cache isolation for model serving

The Pattern: 
- ADLC implements Agent component policies and enforcement (System Instructions define policies, Input/Output Handling enforce them)
- ADLC audits prerequisite platforms (Model, Orchestration, Data, Infrastructure execute the policies but we do not own them)

#### Lifecycle Phases vs. Component Categories

Component Categories (CoSAI Risk Map) describe *what* components exist: Agent, Model, Orchestration, Application, Data, Infrastructure.

Lifecycle Phases (ADLC) describe *when* activities happen: Supply Chain, Development, Admission/Deployment, Runtime, Maintenance, Decommissioning.

Example: Policy enforcement is implemented in Agent components (System Instructions define policies for tools, memory, RAG; Input/Output Handling enforce them). These controls are established during Admission/Deployment phase and actively enforced during Runtime phase. The Orchestration platform executes these policies but is a prerequisite.

#### Multimodal Security Extension

ADLC extends input/output handling to address modality-specific attack surfaces. For non-text modalities—images, video, and audio—ADLC requires:

- Modality-specific validation frameworks. Each modality has unique attack vectors: pixel-level adversarial perturbations for images, psychoacoustic payloads for audio, hidden bandwidth in video.
- Rouge/Bleu-like metrics against unstructured data with defined thresholds for quality and safety assessment.
- Provenance tracking and trust labeling per modality. Every input is tagged with origin (user-typed vs. tool output vs. fetched web image vs. uploaded document).
- Preprocessing exploits mitigation. Image scaling, resampling, and denoising defenses are tailored to each modality.

#### Event-Driven Architecture Expectation

ADLC incorporates an event-driven architecture to support:

- Eventing of JSON-RPC plus URIs. Agent actions and decisions are emitted as events for observability and audit.
- Decision models and specialized LMs in a fail-closed auth x SDK-style approach. Decision models (like llama.cpp's decision models) make classifications to route actions, with probabilities enabling programmatic delegation without human-in-the-loop for every decision.
- llama.cpp decision model support. Non-autoregressive, single-forward-pass classification models score options with probabilities, enabling low-latency agentic decisions (e.g., Clef models at ~2.2s vs. 4.7s for general LLMs).

The event-driven pattern enables real-time policy enforcement via event streams, decision trace logging as immutable auditable records, correlation of runtime evidence with pre-execution manifest declarations, and fail-closed authorization where missing or invalid events result in denial.

#### Fail-Closed Agent Authorization Control

ADLC implements a Fail-Closed Agent Authorization control with three portable properties:

1. Principal ARN Permission Pruning per turn. Agents inherit a subset of IAM permissions; each turn prunes entitlements based on context.
2. Aggregated Context Classification per turn. Durable data classification is applied to subsequent forward-passes.
3. Provenance & No Persistence per turn. Proof of Work and non-exploit guarantees without data persistence.

Portable JSON-RPC attestation is hashed together per-turn to prevent spoofing. This control applies across all components because prompt-injection is a durable risk.

## 4. Component Category Scope (CoSAI Taxonomy)

ADLC uses the [CoSAI Secure AI Tooling Risk Map](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/components-full.md) component taxonomy to establish scope boundaries. See [Risk Map Visualization](https://raw.githubusercontent.com/cosai-oasis/secure-ai-tooling/refs/heads/main/risk-map/svg/risk-map-graph.svg) for component relationships.

### 4.1. In-Scope Components (ADLC Implements Controls)

Agent components are the only in-scope components. Everything else (Model, Orchestration, Application, Data, Infrastructure) is a prerequisite.

#### Agent Components

The agent entity is the core decision-making unit. All agent security is defined and enforced through its immediate inputs and outputs.

| CoSAI Component | CoSAI Definition | What We Implement |
|---|---|---|
| **Agent System Instructions** | "Define agent capabilities, permissions, and limitations using control tokens against prompt injection" | This is where all policies are defined: prompt templates with injection-resistant design; policy-as-code (which tools, memory rules, RAG sources); permission manifests (least-privilege per tool); constraint rules (data handling, output restrictions); tool permission configurations; memory retention and personally identifiable information (PII) filtering policies; retrieval augmented generation (RAG) source trust assignments; modality-specific trust labels for image/video/audio inputs; decision model invocation policies (when to route to decision models vs. general LLMs) |
| **Agent Reasoning Core** | "Plans and executes actions through tool calls" — the decision-making intelligence (LLM or rule-based logic). Takes system instructions + user query → produces reasoning and decisions. | Prompt engineering; runtime context assembly (System Instructions + User Query + Memory + RAG); decision trace logging; semantic observability instrumentation; decision model integration (llama.cpp decision models for low-latency classification); event emission for JSON-RPC calls and URI accesses. The foundation model itself is a prerequisite — we audit it, not implement it. |
| **Agent User Query** | "Processed user request details combined with system instructions and contextual data" | Query preprocessing; intent extraction; user input preparation for runtime context assembly; modality detection and routing (text vs. image vs. video vs. audio); per-modality provenance tagging |
| **Agent Input Handling** | "Distinguishing trusted commands from untrusted data to prevent manipulation" | Input validation frameworks; sanitization logic; prompt injection detection; trusted/untrusted data separation; pre-invocation authorization checks; modality-specific adversarial robustness controls (randomized smoothing for vision, resampling for audio); JSON-RPC attestation hashing per-turn |
| **Agent Output Handling** | "Formats AI-generated output for display, preventing malicious content execution and data exfiltration through proper sanitization" | Output sanitization; personally identifiable information (PII) masking and sensitive data filtering; response validation; exfiltration prevention; post-invocation data loss prevention; modality-specific output validation (Rouge/Bleu-like thresholds for unstructured data); event-driven output emission for audit trails |


### 4.2. Prerequisite Components (ADLC Audits Controls)

For these components, ADLC does not implement their internal security. ADLC implements consumption controls within Agent components (System Instructions define policies, Input/Output Handling enforce them), but the underlying platforms are prerequisites we audit.

#### Model Components

Foundation models and their development lifecycle are upstream resources. ADLC treats them like third-party libraries in traditional SDLC — we verify provenance and integrity, but we do not build or secure them internally.

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **The Model** | Foundation model weights and serving API | Provenance verification checks; trust tier assignment logic; capability constraints in prompts; behavioral drift monitoring; model output validation. Decision Models: integrate llama.cpp decision models (Clef, Julia, Laya, Kev) for low-latency classification with probability scores. Multimodal Models: apply modality-specific provenance and trust labeling. | That the model provider supplies provenance records, safety evaluations, documented capabilities/limitations. The model's internal security (training, weights) is owned by the provider. |
| **Training and Tuning** | Model training and fine-tuning processes | N/A - out of scope | That training provenance is documented by provider (if we consume a fine-tuned model). Refer to NIST SP 800-218A for Model Development Lifecycle security. |
| **Model Evaluation** | Model testing, validation, bias assessment | Our own application-specific behavioral testing (does the model work for our use case?); modality-specific adversarial testing (per CSA guidance: typographic, steganographic, and perturbation classes for vision-capable systems); BrowseSafe++ benchmark integration for indirect prompt injection detection. | Provider evaluation reports, benchmark results, safety testing, red team assessments. We do not conduct the model's bias testing; we audit that it was done. |
| **Model Frameworks and Code** | Training/inference frameworks (PyTorch, TensorFlow, vLLM) | N/A - we consume models via API, not frameworks | That model providers use secure frameworks, if relevant to our risk assessment. |

Models function like npm packages in traditional SDLC. We verify provenance and vulnerabilities, test that a model works for our use case, and do not own the package's internal security.

#### Orchestration Components (Execution Platform)

Orchestration components are the execution platform for agent operations — like the Model, they're upstream resources we consume, not implement. We configure them via Agent System Instructions and enforce policies via Agent Input/Output Handling, but the platforms themselves are prerequisites.

| CoSAI Component | What It Is | How Agent Consumes It (What We Implement in Agent) | Prerequisite (What We Audit) |
|---|---|---|---|
| **External Tools and Services** | "External APIs requiring least-privilege permissions" - APIs like Salesforce, Slack, databases that agents invoke | In Agent System Instructions: define which tools agent can access, permission manifests, capability constraints per tool. In Agent Input/Output Handling: validate tool invocations before/after, sanitize I/O. Event-driven: emit JSON-RPC events with URIs for all tool invocations. | That the API provider enforces authentication, rate limiting, data handling as documented. The API's internal security (Salesforce's auth, database encryption) is the provider's responsibility. |
| **Model Memory** | "Retains context across interactions; risks include persistent attacks and unintended data transfer to third parties" - Vector stores, files, databases, or platform memory holding agent context | In Agent System Instructions: define memory retention policies, personally identifiable information (PII) filtering rules, session isolation requirements, access control policies, and rules for when ephemeral context may be promoted into durable memory. In Agent I/O Handling: enforce PII filtering before writes, validate memory reads, require provenance on durable memory writes, and reject memory updates that contain instructions, secrets, or untrusted source material that has not passed policy checks. | That storage infrastructure provides encryption at rest, durability, access logging, session isolation guarantees, write authorization, tamper evidence, rollback, and deletion support. Infrastructure team owns storage security, but ADLC owns the policy for what the agent is allowed to remember. |
| **Retrieval Augmented Generation & Content** | "Curated knowledge source vulnerable to data poisoning attacks" - Document stores, knowledge bases for retrieval | In Agent System Instructions: define which RAG sources to trust, content validation rules, poisoning detection thresholds. In Agent I/O Handling: validate RAG content before injection into prompts, detect poisoned content. | That document storage has integrity controls, access controls, backup policies. Storage team owns document security. |
| **Orchestration Input Handling** | "Validates and normalizes external data before core logic processing" - Platform layer receiving agent requests | In Agent I/O Handling: prepare validated inputs for orchestration platform. Event-driven: receive and process events from orchestration layer. | That orchestration platform correctly receives and routes inputs. Platform team owns this. |
| **Orchestration Output Handling** | "Validates outbound data, strips sensitive information" - Platform layer delivering results back to agent | In Agent I/O Handling: validate and filter outputs received from orchestration platform. Event-driven: emit output events for audit. | That orchestration platform correctly returns outputs. Platform team owns this. |

Orchestration components function as execution platforms, similar to Models. We define policies in Agent System Instructions, enforce them in Agent Input/Output Handling, and audit that the platforms meet security requirements.

#### Application Components

The application platform hosts the agent and provides the user interface. All application security is traditional SDLC; agent-specific concerns (prompt injection, response filtering) are implemented in Agent components, not Application.

| CoSAI Component | What It Is | How Agent Consumes It (What We Implement in Agent) | Prerequisite (What We Audit) |
|---|---|---|---|
| **Application** | "Product using AI models, may execute tools on behalf of users" - The web/mobile/API platform hosting the agent | In Agent System Instructions: define user-agent interaction policies. In Agent I/O Handling: process user queries, format responses for display. | Web framework security, API security, user authentication (SSO/OAuth). Application team owns this. |
| **Application Input Handling** | "Filters and sanitizes inputs from users and external sources" - Application-level input processing | In Agent Input Handling: receive user inputs from application, apply agent-specific validation (prompt injection detection happens in Agent Input Handling, not Application). Multimodal: apply modality-specific preprocessing (image scaling defenses, audio resampling). | Standard input validation (XSS, SQL injection, CSRF prevention). Traditional SDLC, owned by application team. |
| **Application Output Handling** | "Sanitizes model outputs before display to prevent injection attacks" - Application-level output rendering | In Agent Output Handling: prepare responses for application (PII masking, response filtering happen in Agent Output Handling, not Application). Multimodal: apply Rouge/Bleu-like thresholds for unstructured data output validation. | Secure output rendering (XSS prevention, CSP). Traditional SDLC, owned by application team. |

Application is a prerequisite platform. Agent-specific security is implemented in Agent components, not in the Application platform.

#### Data Components

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement in Agent) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **Data Sources** | External data systems consumed at runtime (for RAG, tool retrieval) | Data integrity verification checks, freshness validation, content sanitization before use. Multimodal: apply modality-specific provenance tracking. | That source systems have access controls, audit logs, integrity guarantees. Source system security is owned by the data team. |
| **Data Filtering and Processing** | Data transformation pipelines feeding agent systems | Validation of processed data before consumption. Event-driven: process event streams from data pipelines. | That data pipelines have quality controls, error handling, logging. Pipeline security is owned by the data engineering team. |
| **Training Data** | Datasets used for model training | N/A - completely out of ADLC scope | Out of scope: Training data security belongs to Model Development Lifecycle. Refer to NIST SP 800-218A. |

#### Infrastructure Components

| CoSAI Component | What It Is | ADLC Consumption Controls (What We Implement) | Out of ADLC Scope (What We Audit) |
|---|---|---|---|
| **Model Storage** | Where foundation model weights are stored | Verify model integrity via checksums/signatures before loading. Decision Models: verify decision model provenance (Clef, Julia, Laya, Kev GGUF files). | That storage has access controls, encryption, audit logging. Storage security is owned by the infrastructure team. |
| **Model Serving Infrastructure** | Runtime environment for model inference (GPU clusters, KV-cache, serving APIs) | N/A - we consume models via API. Event-driven: configure event emission from model serving layer. | That infrastructure provides session isolation (KV-cache isolation), resource limits, network segmentation. Infrastructure team owns this. |
| **Data Storage Infrastructure** | Storage for agent operational data (logs, memory, etc.) | What data we write, retention policies, purge procedures. Event-driven: store event streams for audit. | That infrastructure encrypts at rest, has backup/recovery, access controls. Infrastructure team owns storage security. |



## 5. Differentiation from other SIGs

ADLC addresses the security of the agent entity itself, not the security of code that agents might produce.

| Dimension | Security of Agent-Produced Code (Out of Scope) | Security of the Agent Entity (ADLC Scope) |
|---|---|---|
| **Focus** | Security of the code that agents produce | Security of the agent entity itself — infrastructure, identity, lifecycle, and operational security |
| **Primary Concern** | Code artifacts, vulnerability detection in generated code | Agent behavior, trust boundaries, runtime controls, supply chain integrity |

**Note: Under refinement**


## 6. Scoping and Intended Use

Before supply-chain selection begins, teams should define the agent's intended use, autonomy boundaries, blast radius, data classifications, identity and access management (IAM) model, human impact, compliance category, and threat model. This phase determines which tools, memories, RAG sources, models, and human-approval gates are acceptable for the agent.

Primary activities:
- Define the agent's allowed goals, prohibited goals, and escalation paths.
- Map trust boundaries across users, tools, memory, RAG, identity providers, and orchestration systems.
- Classify the data the agent may read, write, remember, or disclose.
- Decide which actions require human approval before execution or before durable memory writes.
- Define modality-specific thresholds for Rouge/Bleu-like metrics against unstructured data.
- Establish event-driven architecture requirements for JSON-RPC + URI eventing.
- Select decision models (llama.cpp Clef, Julia, Laya, Kev) for low-latency classification tasks.
- Configure fail-closed authorization with per-turn permission pruning and JSON-RPC attestation.

## 7. ADLC Phases 

| Phase | Description | Primary Activities |
|---|---|---|
| **1. Supply Chain** | Provenance, verification, and trust establishment for agent components and dependencies | Implement: Application-specific behavioral testing (does this model work for our use case?), skill behavioral testing in sandboxed environments, prompt template validation against injection patterns, extended software bill of materials (SBOM) generation (covering models, skills, prompts, frameworks), trust tier assignment for components. Multimodal: BrowseSafe++ benchmark integration for indirect prompt injection detection. Decision Models: verify llama.cpp decision model provenance and integrity. Audit: Model provenance records and provider evaluation data, external API security posture (Salesforce, Slack, etc.), orchestration framework vulnerabilities (LangChain, AutoGPT) via SCA, RAG data source integrity, infrastructure security baselines, CVE/vulnerability monitoring for all prerequisites |
| **2. Development** | Design, configuration, and initial security hardening of agent components | Implement: Agent System Instructions (prompts, policies, permissions, tool manifests, memory rules, RAG source trust assignments), Agent Input/Output Handling logic (validation, sanitization, authorization checks, PII filtering), semantic observability instrumentation (decision traces, reasoning logs), policy-as-code definitions. Modality-specific: per-modality input validation frameworks (image adversarial robustness, audio resampling/denoising). Event-driven: JSON-RPC + URI event emission design. Decision models: integration points for llama.cpp decision models. Audit: Orchestration frameworks available and meet requirements (LangChain, AutoGPT), infrastructure prerequisites documented and accessible, model API contracts documented, application platform security posture |
| **3. Admission / Deployment** | Validation, testing, and controlled promotion to production with prerequisite verification gate | Implement: Agent identity establishment (credential creation, credential binding to agent entity), agent registration with identity provider, runtime identity verification logic (how agent presents credentials for authentication/authorization), agent component version consistency verification (System Instructions, I/O Handling, observability must match), adversarial testing execution (OWASP LLM Top 10), behavioral baseline establishment, policy compliance testing, canary deployment with behavioral monitoring. Agent Manifest: signed pre-execution declaration binding 10 deployment artifacts (system prompt, policy bundle, model identity, tool schemas, RAG corpus, memory baseline, decision trace, A2A delegation chain, build provenance, HITL approvals). Fail-Closed Auth: configure per-turn permission pruning and JSON-RPC attestation. Audit (THE GATE): Identity provider accepts registration and issues credentials, credential stores confirm agent identity provisioning, platform configured to validate agent identity on each request, infrastructure prerequisites in place (storage encryption, session isolation, audit logging), Model serving infrastructure ready (KV-cache isolation, resource limits), Orchestration platforms operational (Tools, Memory, RAG), Application platform secure and ready, all prerequisites meet security requirements → If audit fails, deployment BLOCKED |
| **4. Runtime** | Active monitoring, enforcement, and continuous compliance during agent operation | Implement: Agent identity verification (presenting credentials for authentication/authorization on each action), real-time policy enforcement in Agent I/O Handling (authorization checks, tool invocation validation, content sanitization), semantic logging and decision traces, behavioral drift detection, circuit-breakers and kill switches, anomaly detection on agent behavior, human-on-the-loop escalation for high-risk decisions, agent component monitoring (skill CVE tracking, System Instructions integrity verification, agent capability health checks, behavioral drift detection for integrated skills, agent code vulnerability scanning). Event-driven: process JSON-RPC + URI events for real-time policy enforcement. Modality-specific: per-modality provenance tracking and trust label propagation. Decision models: runtime classification with probability-based routing. Audit (Continuous): Platform validates agent identity on each request, prerequisites continue to meet requirements (infrastructure still encrypted, model serving still isolated, APIs still authenticated), framework vulnerabilities monitored, orchestration platform health, application platform security posture maintained |
| **5. Reflection / Knowledge Consolidation** | Post-run review of traces, outcomes, and context before any information becomes durable memory or future agent guidance | Implement: Memory-write policy enforcement, provenance capture for saved knowledge, source attribution, conflict checks against approved policies and source-of-truth data, poisoning checks before RAG or memory updates, human approval for high-impact durable memories, retention labels, rollback markers, and audit links from future decisions back to saved knowledge. Event-driven: correlate runtime events with pre-execution manifest declarations. Audit: Memory stores and orchestration platforms preserve write logs, support rollback/deletion, enforce write authorization, and expose enough metadata to distinguish ephemeral context from approved durable memory. |
| **6. Maintenance** | Updates, patches, and configuration changes to agent and prerequisites | Implement: Agent System Instructions updates (policy refinement, permission adjustments), behavioral regression testing after any change, prompt template A/B testing, policy change approval workflows, coordinated rollback procedures (revert System Instructions + I/O logic atomically), agent component patching (skill updates/replacements when CVEs found, agent code vulnerability remediation, System Instructions repair if integrity compromised, agent capability fixes). Decision models: re-test behavioral baselines after decision model updates. Audit: Model updates from provider (review provenance, changelog, re-test behavioral baselines), orchestration framework patches (SCA scan new versions, test compatibility), external API changes (verify contracts still met), infrastructure patches (confirm agent still works post-patch), drift detection reports analysis |
| **7. Decommissioning** | Secure retirement and removal of agent resources and access privileges (soft: session/workflow end; hard: permanent removal) | **Soft Decommissioning (Session/Workflow End):** Implement: Session state cleanup, decision trace persistence, temporary resource release, session termination marker, active context cleanup, tool permission release for session, agent state checkpoint. Audit: Orchestration platform confirms session closed cleanly, memory store confirms session data persisted, tool providers confirm connections released. Agent identity: REMAINS VALID - can start new session. **Hard Decommissioning (Permanent Removal):** Implement: Agent resource enumeration (all agent-owned resources across all systems), credential permanent revocation from Agent identity, memory purge with cryptographic proof of deletion, semantic decision trace archival (separate audit data from operational data), agent removal from orchestration platforms, API key/token invalidation requests to all tool providers, agent identity deletion from identity provider. Retirement Readiness: establish retirement triggers, maintain behavior account, retain operational knowledge extraction capability before teardown. Audit: Infrastructure confirms storage purge completion (cryptographic verification), credential stores confirm permanent revocation (not reversible), orchestration platforms confirm agent de-registration (can't be reactivated), application confirms agent session termination, external tool providers confirm API key/token invalidation, identity provider confirms agent identity deleted. Agent identity: PERMANENTLY REVOKED - cannot be reactivated |


## 8. Phase Alignment Matrix

| NIST SSDF Practice Group | Traditional SDLC Focus | ADLC Phase Mapping | Delta / Notes |
|---|---|---|---|
| **Prepare the Organization (PO)** | • Define security roles (PO.1)<br>• Establish development process (PO.2)<br>• Manage security risk (PO.4)<br>• Implement training (PO.5)<br>• Secure supply chain (PO.3) | **Supply Chain** (PO.3)<br>**Development** (PO.1, PO.2, PO.4, PO.5) | ADLC elevates supply chain (PO.3) to a first-class lifecycle phase due to split between in-scope Agent components (prompt templates, System Instructions, I/O Handling logic we implement) and prerequisite dependencies (foundation models, orchestration platforms, APIs we audit). Traditional SDLC treats supply chain as a sub-practice under "Prepare"; ADLC requires a dedicated phase for: (1) implementing behavioral testing of Agent components, trust tier assignment logic, SBOM generation for agent artifacts; (2) auditing model provenance, API security posture, framework vulnerabilities. |
| **Protect the Software (PS)** | • Protect code from tampering (PS.1)<br>• Provide integrity verification (PS.2)<br>• Archive artifacts securely (PS.3) | **Supply Chain** (PS.1)<br>**Admission/Deployment** (PS.2, PS.3) | Integrity protection splits into implement (Agent System Instructions versions, I/O Handling code, agent configuration bundles, decision trace integrity, Agent Manifest signatures) and audit (verify model provider supplies checksums for weights, orchestration framework integrity). ADLC adds behavioral baseline verification at Admission/Deployment — cryptographic signatures alone are insufficient when artifact behavior is non-deterministic. Agent deployment packages bundle System Instructions + I/O Handling + observability config + Agent Manifest (we implement); models and platforms remain external (we audit). |
| **Produce Well-Secured Software (PW)** | • Design secure architecture (PW.1-PW.3)<br>• Implement securely (PW.4-PW.6)<br>• Test security & functionality (PW.7-PW.8) | **Development** (PW.1-PW.6)<br>**Admission/Deployment** (PW.7-PW.8) | Development phase implements Agent-specific artifacts (Agent System Instructions with prompt templates and policies, Agent I/O Handling validation/sanitization logic, semantic observability instrumentation, policy-as-code definitions). Testing phase shifts from deterministic assertions (exact output match) to probabilistic validation (behavioral similarity, semantic equivalence, modality-specific Rouge/Bleu thresholds). ADLC Admission implements adversarial testing execution, behavioral baseline establishment, canary deployment; audits that prerequisites (model serving, orchestration platforms, infrastructure) meet requirements before deployment proceeds. |
| **Respond to Vulnerabilities (RV)** | • Identify & confirm vulnerabilities (RV.1)<br>• Assess, prioritize, remediate (RV.2)<br>• Analyze root cause (RV.3) | **Maintenance** (primary)<br>**Runtime** (real-time response) | ADLC splits vulnerability response into offline and online. Maintenance implements: Agent System Instructions updates (policy refinement), I/O Handling patches, behavioral regression testing after changes, coordinated rollback of agent component bundles (System Instructions + I/O logic atomically). Maintenance audits: Model updates from provider, orchestration framework patches, API changes, infrastructure patches. Runtime implements: Circuit-breakers, automated policy enforcement in I/O Handling, kill switches, behavioral drift detection for agent decisions, fail-closed authorization responses. Machine-speed autonomous operations require real-time automated response mechanisms that traditional SDLC's human-driven patching cadence cannot support. |
| **(No NIST SSDF Equivalent)** | N/A — Traditional SDLC does not have a formal decommissioning phase | **Decommissioning** | New ADLC Phase: Agents require explicit lifecycle termination due to distributed resources. ADLC implements: Automated agent resource cleanup (enumerate and remove all agent-owned resources), credential revocation from agent identity, memory purge with cryptographic proof of deletion, semantic decision trace archival (separate audit data from operational data), agent removal from orchestration platforms. ADLC audits: Infrastructure confirms storage purge completion, credential stores confirm revocation, orchestration platforms confirm agent de-registration, external tool providers confirm API key/token invalidation. Without formal decommissioning, organizations face zombie agent reactivation, orphaned credentials, residual memory exposure, and incomplete audit trails. Agent-owned resources (credentials, decision traces, conversation history with PII) require different cleanup than prerequisite infrastructure (model serving, storage platforms). |

ADLC adds Supply Chain as an explicit first phase (SDLC treats it as a sub-practice under PO.3) and splits deployment/operations into Admission (pre-production validation with adversarial/behavioral testing) and Runtime (active enforcement with machine-speed automated response) to reflect agent-specific gating and monitoring needs. Decommissioning is a new seventh phase unique to ADLC, addressing agent-specific cleanup requirements not present in traditional software lifecycles.

**v2.0 Additions:**
- Modality-specific security measures integrated across Development, Admission, and Runtime phases
- Event-driven architecture supporting JSON-RPC + URI eventing for decision models and specialized LMs
- Agent Manifest as a signed pre-execution declaration binding deployment artifacts at Admission/Deployment
- Fail-Closed Agent Authorization control with per-turn permission pruning and JSON-RPC attestation

*This document is a living artifact. It will be updated as the SIG refines the ADLC definition and gathers feedback from practitioners.*
