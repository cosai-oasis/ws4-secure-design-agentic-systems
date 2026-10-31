# A Modality-Independent Taxonomy for Multimodal Agentic Security

## Abstract


## 1. Introduction

Enterprise AI systems have moved rapidly beyond text-only chat interfaces into multimodal agents that inspect documents and screenshots, transcribe voice calls, monitor video streams, invoke external tools, and render rich outputs across connected services. Whether built around a single unified multimodal model or a pipeline of specialized extractors and orchestrators, production deployments routinely put preprocessing steps (resizers, codecs, parsers, OCR or speech extractors) upstream of the model, and attach tool executors and active client renderers downstream.

### 1.1 Background: Limitations of Current Security Practices

Today, application-security teams assess AI agents by combining two established practices, neither of which captures how multimodal agentic pipelines actually fail:

1. **Coarse-grained STRIDE threat modeling.** Standard application threat models draw trust boundaries around whole services or around "the AI model" as a single opaque box. Inside an inference pipeline, however, security-critical transformations happen *between* components that sit inside the same traditional trust zone: a guardrail inspects a full-resolution image before a downscaler resizes it for the model, or a human reviewer previews an HTML draft whose embedded image tags trigger outbound network fetches before approval.
2. **Modality-siloed catalogs and point guardrails.** AI threat and risk catalogs (e.g. OWASP Top 10 for LLM Applications, MITRE ATLAS, and NIST AI 100-2) classify *what* the adversary does (such as prompt injection or multimodal triggers) and *which* business risks result. In response, engineering teams add point defenses one surface at a time: a text prompt filter on chat inputs, an image classifier on file uploads, an audio check on voice lines.

Recent disclosures and research demonstrations show the gaps between these separate catalogs and defenses:

* **Image preprocessing.** Trail of Bits demonstrated an end-to-end attack against Google Gemini CLI in which an uploaded image looked benign at original resolution, revealed an injected prompt only after downscaling, and exfiltrated Google Calendar entries through auto-approved Zapier MCP tool calls.
* **Audio perception.** AudioHijack (IEEE S&P 2026) demonstrated that reverberation-disguised audio perturbations imperceptible to human listeners can steer audio-language voice agents into unauthorized actions, while physical-world adversarial patches (Eykholt et al., CVPR 2018; Tencent Keen Lab, 2019) mislead vision-driven vehicles without any text prompt at all.
* **Output rendering.** In Cursor (`CVE-2025-54132`) and M365 Copilot EchoLeak (`CVE-2025-32711`), prompt injection induced the model to emit active Markdown or Mermaid markup whose preview renderer automatically fetched attacker-controlled URLs, exfiltrating sensitive context before user action.

Treating these as separate "image attacks," "audio attacks," and "rendering bugs" does not scale. Every new input channel or output surface needs its own threat catalog and test suite, and cross-modal attacks that combine two individually benign inputs are not detected by single-modality checks. Organizations also cannot wait for extensive production incident data in every modality before standardizing architectural review. As of October 2026, public vulnerability disclosures and incident trackers (NVD/CVE, the AI Incident Database (AIID), and MITRE ATLAS case studies) record widespread text-borne indirect prompt injections in deployed agents. Non-text agentic compromises, by contrast, appear mostly as researcher demonstrations and disclosed CVEs against production tools, with no confirmed criminal campaigns observed outside research settings. Organizations deploying multimodal agents therefore need an architectural method that works before incident data is available.

### 1.2 Core Thesis: Shared Mechanisms on an Annotated Data-Flow Diagram

**This paper argues that multimodal agentic attacks across text, images, audio, video, and physical sensors are instances of a small set of modality-independent failure mechanisms determined by pipeline topology.** In the Trail of Bits exploit, the human user inspected the image at one resolution while the model consumed it at another. That exact structural divergence recurs when a text guardrail scans URL-encoded strings before decoding, when a video safety sampler checks sparse keyframes while the model reads a denser frame grid, or (as a testable prediction) when an audio front end decimates a high-sample-rate waveform without anti-alias filtering before speech recognition. The carrier modality is different in each case, but the broken architectural assumption is the same.

To enumerate those mechanisms systematically instead of brainstorming them case by case, we pair a three-part mechanism definition, **`M = ⟨Invariant, Divergence, Representation⟩`** (Section 3), with a **four-step derivation method over an annotated data-flow diagram (DFD)** (Section 4):

* **Invariant** names the explicit sink constraint the system relies upon (*Meaning*, *Flow* for integrity and confidentiality, or *Cost*).
* **Divergence** names why two evaluations assumed to agree actually differ (*Evaluator*, *Artifact State*, *Time*, or *Position*).
* **Representation** names the observable form in which adversarial influence travels (*Overt Semantic*, *Encoded / Obfuscated*, *Steganographic*, or *Adversarial Perturbation*) and whether it survives the representational fidelity (`Full`, `Normalized`, or `Typed`) of each data flow.

The method adds three lightweight annotations to the standard DFDs architects already draw for STRIDE: component functional roles, flow trust labels and fidelities, and per-sink security constraints. From the annotated diagram, candidate crossings, multi-step attack chains, high-leverage structural cut points, and falsifiable security tests can be derived systematically.

### 1.3 Ecosystem Positioning

This work covers the inside of the pipeline, which sits between existing adversary catalogs and downstream risk or control frameworks (**Figure 1**). It is meant to be used alongside those frameworks:

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 24, "rankSpacing": 36}}}%%
flowchart LR
    IN["Untrusted Input<br/>«source»"]:::outer

    subgraph ZONE["Traditional STRIDE Trust Zone (Opaque in Coarse Threat Models)"]
        direction LR
        GRD{{"Upstream Check<br/>«guard»"}}:::here
        TRN(["Resize / Decode / ASR<br/>«transform»"]):::here
        LLM(["Agent Model<br/>«follower»"]):::here
        RND(["Preview / Tool<br/>«renderer» · «executor»"]):::here
        GRD --> TRN --> LLM --> RND
    end

    OUT["System Sink / Egress<br/>[Sink Constraint]"]:::outer

    IN --> GRD
    RND --> OUT

    ATL["NIST AI 100-2 & MITRE ATLAS<br/>Adversary capabilities & entry tactics"]:::tag -. "labels entry" .-> IN
    MECH["This Paper: M = ⟨I, D, R⟩<br/>Exposes check-vs.-use & flow crossings"]:::heretag -. "derives inside zone" .-> TRN
    STR["STRIDE · OWASP · CoSAI SAIF<br/>Downstream hazard & governance risk"]:::tag -. "rates impact" .-> OUT

    classDef outer fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#0f172a
    classDef here fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
    classDef tag fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,color:#334155
    classDef heretag fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0f172a
```
*Figure 1. Ecosystem positioning across an agent pipeline. NIST AI 100-2 and MITRE ATLAS characterize adversary capabilities and entry tactics (left); STRIDE, OWASP, and CoSAI SAIF categorize downstream hazards and governance risks (right). Coarse threat models treat the inference pipeline inside the dashed trust zone as opaque; this paper annotates its internal guards, transforms, models, and renderers to derive where assumptions fail across modalities.*

While MITRE ATLAS (`AML.T0129`, `AML.T0068`), OWASP (`LLM01:2025`), and CoSAI's Risk Map already recognize multimodal prompt injection and payload obfuscation, none classifies attacks by the *violated pipeline invariant* or derives where preprocessing transforms, perceptual extractors, and active output renderers activate payloads across modalities. Section 6 situates the method in detail against governance frameworks, classical CWE/STPA precedents, and neighboring academic taxonomies (with full crosswalk tables in **Appendix C**).

### 1.4 Practitioner Workflows and Paper Roadmap

The vocabulary and DFD method support three concrete workflows demonstrated in Section 5:

1. **Design-time threat analysis (Use Case A, Section 5.1):** Walk an architecture's annotated DFD, then evaluate each added capability incrementally (an atomic classifier gains rendered user outputs, backend tools, multimodal inputs, and voice channels) without rebuilding the threat model. **Appendix D.1** has the complete 15-component enterprise derivation.
2. **Incident mechanism triage (Use Case C, Section 5.2):** Draw only the path traversed by a disclosed exploit (such as Trail of Bits / Gemini CLI) using vendor-neutral roles to separate attacker-supplied bypasses from architecture-granted steps and identify related exposures (`CVE-2025-54132`, `CVE-2025-32711`).
3. **Adversarial coverage planning and cross-modal prediction (Use Case B, Section 5.3):** Hold sink constraints fixed while swapping input channels across text, images, audio, video, and physical robotics sensors to generate targeted security tests where the violated sink constraint is the pass/fail oracle.

Section 2 defines the multimodal system model and inference-time perimeter scope. Section 3 (*Defining a Mechanism*) introduces `Invariant × Divergence × Representation` abstractly, and Section 4 specifies the four-step DFD derivation method. Section 5 applies the method across abridged progressive, incident, and robotics cases (with exhaustive breakdowns in **Appendix D**). Section 6 details ecosystem positioning, and Section 7 outlines empirical validation, limitations, and the CoSAI roadmap toward a per-mechanism control catalog and automated DFD assessment tool.


## Multimodal AI: Terminology and System Architectures

### 2.1 Core Terminology

A **modality** is a category of information represented or processed by an AI system, such as text, images, audio, or video [R1]. The following terms describe how AI systems handle information across modalities.

| Term | Definition |
|---|---|
| **Unimodal** | Involves a single modality at a specified input or processing boundary. |
| **Multimodal** | Involves two or more modalities whose information is processed or related together. |
| **Cross-modal** | Describes an operation or relationship between modalities, such as generating text from an image or retrieving images using text [R1]. |
| **Omnimodal** | A term used for models designed to support a broad range of modalities, often within an integrated architecture. It does not imply support for every possible modality. |
| **Modality-agnostic** | Describes an approach or framework designed to operate independently of any particular modality. |

These terms describe different characteristics of AI systems and are not necessarily mutually exclusive. Modality classification also depends on the system boundary being examined: a multimodal-capable model may receive only text in a particular invocation, while a single input artifact may contain multiple information streams.

### 2.2 Modalities and Input Representations

AI systems commonly process text, images, audio, and video, often through composite information sources such as documents, web pages, graphical user interfaces (GUIs), and tool responses.

| Information type | Examples |
|---|---|
| **Text** | Messages, documents, code, retrieved content |
| **Image** | Photographs, screenshots, scans, diagrams |
| **Audio** | Speech, music, environmental sounds |
| **Video** | Frames, motion, temporal sequences |
| **Structured data** | JSON, XML, CSV, database records, API responses |
| **Composite sources** | PDFs, web pages, GUIs, presentations, tool responses |

Structured data is generally an information representation rather than a distinct sensory modality. Similarly, composite sources may contain multiple modalities without necessarily being processed multimodally.

For example, a screenshot containing written instructions constitutes **image input**, even though its contents include readable text. An image accompanied by a separately supplied text question constitutes **multimodal input** when both are processed together. A video containing synchronized visual and audio streams likewise provides multiple modalities when both streams are used.

Input and output modalities should also be distinguished. Image captioning, for instance, is a cross-modal operation involving image input and text output, even when the initial input is unimodal [R1].

### 2.3 Multimodal Processing Architectures

Multimodal capabilities can be implemented through different system architectures. Two representative approaches are **unified** and **fragmented** processing.

| Architecture | Description | Representative example |
|---|---|---|
| **Unified** | A single multimodal model integrates the processing of multiple supported modalities. | OpenAI GPT-4o, which integrates text, visual, and audio processing within an end-to-end model [R2]. |
| **Fragmented** | Multiple specialized models or components process different modalities or stages, exchanging intermediate representations. | Earlier ChatGPT Voice Mode, which used separate speech recognition, language reasoning, and speech generation models [R2]. |

Unified architectures integrate multimodal processing within a model, whereas fragmented architectures distribute processing across specialized components. These are architectural patterns, not rigid implementation categories (even unified models may use modality-specific encoders or preprocessing components). The distinction is about how information is processed, which two systems supporting the same modalities can do very differently.

### 2.4 Agentic Architectures

An **AI agent** is a system that uses AI models to pursue goals and interact with an environment, potentially through tools, APIs, applications, or other agents. Agentic systems can perform multistep tasks involving reasoning, planning, tool invocation, and execution.

Agentic orchestration is distinct from modality-processing architecture. An agent may use a unified multimodal model, coordinate multiple specialized models, or combine both approaches. Commercial platforms such as Microsoft Copilot Studio and Salesforce Agentforce demonstrate agentic orchestration involving models, tools, and enterprise workflows [R4, R5].

Three representative configurations are:

| Configuration | Description |
|---|---|
| **Unified-model agent** | Uses a multimodal model as its primary reasoning component, potentially invoking external tools. |
| **Fragmented-model agent** | Coordinates specialized models or services, potentially handling different modalities. |
| **Multi-agent system** | Multiple agents collaborate, delegate tasks, or coordinate activities to accomplish broader objectives. |

These configurations may overlap. For example, a multi-agent system may coordinate agents built on unified multimodal models alongside agents using specialized processing pipelines.

### 2.5 Relationship Between Modalities and Architectures

Multimodal AI systems can be understood through three complementary perspectives:

1. **Modality:** What types of information does the system receive, process, or generate?
2. **Processing architecture:** Are these modalities handled through unified or fragmented processing?
3. **Agentic orchestration:** How does the system coordinate reasoning, tools, and actions?

These perspectives are related but distinct. A system may be multimodal without being agentic, while an agentic system may operate entirely on text. Similarly, unified and fragmented processing architectures can both support agentic behavior.

So the modalities a system supports do not determine how it behaves. Behavior also depends on how information moves between components and how models interact with tools and external environments. Adversarial content can enter through different modalities, go through different transformations, and pass through different components before it influences the model or triggers an action, and attacks on very different implementations can still exploit related security failures.


## 2. Scope and Terminology
This taxonomy encompasses inference-time security mechanisms involving **unimodal, multimodal, and cross-modal processing**. Inclusion is determined by whether the security-relevant mechanism can be characterized in terms of **Boundary, Representation, and System Processing Stage**, not by the number or type of modalities involved. Model capability is considered insofar as it affects these mechanisms, rather than as a separate taxonomy category. Coverage of particular attack families remains subject to evidence and evaluation maturity. The taxonomy is intended to accommodate **unified, modular, and hybrid AI agent architectures**, with architectural configuration recorded as supporting context rather than a primary classification dimension.

### 2.1 In Scope

* Adversarially constructed inputs presented at inference time, including text, image, audio, video, structured data, tool responses, and composite artifacts.  
* Adversarially constructed outputs, including covert exfiltration channels and outputs that become active when rendered or consumed downstream.  
* Prompt and control-flow injection, perception manipulation, filter bypass, transformation-dependent activation, parser differentials, adversarial examples, and resource amplification.  
* Agentic contexts where model-derived decisions influence tools, external communication, files, APIs, financial operations, or physical actions.  
* Data produced by adversarial means, even when the attack does not modify training data.

### 2.2 Anti-Scope (Deferred)

* Training-dataset poisoning, parameter backdoors, and model-weight compromise.  
* Long-term retrieval poisoning and persistent memory poisoning (deferred until the inference-time taxonomy is ratified).  
* Provenance spoofing, identity impersonation, and replay attacks as standalone families.  
* Side-channel and timing attacks where information leaks through observation of processing behavior (response latency, token-by-token streaming timing, resource consumption patterns) rather than through adversarial artifacts. These are well-studied in conventional security and do not require an artifact-centric taxonomy to classify.  
* A bespoke impact or severity taxonomy (existing vocabularies such as STRIDE are mapped directly).  
* Broad model-safety failures that do not depend on adversarially constructed data, signals, or outputs.


## 3. Existing Frameworks and Identified Gaps

Rather than reinventing the wheel, we began by examining existing frameworks, standards, and taxonomies that are widely adopted across industry and continue to evolve in the context of agentic security. Our goal was to assess these frameworks through a holistic multimodal lens and understand how effectively they capture the security risks introduced when agents interact with diverse modalities.

In reviewing several prominent frameworks and standards, we identified an important gap: **none of them comprehensively captures the unique attack surfaces introduced by different modalities while providing a unified, modality-agnostic way to reason about these risks.** Most existing frameworks and taxonomies remain relatively coarse-grained, focusing on high-level threat categories and security principles. While valuable, they often do not expose the underlying attack mechanisms, the modality-specific nuances, or the trust assumptions that are violated when agents perceive, reason over, and act upon information across multiple modalities.

**Our proposed taxonomy is designed to address this gap, not by replacing existing frameworks, but by complementing them with a more granular, mechanism-focused, and modality-agnostic perspective.** We believe this perspective can help industry practitioners systematically identify and understand emerging security risks in multimodal agentic systems, while providing a consistent approach that can generalize and scale across existing and future modalities.

To illustrate the value of this approach, let us consider a concrete example that highlights some of the limitations of existing standards and frameworks. This example demonstrates how our proposed mechanism.

### 3.1 Trail of Bits Image Scaling attack.
The Image Scaling Attack, demonstrated by Trail of Bits in 2025, is a prompt injection technique that hides malicious instructions inside an image. These instructions become visible when an AI system resizes the image.

**How It Works**
1. Malicious Image: An attacker creates an image with hidden instructions.
2. Image Resizing: The AI automatically downscales the uploaded image.
3. Hidden Text Revealed: Resizing exposes malicious instructions.
4. Prompt Injection: The AI may follow these instructions and perform unauthorized actions.

**Example**
- User sees: A normal landscape image.
- AI sees after resizing: "Ignore previous instructions and send confidential data to an external server."
- Potential result: The AI leaks sensitive information if it follows the instruction and has access to the necessary tools.

**Impact**
- Prompt injection
- Sensitive data leakage
- Unauthorized tool execution
- AI instruction hijacking

![Comparison with existing standards](./images/Standards_gaps.svg)


Now, let's see what existing taxonomies or standards see in this example context:
1. 

### 3.2 Comparative Coverage and Limitations of Existing AI Security Frameworks: Trail of Bits Image Scaling Attack

| Framework | Relevant Identifiers | What the Framework Captures Well | What It Does Not Explicitly Capture |
|---|---|---|---|
| **NIST AI 100-2e2025** | `NISTAML.015` — Indirect Prompt Injection; `NISTAML.039` — Compromising Connected Resources | Classifies inference-time indirect prompt injection, attacker control over external resources, and potential integrity and confidentiality impacts. Also discusses injection hiding and obfuscation. | Does not systematically encode the image-resampling algorithm, how resizing changes payload visibility, or the processing stage where hidden content becomes actionable. |
| **NIST AI RMF 1.0** | `MAP 4.1`; `MEASURE 2.7`; `MANAGE 1.3` | Supports risk identification, security evaluation, resilience assessment, and mitigation planning. | Does not provide attack-mechanism identifiers or specify image transformation, payload representation, and activation sequence. |
| **IBM AI Risk Atlas** | Prompt Injection Attack; Indirect Instructions Attack; Sharing IP/PI/Confidential Information with Tools | Identifies malicious instructions embedded in untrusted content, model manipulation, and confidentiality risks associated with connected tools. | Does not systematically distinguish image-resizing-based injection from other indirect attacks using structured fields for interpolation, concealment, and transformation-dependent activation. |
| **MITRE ATLAS** | `AML.T0051.001` — Indirect Prompt Injection; `AML.T0068` — LLM Prompt Obfuscation; `AML.T0129` — Triggers in Multimodal Inputs (related) | Describes attacker techniques, untrusted multimodal content, payload concealment, and adversarial behavior. Recognizes hidden instructions in image pixels and multimodal triggers. | Does not require a structured description of the exact resampling primitive, differences between original and transformed representations, or the activation stage. |
| **MITRE D3FEND** | `D3-FCOA` — File Content Analysis; `D3-FCR` — File Content Rules; `D3-OTF` — Outbound Traffic Filtering | Provides candidate defensive techniques for inspecting files, applying content-analysis rules, and restricting unauthorized data transmission. | Does not classify the offensive image-scaling mechanism or explicitly describe detection of instructions revealed by resizing. The listed controls are candidate defenses, not a verified attack-specific mapping. |
| **MAESTRO** | `L2` — Data Operations; `L1` — Foundation Model; `L3` — Agent Frameworks; `L7` — Agent Ecosystem; related ASI threats `T2`, `T6` | Identifies affected architectural layers, cross-layer attack propagation, trust boundaries, and potential misuse of connected tools. | Does not systematically represent pixel-level manipulation, the exact resampling algorithm, pre-/post-transformation semantic differences, or the precise activation condition. |
| **STRIDE** | `T` — Tampering; `I` — Information Disclosure; `E` — Elevation of Privilege (conditional) | Classifies security threats involving input manipulation, confidential data exposure, and potential authorization-boundary violations. | Does not distinguish image-scaling attacks from other attacks with the same security consequences or specify payload representation, transformation, and activation mechanisms. |


The comparative analysis demonstrates that existing AI security frameworks provide valuable but complementary perspectives on the Trail of Bits image-scaling attack. NIST and IBM AI Risk Atlas identify adversarial techniques and associated risks; MITRE ATLAS captures attacker behavior and prompt injection techniques; MITRE D3FEND provides defensive countermeasures; MAESTRO examines architectural exposure and trust boundaries; and STRIDE classifies potential security consequences.

However, these frameworks do not consistently provide a structured, mechanism-level representation of **how an attack is constructed, transformed, activated, and propagated through an AI system**. In the Trail of Bits example, the critical mechanism involves pixel-level manipulation followed by image downscaling, which reveals previously concealed instructions that may subsequently influence model behavior and agent actions. Although existing frameworks recognize prompt injection, obfuscation, and multimodal threats, they do not uniformly capture the relationship between these processing transformations and the resulting security boundary violations.

This gap motivates the proposed taxonomy, which introduces complementary dimensions for **payload representation, transformation mechanisms, security boundaries, and system processing stages**. Rather than replacing established frameworks, the proposed approach aims to extend their descriptive capabilities by enabling more precise characterization and comparison of attack mechanisms across different modalities.

By explicitly representing how adversarial content becomes effective within an AI processing pipeline, the taxonomy has the potential to support more systematic attack analysis, identification of vulnerable processing stages, and selection of targeted defensive controls. 

Its incremental value over existing frameworks remains to be validated through broader attack coverage and reproducible classification studies.


## 4. Proposed Modality-Independent Taxonomy

Traditional threat modeling identifies trust boundaries between users, processes, services, and networks. Multimodal AI introduces additional semantic and representational boundaries where the same artifact can acquire a different meaning, authority, or computational effect across humans, guards, models, transformations, and downstream consumers. The mechanism taxonomy is intended to make these AI-specific perimeter gaps explicit.

| Dimension | Question Answered | Specificity |
| :---- | :---- | :---- |
| Boundary | What security-relevant discontinuity, trust assumption, or semantic interface makes the attack possible? | Most general |
| Representation | How is adversarial influence or computational burden embodied in the artifact or signal? | More specific |
| System Processing Stage | Where does attacker-controlled information enter the target system or become security-relevant? | Most operational |


```mermaid
%%{init: {"flowchart": {"wrappingWidth": 260}}}%%
flowchart LR
    B("<b>BOUNDARY</b><br/><br/>What security-relevant<br/>discontinuity is crossed?")
    R("<b>REPRESENTATION</b><br/><br/>How is adversarial<br/>influence embodied?")
    S("<b>SYSTEM PROCESSING STAGE</b><br/><br/>Where does it enter or<br/>become effective?")
    B --> R --> S
```

*Figure 1\. Core mechanism taxonomy tuple M \= \<Boundary, Representation, System Processing Stage\>.*


### 4.1 Naming Conventions & Resolving Collisions

Because the three dimensions describe the same attack from different angles, a single root word (such as "Transformation") could appear in all three slots. To eliminate ambiguity, each slot strictly follows its generating question:

* **Boundary names** denote the invariant assumed: *Transform Consistency*, *Check-Use Consistency*, *Authorization Stability*, *Grant Persistence*, *Data-Control*.  
* **Representation names** denote how influence is embodied: *Transform-Activated*, *Sequence-Dependent*, *Fragmented / Distributed*, *Resource-Amplifying*.  
* **Construction names** denote how the payload was produced: *Manual*, *Black-box Search*, *White-box Optimization*, *Surrogate Transfer*.  
* **System Processing Stage names** denote a pipeline location: *Ingestion*, *Transformation*, *Perception / Decoding*, *Interpretation / Decision*, *Generation*, *Action*, *Consumption*, *Feedback*.

*Deliberate exception:* **Parser / Interpreter Differential** retains "Differential" because parser differential is established security terminology that maps one-to-one onto existing usage.

### 4.2 Taxonomy Diagram


![Taxonomy Diagram](./images/taxonomy_diagram.svg)


## 5. Taxonomy Dimensions and Classification Rules

### 5.1 Boundary Classes

A security boundary represents a security-relevant assumption or constraint that must remain valid as information is evaluated, transformed, transferred, or acted upon within an AI system.

Building on established cybersecurity concepts such as interpretation consistency (CWE-436), authorization enforcement (NIST SP 800-53 AC-3), and resource bounding (CWE-400), the proposed taxonomy organizes security boundaries into three families: **Meaning, Authority, and Cost**.

These families describe the security property being protected, independently of the modality carrying the adversarial artifact.

#### 5.1.1 Security Boundary Invariants

A boundary violation occurs when an adversarial artifact causes the system to violate an applicable security assumption or constraint. A difference in interpretation, processing behavior, or resource usage is not enough on its own; there has to be a security-relevant failure.

The taxonomy distinguishes three families of security invariants:

- **Meaning (Semantic Integrity):** Security-relevant interpretations must remain consistent across evaluators, representations, or transformations wherever the system relies on that consistency.
- **Authority (Authorization Scope):** Lower-trust information must not acquire unauthorized instruction authority, and system actions must remain within the permissions granted by the applicable authorization policy.
- **Cost (Resource Bounding):** Processing, inference, and tool execution must remain within established resource limits.

**Example: Image-Scaling Prompt Injection**

In the Trail of Bits image-scaling attack, an adversarial image appears benign during initial inspection but reveals malicious instructions after resizing.

- **Meaning:** The transformed image exposes security-relevant content that an earlier inspection did not identify, potentially invalidating that assessment.
- **Authority:** If the agent treats the revealed instructions as authoritative, a Data-Control boundary is violated. If an unauthorized tool operation is subsequently executed, an additional authorization failure may occur.
- **Cost:** The attack does not inherently violate a resource boundary, since excessive resource consumption is not part of the demonstrated mechanism.

Not every difference in interpretation or transformation constitutes a security failure. A boundary violation requires an identifiable security assumption or constraint to be violated.

**Example: Resource Exhaustion Through Media Decompression**

An attacker submits a highly compressed image or media file that appears small at ingestion but expands into a disproportionately large amount of data during decoding.

- **Cost:** Decoding the artifact consumes excessive memory or processing resources, exceeding the system's configured resource limits and potentially causing denial of service.
- **Meaning:** No semantic inconsistency is required for the attack.
- **Authority:** No unauthorized instruction or permission escalation is required.


#### 5.1.2 Boundary Families and Subclasses

Boundary subclasses identify specific security assumptions that may be violated during AI system processing. Each subclass describes a security-relevant failure, independent of attack technique or modality.

Subclasses may overlap within an attack chain, so classify by the specific security assumption violated. A processing step is not a separate failure just because it is a separate step.

##### Meaning (Semantic Integrity)

Meaning boundaries concern security-relevant inconsistencies across evaluators, transformations, interpretations, or processing contexts. These boundaries build upon established security concepts such as interpretation consistency, canonicalization, and adversarial robustness.

| Subclass | Definition | Example | Related Security Concept |
|---|---|---|---|
| **Human-Machine Perception** | A difference between human and machine interpretation of the same artifact that invalidates a security assumption based on human perception. | A human reviewer sees a benign image, while an AI model detects embedded malicious instructions that undermine the reviewer's security assessment. | Human-machine perception mismatch |
| **Guard-Model Capability** | A protective evaluator fails to identify security-relevant content or behavior that the target model can recognize or act upon, despite evaluating equivalent security-relevant input. | A security guard and target multimodal model examine equivalent image content, but only the target model recognizes embedded malicious instructions. | Security evaluator and target-model capability mismatch |
| **Parser / Interpreter Differential** | Different parsers or interpreters produce inconsistent security-relevant interpretations of the same input, undermining security validation or enforcement. | A validation parser accepts structured content that a downstream interpreter processes as an executable instruction. | CWE-436: Interpretation Conflict |
| **Transform Consistency** | A transformation changes or exposes security-relevant content, invalidating an earlier security assessment on which the system relies. | An image passes initial security inspection, but subsequent downscaling reveals previously concealed malicious instructions. | CWE-180: Validate Before Canonicalize; CWE-436: Interpretation Conflict |
| **Semantic Stability** | Different input instances with equivalent security-relevant meaning receive inconsistent security decisions under the same security policy. | Two images contain the same malicious instruction but use different fonts or backgrounds. The guard blocks one image but allows the other. | NIST AI 100-2: Adversarial Evasion and Robustness |
| **Check-Use Consistency** | A security property established during validation no longer holds at the point of use because the artifact's security-relevant content, interpretation, or validated state has changed. | An agent validates a document, but the document is replaced with one containing malicious instructions before the agent processes it. The agent relies on the earlier assessment. | CWE-367: Time-of-check Time-of-use (related) |

**Classification Distinctions**

- **Human-Machine Perception vs. Guard-Model Capability:** The former concerns a security assumption based on human perception; the latter concerns a capability mismatch between a protective evaluator and the target model.
- **Guard-Model Capability vs. Transform Consistency:** Guard-Model Capability concerns differences in what evaluators can recognize from equivalent security-relevant input. Transform Consistency concerns changes introduced or exposed by processing transformations.
- **Parser / Interpreter Differential vs. Transform Consistency:** The former concerns inconsistent interpretation by different parsers or interpreters; the latter concerns security-relevant changes across transformations of an artifact.
- **Transform Consistency vs. Semantic Stability:** The former concerns the same artifact across processing states; the latter concerns different input instances with equivalent security-relevant meaning that receive inconsistent security decisions.
- **Transform Consistency vs. Check-Use Consistency:** The former identifies a transformation-related inconsistency; the latter identifies reliance on a security assessment that is no longer valid when the artifact is used.

**Relationship to Existing Standards**

These subclasses reuse established security concepts. CWE-180 covers validation before canonicalization, CWE-436 covers interpretation conflicts, and CWE-367 covers time-of-check/time-of-use weaknesses. NIST AI 100-2 has related concepts for adversarial evasion and robustness. The mappings are conceptual (not exact equivalences); what the taxonomy adds is organizing these concerns around how multimodal and agentic AI systems evaluate and process inputs.

**Meaning Classification Principle**

A Meaning boundary violation requires a security-relevant inconsistency that invalidates an identifiable security assumption. Differences in perception, model outputs, or representations alone do not constitute security violations.

Each subclass should be assigned only when its specific failure condition is supported by the system architecture and available evidence. When multiple labels appear applicable, independently identifiable failures should be distinguished from different descriptions of the same failure.

##### Authority (Authorization Scope)

Authority boundaries govern how instructions, permissions, decisions, and outputs acquire, transfer, retain, or exercise authority within AI systems. These boundaries build upon established security principles including least privilege, access control, delegation, and secure execution.

| Subclass | Definition | Example | Related Security Concept |
|---|---|---|---|
| **Delegation Authority** | A delegated agent or component exercises authority beyond the permissions or constraints explicitly granted by the delegating principal. | A subagent authorized only to retrieve financial records initiates a financial transaction. | Least Privilege; NIST SP 800-53 AC-6 |
| **Authorization Stability** | An unchanged authorization policy is enforced inconsistently across equivalent execution contexts or input instances. | An agent correctly denies a restricted API operation in one context but permits the same operation in another despite identical permissions and applicable policy. | CWE-863: Incorrect Authorization |
| **Grant Persistence** | A permission or delegated grant remains usable after its authorized expiration, revocation, or termination. | An agent continues invoking a tool using a revoked access grant. | Authorization lifecycle; revocation enforcement |
| **Data-Control** | Lower-trust content is improperly promoted into authoritative instructions or control flow, contrary to the system's instruction hierarchy or trust policy. | An agent treats malicious instructions embedded in an attacker-controlled image as if they were commands from the authenticated user. | OWASP LLM01: Prompt Injection |
| **Decision-Action** | A model-generated decision is executed without satisfying the authorization requirements applicable to the resulting operation. | An agent issues a tool call to transfer funds, and the executor performs the transfer without enforcing the required transaction authorization. | NIST SP 800-53 AC-3; OWASP LLM06: Excessive Agency |
| **Output-Consumer** | A generated output crosses into a downstream execution or consumption context and produces effects prohibited by that consumer's security policy. | A generated diagram includes an external image reference that causes confidential data to be transmitted when the diagram is rendered. | OWASP LLM05: Improper Output Handling |

**Classification Distinctions**

- **Delegation Authority vs. Authorization Stability:** Delegation Authority concerns exceeding the permissions granted to a delegated component, whereas Authorization Stability concerns inconsistent enforcement of the same applicable authorization policy across equivalent contexts.
- **Authorization Stability vs. Grant Persistence:** Authorization Stability concerns inconsistent authorization decisions across contexts; Grant Persistence concerns authority remaining usable after its permitted lifetime.
- **Data-Control vs. Decision-Action:** Data-Control concerns improper promotion of untrusted content into instruction authority. Decision-Action concerns failure to enforce authorization when executing a resulting operation.
- **Data-Control vs. Output-Consumer:** Data-Control concerns untrusted information influencing model instructions or decisions. Output-Consumer concerns unauthorized effects arising when generated artifacts are processed downstream.
- **Delegation Authority vs. Decision-Action:** Delegation Authority concerns the scope of authority passed to another component. Decision-Action concerns enforcement of authorization for a particular executed operation.

**Relationship to Existing Standards**

These subclasses extend established access-control and secure-processing concepts to agentic AI systems. NIST SP 800-53 provides access-enforcement and least-privilege principles, CWE-863 covers incorrect authorization, and OWASP lists related risks for prompt injection, excessive agency, and improper output handling. As above, the mappings are conceptual. The taxonomy separates where authority is acquired, delegated, retained, or exercised, so unauthorized agent behavior can be split into distinct failures.

**Authority Classification Principle**

An Authority boundary violation requires an identifiable breach of instruction trust, permission scope, authorization policy, or downstream execution constraints.

A manipulated model decision, tool invocation, or generated output does not automatically constitute an independent Authority violation. Each subclass should be assigned only when its corresponding security assumption is violated or explicitly identified as a potential failure under a stated threat model.

In particular, Authorization Stability requires evidence of inconsistent enforcement under equivalent authorization conditions. A legitimate change in policy, permissions, or execution context does not by itself constitute a violation.

##### Cost (Resource Bounding)

Cost boundaries concern whether adversarial inputs or induced operations cause system resource consumption to violate established operational constraints.

| Subclass | Definition | Example | Related Security Concept |
|---|---|---|---|
| **Resource Accounting** | An adversarial artifact or induced operation causes resource consumption to exceed applicable processing or execution limits or violate an availability requirement. | A compressed media file triggers excessive memory consumption during decoding, or an agent enters uncontrolled recursive tool execution. | CWE-400: Uncontrolled Resource Consumption |

Resource Accounting covers computational resources, memory, storage, inference budgets, and tool-execution costs.

Resource Accounting stays a single subclass because the other two dimensions already capture how a resource violation arises. Specific mechanisms such as media decompression or recursive tool execution are recorded through Representation and Processing Stage, so they do not need their own Cost boundaries.

A resource-intensive operation does not automatically constitute a security violation. A Cost boundary violation requires an applicable resource constraint or availability requirement to be breached.

##### Boundary Classification Principle

A boundary subclass should be assigned only when its corresponding security assumption is violated or when a potential violation is explicitly identified under a stated threat model.

A single attack may involve multiple boundary failures, but each classification should be a distinct security-relevant failure. Another processing step or downstream consequence does not count as one.

For example, image-scaling prompt injection may involve:

- **Transform Consistency:** Resizing exposes instructions missed by an earlier security assessment on which the system relies.
- **Data-Control:** The agent treats untrusted image instructions as authoritative.
- **Decision-Action (conditional):** A resulting tool operation is executed without satisfying an applicable authorization requirement.

Additional subclasses, such as Guard-Model Capability or Check-Use Consistency, should be assigned only when supported by the system architecture and available evidence.

### 5.2 Representation

Representation describes how adversarial information or influence is embodied in an artifact and becomes interpretable at a specified processing boundary. It describes properties of the artifact; how the attacker built it is recorded separately (Section 5.4.1).

Representation is classified according to the information or processing capabilities required to recover the adversarial content or effect. Because an artifact may change during processing, classifications are specific to the artifact state being examined.

The proposed categories build upon established security concepts, including encoding, obfuscation, steganography, and adversarial evasion. This dimension provides a common vocabulary for characterizing adversarial representations across modalities and AI processing architectures.

#### 5.2.1 Representation Forms

| Form | Definition | Documented Example | Related Security Concept |
|---|---|---|---|
| **Overt Semantic** | Adversarial content is accessible through ordinary interpretation of the artifact at the specified observation point, without specialized decoding or target-specific processing. | Palo Alto Networks Unit 42 documented plaintext prompt-injection attempts embedded in webpages targeting AI agents [1]. | MITRE ATLAS: Prompt Injection (related) |
| **Encoded / Obfuscated** | Adversarial content is concealed or made less recognizable through encoding, symbolic substitution, or obfuscation recoverable using known or discoverable conventions. | Unit 42 documented webpage prompt-injection attempts using Base64, URL encoding, HTML entities, and nested encoding [1]. | MITRE ATT&CK T1027: Obfuscated Files or Information |
| **Steganographic** | Adversarial information is concealed within a carrier whose apparent content does not reveal the embedded information through ordinary interpretation. | *Invisible Injections* (2025) reported experiments embedding malicious instructions within images using steganographic techniques to influence vision-language models [2]. | MITRE ATT&CK T1027.003: Steganography |
| **Processing-Dependent** | The adversarial content or effect depends on a specific target model, transformation, or processing pathway and cannot be reliably recovered through ordinary interpretation or general-purpose decoding alone. | Trail of Bits demonstrated image-scaling attacks in which instructions became readable after targeted downscaling, including a proof of concept involving Gemini CLI and connected tools [3]. | NIST AI 100-2: Adversarial Examples and Evasion (related) |

A manually constructed payload and an adversarially optimized one may share the same representation classification.

Representation forms are not necessarily mutually exclusive. For example, a concealed image payload may be both Steganographic and Processing-Dependent when the embedded information requires a specific processing pathway to become effective.

#### 5.2.2 Representation Modifiers

Representation modifiers describe additional conditions required for adversarial information or effects to become effective. A modifier is added on top of a representation form.

| Modifier | Definition | Documented Example | Related Security Concept |
|---|---|---|---|
| **Transformation-Activated** | Adversarial information or influence becomes effective only after a particular transformation, normalization, or decoding operation. | Trail of Bits demonstrated that targeted image downscaling can reveal concealed malicious instructions [3]. | CWE-180: Validate Before Canonicalize (related) |
| **Fragmented / Distributed** | A single effective payload is distributed across multiple fragments that require aggregation or reconstruction to recover its adversarial effect. | *Hiding in Plain Floats* (2026) investigated prompt-injection payloads concealed in structured floating-point data and reconstructed through downstream processing [4]. | Payload fragmentation and obfuscation (related) |
| **Sequence-Dependent** | The adversarial effect depends on the timing, ordering, duration, or synchronization of information. | A 2026 study of prompt injection in surgical decision-support systems examined how the temporal placement and duration of visual instructions affected vision-language model behavior [5]. | Temporal adversarial attacks and sequence manipulation |
| **Composition-Dependent** | The adversarial effect emerges through joint interpretation of multiple artifacts that contribute distinct information rather than fragments of a single payload. | NVIDIA's *When Modalities Combine* (2026) reported a three-modal prompt-injection attack requiring the joint processing of text, image, and audio [6]. | Multimodal adversarial interaction and input fusion |

**Classification Distinctions**

- **Processing-Dependent vs. Transformation-Activated:** Processing-Dependent describes reliance on a target-specific processing pathway, whereas Transformation-Activated identifies a transformation required to activate the adversarial effect.
- **Fragmented / Distributed vs. Composition-Dependent:** Fragmented / Distributed concerns reconstructing a payload from multiple pieces. Composition-Dependent concerns distinct artifacts whose joint interpretation produces the effect.
- **Fragmented / Distributed vs. Sequence-Dependent:** Fragmentation concerns distribution across pieces, while sequence dependence concerns whether ordering or timing is essential.
- **Encoded / Obfuscated vs. Steganographic:** Encoded / Obfuscated content relies on encoding or obfuscation conventions, whereas Steganographic content is concealed within a carrier whose apparent purpose does not disclose the embedded information.

#### 5.2.3 Resource-Amplification Characteristics

Some adversarial artifacts cause security failures mainly by consuming disproportionate resources, with no instruction manipulation or semantic inconsistency involved. There are two ways this happens:

- **Intrinsic Amplification:** The artifact's structure or encoding causes disproportionate resource consumption during processing, independently of its semantic content. Examples include decompression bombs and pathological media bitstreams.
- **Semantic Amplification:** The interpreted content of an artifact induces disproportionate resource consumption through system behavior. Examples include recursive agent delegation, repeated tool invocation, and uncontrolled retry loops.

These characteristics are descriptive; they are not additional Representation Forms or Modifiers. When resource consumption violates an applicable operational constraint or availability requirement, the security failure is classified under the **Resource Accounting** boundary within Cost (Section 5.1.2).

The split matters for controls. Intrinsic Amplification may need limits on decoding, decompression, or processing complexity, while Semantic Amplification may need execution budgets, bounded delegation, or tool-call limits.

#### 5.2.4 Representation Classification Principles

Representation classification follows five principles:

1. **Artifact-State Specificity:** Classify the representation at a specified observation or processing point. Classification may change when the artifact is transformed.
2. **Multiple Applicable Forms:** More than one representation form may apply when an artifact satisfies multiple definitions. The primary form should reflect the characteristic most relevant to the security mechanism.
3. **Complementary Modifiers:** Assign modifiers only when their corresponding transformation, distribution, sequencing, or composition condition contributes to the adversarial effect.
4. **Construction Independence:** Representation classification does not depend on whether the payload was manually created, discovered through black-box search, or generated through white-box optimization. Construction method is recorded separately in Section 5.4.1.
5. **Evidence-Based Classification:** Assign forms and modifiers only when supported by the attack description, system architecture, or available evidence.

The examples presented in this section are drawn from publicly reported attacks and security research. Their inclusion does not imply that all were observed in production environments.

**Example: Image-Scaling Prompt Injection**

In the Trail of Bits image-scaling attack, an adversarial image appears benign at its original resolution but reveals malicious instructions after targeted resizing [3].

| Artifact State | Representation | Modifier |
|---|---|---|
| Original image before resizing | Processing-Dependent; potentially Steganographic if the concealment criteria are met | Transformation-Activated |
| Image after targeted resizing | Overt Semantic, when instructions become readable | Transformation-Activated describes the preceding activation condition |
| Extracted instructions interpreted by the model | Overt Semantic | No additional modifier required unless another activation condition applies |

The representation classification changes twice here, even though it is the same artifact in the same attack chain. Note also that Processing-Dependent and Transformation-Activated describe how the adversarial payload becomes effective, whereas Transform Consistency and Data-Control describe the security assumptions potentially violated.

#### 5.2.5 Relationship to Existing Security Standards

MITRE ATT&CK provides terminology for obfuscation and steganography, and NIST AI 100-2 discusses adversarial examples and evasion. CWE-180 (validation before canonicalization) is the closest existing concept to transformation-dependent activation.

Those frameworks mostly describe adversary techniques, weaknesses, or threat characteristics. The Representation dimension instead describes how adversarial information is embodied, recovered, or activated inside an AI processing pipeline, using the same terms for text, images, audio, video, structured data, and agentic architectures. The mappings are conceptual.


### 5.4 Supporting Annotations

Supporting annotations capture additional information about payload construction, attacker knowledge, and transferability alongside the core mechanism tuple.

These annotations are optional and should be recorded only when supported by the available evidence. They improve threat characterization and deployment-specific analysis without changing the underlying mechanism classification.

#### 5.4.1 Construction Method

Construction Method describes how an adversarial artifact was created or refined, what knowledge or access was available during its development, and whether it was developed against the intended deployment target.

It is recorded independently of Representation because an artifact's observable characteristics do not uniquely determine how it was constructed. Although certain representations may favor particular construction techniques or attacker capabilities, construction history does not define the Representation category.

Three complementary fields are used.

**A. Construction Technique**

| Technique | Definition | Documented Example | Related Security Concept |
|---|---|---|---|
| **Manual Construction** | An attacker directly creates or modifies a payload without automated optimization or systematic algorithmic search. | Greshake et al. (2023) demonstrated indirect prompt injections using attacker-crafted instructions placed in external content retrieved by LLM-integrated applications [1]. | MITRE ATLAS AML.T0043.003: Manual Modification (related) |
| **Adaptive Search** | Candidate payloads are iteratively generated, evaluated, and refined using observed responses or feedback from a target or evaluation system. | Chao et al. (2023) introduced Prompt Automatic Iterative Refinement (PAIR), which uses an attacker LLM to iteratively generate jailbreak candidates based on responses from a black-box target model [2]. | MITRE ATLAS AML.T0043.001: Black-Box Optimization (related) |
| **Optimization** | An explicit mathematical or algorithmic optimization procedure constructs or refines a payload using a defined objective and available model or pipeline information. | Zou et al. (2023) introduced Greedy Coordinate Gradient (GCG) for adversarial suffix optimization [3]. Trail of Bits (2025) also demonstrated least-squares pixel optimization against image-resizing algorithms [4]. | MITRE ATLAS AML.T0043.000: White-Box Optimization (related) |

These techniques are not mutually exclusive. A payload may be manually initialized, optimized, and subsequently refined through adaptive testing.

In this taxonomy, Adaptive Search emphasizes iterative evaluation and feedback, while Optimization emphasizes an explicit objective and optimization procedure. An attack may satisfy both descriptions.

**B. Attacker Knowledge / Access**

Attacker Knowledge / Access records what information or interaction capabilities were available during payload development.

| Knowledge / Access | Definition | Documented Example |
|---|---|---|
| **Black-box** | The attacker can submit inputs and observe outputs but does not have access to the target's relevant internal parameters or implementation. | PAIR demonstrated iterative jailbreak generation using black-box access to target language models [2]. |
| **Partial Knowledge** | The attacker knows or can infer some implementation details, such as processing algorithms or component configurations, without complete access to the target system. | Trail of Bits demonstrated fingerprinting of image-resizing algorithms and implementations to construct compatible payloads without requiring access to downstream model weights [4]. |
| **White-box** | The attacker has access to internal information relevant to the attack, such as model parameters, gradients, processing algorithms, or implementations. | GCG used gradient information from accessible language models to construct adversarial suffixes [3]. |
| **Unknown** | Available evidence does not establish the attacker's knowledge or access. | Recorded when a published attack description does not disclose the relevant information. |

Knowledge and access should be evaluated relative to the specific target component. Full knowledge of an image transformation algorithm does not imply white-box access to the downstream multimodal model.

The Black-box, Partial Knowledge, and White-box categories correspond conceptually to attacker-knowledge distinctions in NIST AI 100-2. They are not intended to exhaustively represent every attacker capability, such as control over training data, retrieved resources, or tools.

**C. Transfer Context**

Transfer Context records whether the payload was developed against the intended deployment target or another model or processing pipeline.

| Context | Definition | Documented Example | Related Security Concept |
|---|---|---|---|
| **Direct-Target Development** | Payload development or refinement uses the intended deployment target. | PAIR demonstrated iterative attacks that query and refine candidates against a target language model [2]. | Direct target querying and attack verification (related) |
| **Surrogate Transfer** | A payload is developed against a surrogate model or processing pipeline and subsequently applied to a different target. | Zou et al. (2023) optimized adversarial suffixes using accessible Vicuna models and demonstrated transfer to other language models, including closed-source systems [3]. | MITRE ATLAS AML.T0043.002: Black-Box Transfer (related) |
| **Unknown** | Available evidence does not establish whether development and deployment targets differed. | Used when the development environment is not disclosed. | Not applicable |

Transfer Context is distinct from Construction Technique. A payload may be optimized with white-box access to a surrogate model and subsequently transferred to a black-box deployment target.

The three construction fields may therefore be combined without changing the core mechanism classification.

**Example: GCG Adversarial Suffixes**

The attack introduced by Zou et al. [3] can be characterized as follows:

| Annotation Field | Classification |
|---|---|
| Construction Technique | Optimization; Adaptive Search |
| Attacker Knowledge / Access | White-box for the source models; black-box for the tested closed-source targets |
| Transfer Context | Surrogate Transfer |

The distinction between source-model access and deployment-target access is important: an attack can use white-box optimization during development while requiring only black-box interaction with the eventual target.

#### 5.4.3 Relationship to Existing Security Standards

Supporting annotations complement established adversarial machine-learning and cybersecurity frameworks, particularly those addressing attacker capabilities and attack construction.

| Framework | Relevant Concepts | Relationship to Supporting Annotations |
|---|---|---|
| **NIST AI 100-2e2025** | Attacker knowledge, capabilities, objectives, and attack lifecycle. | Provides established concepts for describing attacker access and threat conditions. Construction Method records narrower information about payload development, access, and transfer. |
| **MITRE ATLAS** | Adversarial tactics and techniques, including crafting adversarial data through manual modification, black-box optimization, white-box optimization, and black-box transfer. | Provides directly related technique terminology for Construction Method. The taxonomy splits these characteristics into separate, combinable descriptive fields. |
| **OWASP Top 10 for LLM Applications (2025)** | Risks such as Prompt Injection (LLM01) and Excessive Agency (LLM06). | Provides application-security context for architectural interfaces where untrusted content may influence model decisions or connected tools. |

The mappings are conceptual. When evidence is incomplete, mark fields Unknown or leave them unassigned, and record construction history, attacker access, and internal architecture from direct evidence about each.


## 4. Architectural Analysis Method

Application-security architects already model systems with standard data-flow diagrams (DFDs) composed of external entities, processes, data stores, and data flows (Shostack, 2014). This method keeps the standard DFD and adds three lightweight annotations: per-sink security constraints, component functional roles, and flow trust labels and representational fidelities (**Table 3**). Once a diagram is annotated, candidate boundary crossings, mechanism records (`M = ⟨Invariant, Divergence, Representation⟩`), multi-step attack chains, minimal structural cut points, and falsifiable security tests follow from graph traversal rules. That leaves one documented judgment per crossing: can an attacker realize it in practice?

The method combines three established foundations: top-down loss-to-constraint analysis from STPA-Sec (Young & Leveson, 2013; `arXiv:2006.02930`), source-to-sink taint and information-flow lattices (Denning, 1976; FIDES, `arXiv:2505.23643`; CaMeL, Debenedetti et al., 2025) paired with attack-graph minimum cuts (Phillips & Swiler, 1998; Sheyner et al., 2002; Ou et al., 2005), and the distinction between safety (*nothing unauthorized happens*) and liveness (*a required intervention occurs within its operational bound*) (Lamport, 1977; Alpern & Schneider, 1985).

| Layer & Attached Element | Annotation Values & DFD Notation | Operational Meaning | Multimodal & Agentic Examples |
| :---- | :---- | :---- | :---- |
| **Step 1: Sink Constraints**<br/>*(attached to authority, egress, susceptible, and safeguard sinks)* | **Flow clearance** | Allowed trust/sensitivity labels (`label ⊑ clearance`) and permitted data types at an authority or egress sink; violations break **Flow (integrity)** or **Flow (confidentiality)**. | Supplier content may populate typed invoice fields only; internal records may reach only the ERP system and finance channel. |
| | **Reference specification** | Ground-truth reference that acted-on values at an authority sink must match; violations break **Meaning**. | Executed payee and amount must match the invoice as read by a human reviewer; a text claim must agree with an independent visual or ledger observation. |
| | **Resource budget** | Maximum operational expenditure per admitted unit at a susceptible process; violations break **Cost**. | At most 50 pages, 60 seconds, `\$0.50` in model spend, and 5 tool calls per invoice; at most 4,000 characters and 5 seconds per support ticket. |
| | **Safeguard obligation** | Mandatory intervention and explicit timing or scope bound (a liveness requirement) on a `guard` or alert sink; omissions breach **Meaning**, **Flow (integrity)**, or **Cost**. | Every payable over `\$10,000` must reach human review before settlement; every abuse or threat ticket must page on-call responders within 1 hour. |
| **Step 2: Node Shapes & Functional Roles**<br/>*(attached to external entities, stores, and processes)* | **`source`** · Rectangle `[ ]` | External entity supplying potentially attacker-controlled inputs. | Email sender, fetched web page, uploaded screenshot, telephony caller, physical camera scene. |
| | **`receiver`** · Rectangle `[ ]` | External entity receiving outbound messages, network fetches, or physical side effects. | Customer email recipient, external webhook host, physical brake or steering actuator. |
| | **Data store** · Cylinder `[( )]` | Persists state read or mutated across execution steps. | CRM database, vendor reference record, calendar store, internal ticket header. |
| | **`guard`** · Hexagon `{{ }}` | Process that evaluates content and gates downstream flow or triggers a required alert. | Text prompt filter, human approver, deterministic threshold gate, on-call abuse pager. |
| | **`transform`** · Rounded `([ ])` | Process that deterministically or algorithmically converts an input artifact into a new form. | Image resizer, HTML/Unicode normalizer, audio resampler, container splitter, OCR or ASR extractor. |
| | **`follower`** · Rounded `([ ])` | Instruction-following or model-driven process whose output selection can be steered by input semantics. | Agent orchestrator, triage classifier, field extractor, summarizer, VLM planner. |
| | **`executor`** · Rounded `([ ])` | Process that deterministically executes structured arguments, commands, or queries under system authority. | Queue router, payment API connector, MCP tool runner, SQL or shell executor. |
| | **`renderer`** · Rounded `([ ])` | Process that evaluates active output markup or fetches external references in a client or UI. | Staff HTML previewer, Markdown/Mermaid renderer, link unfurler, browser client. |
| | **`relay`** · Rounded `([ ])` | Process that stores or passes raw bytes or typed values through unchanged. | Audit log archive, encrypted transport passthrough. |
| **Step 2: Flow Labels & Fidelities**<br/>*(attached to directed data flows)* | **Trust labels:**<br/>`Untrusted` · `Trusted` · `Secret` | Provenance and sensitivity of a flow. A process with multiple inputs propagates the *least-trusted* (`Untrusted`) and *most-secret* (`Secret`) labels among its inputs. | Customer ticket (`Untrusted`), verified system configuration (`Trusted`), internal fraud header or private calendar (`Secret`). |
| | **`Full` fidelity** | Preserves the raw carrier, including covert or sub-perceptual channels ignored by ordinary reading, as well as outputs of model-based extractors (`OCR`, `ASR`). | *Text:* raw Unicode (zero-width/tag chars intact). *Image/doc:* raw pixels, EXIF, hidden PDF layers, aliasing downscale. *Audio:* full spectrum, near-ultrasonic or reverberant perturbations. *Video:* unsampled frames, auxiliary tracks. |
| | **`Normalized` fidelity** | Retains only features an ordinary human reader perceives after a deterministic transform strips residual channels. | *Text:* canonicalized Unicode with control/tag chars stripped. *Image/doc:* re-encoded pixels, metadata stripped, anti-aliased resampling. *Audio:* band-limited anti-aliased resampling. *Video:* fixed frame grid with auxiliary tracks stripped. |
| | **`Typed` fidelity** | Constrained to values of a narrow, schema-enforced primitive type across any modality. | Fixed enum (`L = {billing, technical, ...}`), bounded numeric value, or allowlisted identifier. |

*Table 3. Data-flow diagram shape and annotation reference across Steps 1 and 2.*

### 4.1 Step 1: Sink Constraints

Security is defined relative to an explicit policy that partitions system states into authorized and unauthorized ones (Bishop, 2002). Two evaluators always differ in minor details, so violations are measured against explicit constraints on the system's sinks: untrusted content steering execution presupposes rules on what untrusted data may legitimately influence, a confidentiality breach presupposes approved recipients, and resource exhaustion presupposes a budget.

Following STPA-Sec's top-down sequence (Young & Leveson, 2013), the analyst derives sink constraints in three substeps:

1. **Stakeholder losses:** Unacceptable business, operational, or physical outcomes (for example, *unauthorized wire transfers, leaked confidential records, unreviewed fraud or abuse reports, or physical collision with a pedestrian*).
2. **System hazards:** System-level states or outputs that precipitate a loss (for example, *a payment executes with terms differing from an approved invoice, sensitive context reaches an unapproved recipient, or a high-risk item bypasses human review*).
3. **Per-sink constraints:** Enforceable conditions attached to each authority (`executor`/`renderer`), egress (`receiver`), susceptible (resource-consuming), and safeguard (`guard`) sink on the DFD (**Table 3**, Step 1). Because agents often exist specifically to process untrusted inputs (such as supplier invoices or support tickets), an authority sink's **Flow clearance** states *which choices* untrusted data cannot steer (such as tool selection or bank routing overrides) and *through which narrowed types* it may legitimately act, while its **Reference specification** defines the ground-truth source that acted-on values must match.

Three rules govern Step 1:

* **State an explicit safeguard obligation for every safeguard whose job is to intervene.** Attacks that suppress a fraud flag, omit a malicious message from an executive summary, or make a video quality-control sampler skip non-compliant frames execute no unauthorized tool call. A liveness bound on the safeguard sink (for example, *"before settlement"* or *"within 1 hour"*) is what makes a suppressed alert a violation.
* **Record an unconstrained sink as an architectural finding.** If policy lets a client previewer fetch images from any external host, exfiltration via rendered Markdown breaks no stated rule; the finding is the missing security requirement.
* **Attach STRIDE impact categories to sink constraints.** Because STRIDE names the downstream consequence, the same `Meaning` divergence can cause Elevation of Privilege, Information Disclosure, or Tampering depending on which sink its path reaches.

### 4.2 Step 2: Annotated Data-Flow Diagram

Starting from the system's DFD, the analyst assigns a functional role to each process and external entity and annotates each directed flow with a trust label and representational fidelity (**Table 3**, Step 2).

**Assigning functional roles.** Roles describe pipeline behavior rather than underlying vendor technology:
* An LLM that only blocks unsafe inputs carries the `«guard»` role (its susceptibility to evasion is a `Guard-Model Capability` crossing); an LLM whose output drives downstream data, routing, or tool selection carries the `«follower»` role.
* **Draw `«executor»` and `«renderer»` nodes as separate processes from the `«follower»` node that invokes them.** The `«follower» → «executor»` or `«follower» → «renderer»` edge is the decision interface, and its *fidelity* is often the most consequential annotation on the diagram: if a model emits only a schema-validated enum (`Typed` fidelity), an attacker who steers the model is limited to selecting an incorrect enum value (a `Meaning` violation), which closes `Flow (integrity)`.
* **Aggregation is structural.** Any process with two or more incoming flows is an aggregation point.

**Unpacking multimodal and agentic pipelines (Step 2 checklist).** High-level diagrams often collapse preprocessing, extraction, and rendering into a single "AI service" box (**Appendix B.2** maps these locations to traditional processing stage names). Before Step 3, verify that the DFD unpacks six commonly hidden elements:
1. **Hidden transforms (`«transform»`):** Image downscalers, audio resamplers, video frame samplers, Unicode/HTML normalizers, decoders, and archive or document container splitters.
2. **Perceptual extractors (`«transform»` or `«follower»`):** OCR, ASR, captioning, or object-detection components that convert one carrier into another before reasoning.
3. **Guard placement (`«guard»`):** Whether human review, content filtering, or schema validation inspects the artifact *before* or *after* a `«transform»`.
4. **Decision-to-action interfaces (`«follower» → «executor»`):** Every tool connector, query runner, router, or physical actuator, separated from the model that invokes it.
5. **Active output consumers (`«follower» → «renderer»`):** Any chat UI, preview console, Markdown/Mermaid renderer, or link unfurler that interprets markup or fetches remote URLs.
6. **Single-session feedback loops (`«executor» / «renderer» → «follower»`):** Any path where tool outputs, retrieved records, or captured browser screenshots re-enter the ongoing execution cycle.

**Why only deterministic transforms grant `Normalized` fidelity.** Marking a flow `Normalized` asserts that covert channels absent from ordinary human perception have been removed deterministically, such as stripping PDF metadata, canonicalizing Unicode, or applying an anti-aliased low-pass filter before downsampling (an aliasing downscaler's output stays `Full`). Output flows from model-based extractors (`OCR`, `ASR`, captioners) stay at `Full` relative to a human reference because machine and human perception differ: OCR can transcribe low-contrast or micro-printed instructions a human reviewer overlooks and emit them downstream as plain `Overt Semantic` text.

**Deriving trust boundaries.** A trust boundary falls automatically across every flow whose propagated label changes or violates the receiving sink's flow clearance; any mismatch with an architect's intuition highlights an unexamined trust assumption.

### 4.3 Step 3: Deriving Crossings, Attack Chains, and Cut Points

Once the diagram is annotated, findings follow from seven traversal rules (lookup tables and formal rules appear in **Appendix A**):

1. **Enumerate and group paths.** Trace every directed path from an external `source` to a constrained sink and from a `Secret` store or input to an external `receiver`, grouping parallel edges that share the same `(source, guards crossed, sink)`.
2. **Identify boundary crossings (`Invariant × Divergence`).** Along each grouped path, node-and-edge patterns determine candidate crossings mechanically (**Appendix A, Table A.1**). A sink's *Reference specification* serves as the evaluation baseline and generates crossings only for `Meaning` reference constraints (**Appendix A.1**).
3. **Look up surviving representations.** At each crossing, intersect the incoming flow fidelity (`Full`, `Normalized`, or `Typed`) with the representation survival table (**Section 3.2, Table 2**) to determine which forms (*Overt Semantic*, *Encoded / Obfuscated*, *Steganographic*, or *Adversarial Perturbation*) arrive intact.
4. **Emit mechanism records (one crossing per record).** Emit one record `M = ⟨Invariant, Divergence, Representation⟩` per crossing judged *realizable* by an attacker, noting its evidence maturity (`Observed`, `Demonstrated`, or `Feasible`). Keeping records 1-to-1 with crossings (so evading an input `«guard»` and steering a `«follower»` emit two distinct records even from a single payload) keeps chain lengths comparable across architectures.
5. **Assemble attack chains (supplied vs. granted legs).** Each required step toward violating a sink constraint is a **leg**: **granted** when the architecture permits passage unconditionally (unguarded channels, `auto-approve` tools, or task-permitted navigation) and **supplied** when a deployed `«guard»` forces an active bypass:
   * Harm requires *every leg* of a sink violation; the attacker supplies whichever legs the architecture did not already grant (yielding single-record exploits when remaining legs are granted, or in standalone `Time` and `Cost` failures).
   * Records link wherever one crossing's postcondition satisfies the next crossing's precondition. **Confidentiality exfiltration chains** join an integrity path (steering a `«follower»` that holds `Secret` state) with a confidentiality path (carrying that `Secret` output to an unauthorized `«receiver»`), capturing the "lethal trifecta" (Willison, 2025) as graph topology. *Fragmented / Distributed* payloads emit one `Meaning × Artifact State` aggregation record with a conjunctive precondition across the contributing flows.
6. **Compute minimal structural cut points.** Identify the minimum set of flows or processes whose hardening or removal disconnects external sources from violated sinks (e.g. narrowing a `«follower» → «executor»` flow from `Full` to `Typed`, or gating an auto-fetching `«renderer»`).
7. **Verify annotation coverage.** Confirm that every process, flow, and sink is annotated, flagging any unannotated element as a specification gap and recording the structural reason (*`relay` node, trusted and unreachable, within sink constraint, or out of scope*) whenever an element produces zero crossings.

Completeness holds relative to the diagram: an omitted flow means an omitted chain. Structural reachability determines which representations *can arrive* at a crossing; whether a specific model is affected is an empirical question tracked via evidence maturity and verified in Step 4.

### 4.4 Step 4: Deriving Security Tests and Reverse Triage Order

Each derived attack chain maps to a falsifiable **security test scenario** whose pass/fail oracle is the target sink constraint:

* **Test setup and input:** Construct an entry artifact at `«source»` using the surviving `Representation` form(s) required for each attacker-*supplied* leg while leaving *granted* legs in their default state.
* **Pass/fail oracle:** The test *fails* (confirming the vulnerability) if and only if execution violates the terminal **Sink Constraint** (*Flow clearance*, *Reference specification*, *Resource budget*, or *Safeguard obligation* window).

Design-time reports can present compact summary counts by crossing pattern, sink, and cut point in the main text while placing exhaustive derivation tables in an appendix (e.g. the 15-component Invoice-Processing Agent in **Appendix D.1** yields 17 crossings, 1 missing-safeguard gap, 13 realizable records, 9 chains, and 13 tests).

**Reverse traversal for incident mechanism triage (Use Case C).** To triage a disclosed vulnerability or incident (**Section 5.2**), run the same method in reverse on a minimal diagram:
1. Draw *only* the path traversed from entry `«source»` to harmed sink using vendor-neutral functional roles (`«guard»`, `«transform»`, `«follower»`, `«executor»`, `«renderer»`).
2. Annotate roles, flow labels/fidelities, and the violated sink constraint along that path, then apply Step 3 to emit the chain's mechanism records, separate *supplied* bypasses from *granted* legs, and locate minimal cut points.
3. Any architectural detail omitted from the incident report (such as whether a filter inspected the raw upload or the resized tensor) surfaces as an unannotated element, defining the exact triage question to ask the system owner; matching the resulting chain against the full DFD reveals sibling exposures across other tools and modalities.


## 7. Worked Examples and Case Studies

### 7.1 Image-Scaling Prompt Injection

#### 7.1.1 Worked Example 1: Image-Scaling Prompt Injection Across Modality Analogs

An uploaded image appears benign at the representation reviewed by a human or upstream control, but resizing produces an effective instruction that the multimodal model interprets and an agent executes.

| Dimension | Classification |
| :---- | :---- |
| Boundary – Meaning | Transform Consistency (pre-transform vs. post-transform evaluation) |
| Boundary – Authority | Data-Control (data role vs. control role) |
| Representation | Processing-Dependent (pre-transform) → Overt Semantic (post-transform) \+ Transformation-Activated modifier |
| Construction | White-box optimization (pixel optimization against resizing algorithm) |
| System Processing Stage | Transformation → Interpretation / Decision → Generation → Action |
| Modality | Image |
| STRIDE mapping | Elevation of Privilege when the attack exercises unauthorized agent authority; potentially Information Disclosure if data is exfiltrated. |
| ATLAS mapping | Prompt Injection / Prompt Obfuscation-related adversary behavior. |
| NIST context | Inference-time; attacker supplies image; white-box optional.  |
| Adversary behavior | AML.T0051 Prompt Injection (or ATLAS Prompt Obfuscation if encoded) |
| Attacker assumptions | Inference-time; attacker supplies image; white-box optional |
| OpenCRE relation | Broader than named prompt-injection CRE; map Data-Control as related |

The modality-independent claim is not that every implementation is identical. It is that the same abstract mechanism can recur through different preprocessing and representation paths.

| Modality | Transformation | Concrete instance | Boundary | Representation | Stage | Evidence |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Text | Unicode / entity / URL decode | Message contains \`%0AIgnore%20prior\` or homoglyphs that look benign in the review UI; after decode the model sees a new instruction. | Transform Consistency; Data-Control | Encoded / Obfuscated \+ Transformation-Triggered | Transformation to Interpretation to Action | Observed |
| Image | Resize / crop / OCR reveals instruction | Uploaded image looks like a product photo at review size; after downscale or OCR the model reads \`authorize refund \$500\`. | Transform Consistency; Data-Control | Processing-Dependent → Overt Semantic \+ Transformation-Triggered | Transformation to Perception to Interpretation to Action | Demonstrated |
| Audio | Resample / codec activates spoken command | Clip sounds like music at 48 kHz; after downsample to 16 kHz ASR emits \`transfer funds to account 9912\`. | Transform Consistency; Data-Control | Processing-Dependent \+ Transformation-Triggered | Transformation to Perception to Interpretation to Action | Demonstrated |
| Video | Frame sampling omission (existing A3/A16) | Harmful or out-of-contract shot sits between sampled frames; QC model never sees it and certifies the title. | Transformation Differential; Guard-Model Capability | Steganographic; Temporal; Fragmented | Transformation to Perception | Feasible |
| Video | Transformation-triggered injection (new) | Slate text is unreadable at source resolution; after player letterbox/OCR the diligence agent treats burned-in text as task instructions. | Transformation Differential; Data-Control; Human-Machine Perception | Overt Semantic \+ Transformation-Triggered | Transformation to Perception to Interpretation to Action | Feasible |
| Structured | Deserialization / formula / macro as control | CSV cell or JSON field looks like a SKU; spreadsheet formula or YAML tag coerces into a tool argument that deletes a bucket. | Parser / Interpreter Differential; Data-Control | Encoded / Obfuscated \+ Transformation-Triggered | Transformation to Interpretation to Action | Observed |

Evidence maturity levels: **Observed** — documented in real-world production incidents. **Demonstrated** — proven in research with end-to-end exploitation. **Feasible** — plausible extrapolation from demonstrated mechanisms.


### 7.2 Example: Sequence-Dependent Injection Across Streaming Artifacts

**Scenario**  
An attack first discovered in video frames predicts a non-obvious vulnerability in streaming text:

* **Video:** Frames 40 (ignore), 95 (previous), 150 (instructions), 205 (and), 260 (forward), 315 (all), 370 (emails). No single frame contains an instruction.  
* **Streaming Text:** Chunk 1 (... ignore), Chunk 2 (... previous), Chunk 3 (... instructions), Chunk 4 (... and), Chunk 5 (... forward), Chunk 6 (... all), Chunk 7 (... emails). A per-chunk content filter approves every chunk in isolation, while the LLM context aggregates them into an active command.

#### 7.2.1 Resulting Classification

| Dimension | Classification | Why |
| :---- | :---- | :---- |
| Boundary — Meaning  | Transform Consistency | Security evaluation occurs on fragmented units; model evaluates aggregated units. |
| Boundary — Authority  | Data-Control | Stream entered as untrusted data but reconstructed content acquires control authority. |
| Representation | Overt Semantic | No decoding secret required once assembled. |
| Modifiers | Fragmented / Distributed; Sequence-Dependent  | Payload emerges only after aggregation, and meaning depends on ordering. |
| System Processing Stage | Ingestion → Transformation → Interpretation / Decision → Action  | Enters normally, aggregates in context, interpreted as instruction. |
| Modality | Video or Streaming Text | Implementation surface changes while mechanism classification remains constant. |
| Evidence Maturity | Demonstrated (Video) / Feasible (Streaming Text) | Demonstrated in video temporal slicing; feasible across streaming guardrails. |


### 7.3 Full-Pipeline Traversal: Image Transformation to Agent Action

**Scenario.** A legitimate user's agent analyzes an attacker-controlled image to prepare an internal report. An upstream guard approves the original image, but resizing reveals concealed instructions. OCR extracts those instructions, which the reasoning model incorrectly treats as authoritative. The model requests an external transfer of confidential data, and the tool executor performs it without enforcing the required authorization.

This is an illustrative composite scenario, not a single independently verified end-to-end exploit. Rendering a later report is a **Consumption** step, but not another security violation.

```mermaid
flowchart LR
    I["Image ingested"] --> V["Original image approved"]
    V --> T["Resize reveals instructions"]
    T --> P["OCR extracts text"]
    P --> D["Agent follows injected text"]
    D --> G["Tool request generated"]
    G --> A["Unauthorized transfer executed"]
    A -. optional .-> C["Report consumed"]
```

*Figure 2. Attack processing sequence; approval is a security check, not an additional taxonomy stage.*

#### 7.3.1 Classification of Security Mechanisms

| Mechanism | Boundary and failure condition | Representation | Processing stage |
|---|---|---|---|
| **M1: Transformation-dependent activation** | **Transform Consistency:** Resizing invalidates an earlier security assessment on which the system relies. | **Processing-Dependent → Overt Semantic**; **Transformation-Activated**. | **Entry:** Ingestion; **activation:** Transformation → Perception / Extraction. |
| **M2: Instruction authority takeover** | **Data-Control:** Lower-trust OCR text is promoted into authoritative instructions. | **Overt Semantic** extracted text. | **Effect:** Interpretation / Decision. |
| **M3: Unauthorized tool execution** | **Decision-Action:** The executor performs a prohibited transfer without the required authorization. | Induced instruction expressed in a structured tool request; the tool format is supporting context, **not a new Representation Form**. | Generation → Action; **effect:** Action. |

These are three separate security failures. Resizing, OCR, and creating a tool request are not violations by themselves. Consumption is a stage; it only becomes an **Output-Consumer** violation if processing the output independently causes a prohibited effect.

#### 7.3.2 Candidate controls

Because the record separates what failed (Boundary), how the adversarial content became effective (Representation), and where it happened (Processing Stage), each failure points to its own check: inspect transformed inputs (M1), enforce the instruction/data boundary (M2), and authorize tool operations independently (M3). These are candidate controls, not proven mitigations for the composite scenario.

#### 7.3.3 Comparison With Existing Security Frameworks

| Framework | What it highlights | Additional detail provided by this taxonomy |
|---|---|---|
| **NIST AI 100-2e2025** [1] | Indirect prompt injection (`NISTAML.015`) and compromised connected resources (`NISTAML.039`). | Separates transformation activation (M1), instruction authority (M2), and tool authorization (M3). |
| **NIST AI RMF 1.0** [2] | Risk identification, security assessment, and risk treatment (`MAP`, `MEASURE`, `MANAGE`). | Specifies the mechanism and pipeline point to evaluate. |
| **IBM AI Risk Atlas** [3] | Indirect instructions, prompt injection, and confidential-data sharing through tools. | Distinguishes pre-/post-transform content, authority takeover, and execution failure. |
| **MITRE ATLAS** [4] | Indirect prompt injection (`AML.T0051.001`), relevant obfuscation (`AML.T0068`), and exfiltration via agent tools (`AML.T0086`). | Links representation-state changes to distinct violated security assumptions and effect locations. |
| **MITRE D3FEND** [5] | Candidate defenses, including File Content Analysis (`D3-FCOA`) and Outbound Traffic Filtering (`D3-OTF`). | Locates where candidate controls should be evaluated; does not claim they are validated mitigations. |
| **MAESTRO** [6] | Exposure across data, foundation-model, agent-framework, and connected-service layers. | Adds representation and processing-stage detail without conflating stages with architectural layers. |
| **STRIDE** [7] | Information Disclosure; potentially Tampering and Elevation of Privilege, depending on the threat model. | Identifies the specific mechanisms producing those broader threat categories. |

A few caveats on these mappings. The indirect-injection labels assume the image is controlled by an attacker other than the legitimate user. D3FEND entries are candidate defenses. STRIDE categories and MAESTRO layers are not one-to-one equivalents of M1 to M3.

#### 7.3.4 Comparative Takeaway

Existing frameworks already cover prompt injection, connected-tool misuse, risk management, and defensive controls. What the taxonomy adds is linking **Boundary × Representation × System Processing Stage** at each step of the attack chain. How much that helps in practice still needs to be measured through repeatable classification and targeted security testing.

### 7.4 Example: Multi-Hop Browser Agent Attack via Feedback Loop

**Scenario**  
A computer-use agent views a webpage (Screenshot 1), clicks a link, receives a new screenshot (Screenshot 2) containing an image-based prompt injection, interprets the injected instructions, and executes an unauthorized action. The attacker never sends the payload directly — they place a trap on a page the agent navigates to through its own browsing loop.

```mermaid
%%{init: {"flowchart": {"wrappingWidth": 180}}}%%
flowchart LR
    S1["<b>Screenshot 1</b><br/>Benign page<br/>with lure link"]
    C["<b>Action</b><br/>Agent clicks link"]
    F["<b>Feedback</b><br/>New page loads"]
    S2["<b>Screenshot 2</b><br/>Contains injection"]
    I["<b>Interpretation</b><br/>Agent reads injected<br/>instructions"]
    A["<b>Action</b><br/>Unauthorized<br/>operation"]
    S1 --> C --> F --> S2 --> I --> A
```

*Figure 3\. Two-hop attack chain. The agent's own action (clicking) produces the artifact (Screenshot 2) that carries the adversarial payload back into the pipeline through the Feedback stage.*

#### 7.4.1 Linked Mechanism Records

| Record | Boundary | Representation | Construction | Stage | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **M1: Lure / navigation** | Data-Control (web page content steers the agent to click a specific link — data influences a navigation decision) | Overt Semantic (the link is visible on the page) | Manual (attacker placed the link on a page the agent visits) | Ingestion → Perception → Interpretation → Action (click) | The first pass through the pipeline is benign-looking navigation. The agent follows a link the same way it would follow any other. |
| **M2: Injection delivery via feedback** | Transform Consistency (the screenshot the agent captures vs. what a human reviewing the original page would evaluate) + Data-Control (screenshot content acquires instruction authority) | Overt Semantic (typographic injection visible in the screenshot) + Transformation-Activated (if the screenshot capture or rendering changes the representation) | Manual (attacker placed injection text on the destination page) or White-box optimization (if exploiting rendering pipeline) | Feedback → Ingestion → Perception → Interpretation / Decision | The Feedback stage is the critical link: the agent's own action produces the artifact that carries the injection. The attacker doesn't send the payload — the agent fetches it. |
| **M3: Unauthorized action** | Decision-Action (the agent executes an operation based on injected instructions, under system authority) | Structured data (tool call, browser action, or API request) | n/a | Generation → Action | Same pattern as M3 in Sections 7.2 and 7.3. An independent authorization gate would block this regardless of whether M1 and M2 succeeded. |

#### 7.4.2 Feedback as the attack vector

This is the first worked example where the Feedback stage carries the attack. In the earlier examples (Sections 7.1.1, 7.2, 7.3), the adversarial artifact enters once at Ingestion and flows forward. Here the attack needs two passes through the pipeline, connected by Feedback: the result of an Action (a new page loads) re-enters as Ingestion for the next cycle, so the agent's own browsing loop delivers the payload.

**It demonstrates agent-generated adversarial artifacts.** The agent itself produces the screenshot that contains the injection. This is conceptually similar to the Repeat-After-Me context-reuse pattern (M3 in the scenario analysis), but occurs within a single execution context — the browsing loop — rather than across sessions. This keeps it in-scope under the Feedback stage definition ("outputs, tool results, or environmental observations re-enter the execution loop").

**The two-hop structure shows how a benign first action enables a malicious second action.** M1 (clicking a link) is indistinguishable from normal browsing behavior. Content-filtering the first screenshot would find nothing adversarial. The attack only materializes after the agent acts on the lure, producing a second artifact that carries the actual payload. Defenses that inspect only the initial input miss this entirely.


### 7.5 Worked Example: Cross-Modal Semantic Completion

**Scenario:** A user submits a text message saying "jump" alongside an image showing a person standing on top of a tower. Neither input is adversarial alone — "jump" is a common word, and the image is an ordinary photograph. However, the multimodal model fuses both inputs and interprets a harmful instruction: "make the person jump from the tower."

| Record | Boundary | Representation | Construction | Stage | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| M1: Cross-modal meaning emergence | Semantic Stability (meaning of the combined input differs from meaning of each input independently) | Overt Semantic (text) + Overt Semantic (image), **Composition-Dependent** modifier | Manual | Ingestion → Perception → Interpretation / Decision | Neither artifact alone carries the harmful meaning. The adversarial effect exists only in the fused interpretation. |
| M2: Harmful action (conditional) | Data-Control (fused interpretation acquires instruction authority) + Decision-Action (if agent executes) | Overt Semantic (generated instruction) | n/a | Interpretation → Generation → Action | Applies only if the system acts on the fused interpretation — e.g., an agent with tool access. A chatbot producing harmful text is a safety failure; an agent executing the instruction is an authority failure. |

**Why the Composition-Dependent modifier is needed:** Without it, the taxonomy classifies each artifact correctly (both are Overt Semantic) but cannot express that the adversarial effect requires their co-processing. The Fragmented / Distributed modifier does not fit because there is no single payload split into pieces — there are two independent artifacts whose combined interpretation is harmful. The composition operator is **Completion**: the text supplies the action ("jump") while the image supplies the context (the tower), and neither is meaningful as an instruction without the other.

**Key distinction:** This differs from a typographic prompt injection (I9 in the cross-modality table), where a single artifact carries the full adversarial instruction. Here, the harmful meaning is emergent — it exists only at the fusion layer, not in either input.

### 7.6 Worked Example: Cross-Modal Contradiction

**Scenario A:** A text message says "send $10" while an accompanying screenshot shows a $10,000 transaction. The model must decide which modality to trust for the transaction amount.

**Scenario B:** A compliance report states "the worker is wearing a helmet" while the attached image shows a worker without a helmet. An inspection agent must determine whether the site is compliant.

In both cases, neither input is adversarial in isolation — a text instruction to send $10 is legitimate, and a photo of a worker is an ordinary image. The attack lies in the deliberate inconsistency between them, crafted to exploit the model's conflict-resolution behavior.

| Record | Boundary | Representation | Modifier | Construction | Stage | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| M1: Cross-modal contradiction | Semantic Stability (the security-relevant meaning differs depending on which modality the model prioritizes) | Overt Semantic (text) + Overt Semantic (image) | Composition-Dependent | Manual | Ingestion → Perception → Interpretation / Decision | The attacker crafts the pair so that the model's arbitration — whichever modality it trusts — produces an incorrect outcome. |
| M2: Incorrect action (conditional) | Decision-Action (the model acts on the wrong interpretation) | Overt Semantic (generated decision or transaction) | — | n/a | Interpretation → Generation → Action | In Scenario A: $10,000 is processed instead of $10. In Scenario B: non-compliance is certified as compliant. |

**How the attack exploits arbitration:**

| Scenario | If model trusts text | If model trusts image | Attacker's goal |
| :---- | :---- | :---- | :---- |
| A: $10 vs. $10,000 | Processes $10 (correct) | Processes $10,000 (attacker wins) | Model trusts the screenshot |
| B: Helmet claim vs. no-helmet photo | Certifies compliant (attacker wins) | Flags non-compliance (correct) | Model trusts the text claim |

The attacker can tailor the pair to exploit whichever arbitration bias the model has. If the model generally trusts visual evidence over text, the attacker puts the malicious value in the image. If it trusts text claims, the malicious value goes in the text.

**Composition operator: Contradiction** (from the Section 6.3 table). In Completion (Section 7.5), both modalities cooperate to produce an emergent meaning. In Contradiction, the modalities deliberately conflict, and the attack exploits whichever one the model treats as authoritative.

**Comparison with A17 (Audio Contradiction / Speech Exploit):** The A17 entry in the control-coverage matrix (Section 9.2.1) also uses Contradiction as the composition operator, but with Processing-Dependent representation (an adversarially optimized audio waveform). In these scenarios both modalities are Overt Semantic, so the contradiction is between two plainly readable/viewable inputs. The boundary (Semantic Stability) and composition operator are the same, and only the representation form differs, which is enough for the taxonomy to tell them apart: A17 requires detecting a processing-dependent perturbation, while these scenarios require detecting a logical inconsistency between two overt inputs.


## Appendix A: Formal Derivation Specification

This appendix specifies the formal graph-traversal lookup rules and propagation properties used in Step 3 of the architectural analysis method (**Section 4.3**).

### A.1 Step 3 Crossing-Derivation Lookup Table

Along each grouped directed path from an external `«source»` to a constrained sink (or from a `Secret` store/input to an external `«receiver»`), structural node-and-edge patterns determine candidate boundary crossings (`Invariant × Divergence`) mechanically:

| Structural Pattern Along the Directed Path | Derived `Invariant × Divergence` | Named Boundary Subclass(es) |
| :---- | :---- | :---- |
| A downstream process acts on content in the same artifact state that a deployed `«guard»` (or the sink's stated *Reference specification*) evaluated | **Meaning × Evaluator** | *Human-Machine Perception*; *Guard-Model Capability* (deployed reference); *Semantic Stability* (idealized reference) |
| A `«transform»` modifies the artifact between an upstream `«guard»` (or the sink's *Reference specification*) and downstream consumption | **Meaning × Artifact State** | *Transform Consistency* |
| A `«guard»` and a downstream consumer inspect *different* parallel transforms or parses of the same upstream artifact (for example, two parsers, or a human approval card vs. raw tool arguments) | **Meaning × Evaluator** | *Parser / Interpreter Differential* |
| Guards inspect individual flows separately before a downstream process aggregates them, or a *Safeguard obligation* bounds a cumulative total that guards check only per item | **Meaning × Artifact State** | *Transform Consistency* (aggregation) |
| An upstream `«guard»` validates a data store at time `t`, and a downstream consumer re-reads that store at `t + Δ` | **Meaning × Time** | *Check-Use Consistency* |
| A permission or capability grant remains active at a sink after its authorized task window or revocation | **Flow (integrity) × Time** | *Grant Persistence* |
| A flow reaches an authority or egress sink carrying a trust/sensitivity label or fidelity prohibited by that sink's *Flow clearance* (or triggers an `«executor»` that skips a required authorization check) | **Flow × Position** | *Data-Control*, *Decision-Action*, or *Delegation Authority* (integrity); *Context Confinement* or *Output-Consumer* (confidentiality) |
| An instruction-following (`«follower»`) process controls whether or what a safeguard sink records or escalates | **Flow (integrity) × Position** | Culminates in a *Safeguard obligation* breach |
| A susceptible sink's resource expenditure is unbounded by its upstream admission check against its *Resource budget* | **Cost × Evaluator** | *Resource Accounting* |

*Table A.1. Step 3 structural crossing-derivation lookup table.*

**Evaluation-baseline rule for reference specifications.** A sink's *Reference specification* (for example, *"the invoice total as read by a human reviewer"*) serves as an evaluation baseline rather than a runtime gate. Comparing a process against an idealized reference generates crossings only for `Meaning` reference specifications, where extracting or acting on an incorrect value is itself the hazard; for a *Flow clearance*, concealment matters only when a deployed human or automated `«guard»` stands on the path.

### A.2 Path-Grouping, Flow-Fidelity Propagation, and Chain-Length Rules

1. **Label propagation across multi-input nodes:** Any process receiving `k ≥ 2` incoming flows propagates the *least-trusted* provenance label (`Untrusted < Trusted`) and the *most-sensitive* confidentiality label (`Secret > Public`) to its outbound flows unless a deterministic rule on a `«guard»` or `«executor»` strips or rejects that label.
2. **Flow-fidelity transitions:**
   * A flow leaves an external `«source»` at `Full` fidelity unless constrained by physical or protocol framing.
   * Only a deterministic `«transform»` that strips sub-perceptual and metadata channels relative to ordinary human perception transitions a flow from `Full` to `Normalized`; model-based extractors (`OCR`, `ASR`, captioners) leave outbound fidelity at `Full` relative to a human reference.
   * Only deterministic schema validation to a narrow primitive (enum, bounded number, allowlisted ID) transitions a flow to `Typed`.
3. **Path grouping:** Parallel edges sharing the same `(source, guards crossed, sink)` form a single equivalence class before crossing enumeration, preventing combinatorial path explosion on multi-tool agents.
4. **Chain-length accounting:** A complete attack chain contains one record per *supplied* guard-bypass leg, one record per flow-clearance-violating edge into a sink, and (for `Meaning` reference specifications) one record per reference divergence, so chain length counts how many independent barriers the architecture forces an attacker to overcome.

---

## Appendix B: Supporting Annotation Schema and Machine-Readable Format

### B.2 System Processing Stage Reference Mapping

*System Processing Stage* is derived from where a crossing occurs on the annotated DFD (**Section 4.2**). To support crosswalks with stage-oriented reports and benchmarks, **Table B.2** maps traditional functional stage definitions and location tags (*Entry*, *Activation*, *Effect*) deterministically to DFD roles and path positions:

| Processing Stage | Operational Definition | Deterministic DFD Role & Path Mapping |
| :---- | :---- | :---- |
| **Ingestion** | An artifact enters the system through an input channel, sensor, tool response, or external data source. | Outbound flow from an external `«source»` (or initial read from an untrusted data store) into the first system node (**Entry** location). |
| **Transformation** | An artifact undergoes processing that changes its encoding, structure, resolution, format, segmentation, or ordering. | Deterministic or algorithmic `«transform»` node (resizer, decoder, normalizer, resampler, frame sampler, chunker) where a `Meaning × Artifact State` crossing activates (**Activation** location). |
| **Perception / Extraction** | A model or subsystem extracts or recognizes content, features, symbols, objects, speech, or other information from an artifact. | Perceptual extractor (`OCR`, `ASR`, object detector) or multimodal encoder interface (`«transform»` or `«follower»`) where `Human-Machine Perception` or `Guard-Model Capability` crossings activate. |
| **Interpretation / Decision** | The system assigns meaning, assesses relevance or authority, and determines an appropriate response or operation. | Instruction-following or decision-making `«follower»` node (or policy `«guard»`) where `Data-Control` or `Semantic Stability` crossings take effect (**Effect** location). |
| **Generation** | The system produces a response, output artifact, tool request, or action parameters. | Outbound decision/output flow emitted by a `«follower»` toward an `«executor»`, `«renderer»`, or external `«receiver»` (carrying `Full`, `Normalized`, or `Typed` fidelity). |
| **Action** | A generated request or decision is executed through a tool, API, application, or actuator, changing state or transferring information. | `«executor»` sink (or physical actuator `«receiver»`) governed by a *Flow clearance* and *Reference specification* where `Decision-Action` or `Delegation Authority` takes effect. |
| **Consumption** | Generated output is rendered, displayed, transmitted, decoded, or fetched by a downstream component or recipient. | `«renderer»` node or outbound flow to an external `«receiver»` governed by an egress *Flow clearance* where `Output-Consumer` or `Context Confinement` takes effect. |
| **Feedback** | Outputs, tool results, or environmental observations return to an ongoing execution loop and influence subsequent processing. | Directed cycle edge from an `«executor»`, `«renderer»`, or mutated data store back into an upstream `«transform»` or `«follower»` within the same execution session. |

*Table B.2. Mapping functional processing stages and Entry/Activation/Effect locations to annotated DFD elements.*

The DFD mapping keeps these stage distinctions:
* **Transformation vs. Perception / Extraction:** Deterministic media/encoding transforms (`«transform»`) alter artifact state (`Meaning × Artifact State`). Perceptual extraction (`OCR`, `ASR`, model encoders) evaluates content (`Meaning × Evaluator`, leaving output flow fidelity at `Full` relative to a human reference).
* **Generation vs. Action vs. Consumption:** Emitting a tool request or markup draft (`«follower»` outbound edge), executing the tool (`«executor»`), and rendering active markup in a client (`«renderer»`) are three separate steps.
* **Feedback vs. Ingestion:** A tool response or browser screenshot returning along a cycle edge constitutes *Feedback* from the prior action and *Ingestion* into the next pass of the `«follower»`.

### B.3 Machine-Readable Schema and Reusable Assessment Assets

To support automated traversal and cross-team reuse (**Section 7**), annotated DFDs, derived mechanism records, and security test plans can be serialized in a versioned JSON or YAML reference format containing five linked components:

* **Taxonomy Catalog:** Standardized identifiers and lookup rules for `Invariant × Divergence` cells, `Representation` forms and modifiers, and flow fidelities.
* **Annotated DFD Specification:** Nodes (`id`, `role`, `sink_constraints`), directed flows (`source`, `target`, `trust_label`, `fidelity`, `modality_context`), and path-grouping equivalences.
* **Derived Mechanism & Chain Inventory:** Realizable crossings (`M = ⟨Invariant, Divergence, Representation⟩`), assembled attack chains with explicit `granted` vs. `supplied` legs, evidence maturity (`Observed`, `Demonstrated`, `Feasible`), and minimal structural cut points.
* **Security Test Catalog:** Reusable test templates generated per chain, specifying entry source, required representation payload, and the target sink constraint used as the pass/fail oracle.
* **Framework Crosswalk Links:** Machine-readable pointers from each record and sink constraint to MITRE ATLAS, NIST AI 100-2, OWASP, CoSAI Risk Map / SAIF, CWE, and STRIDE (**Appendix C**).

---

## Appendix C: Framework and Standards Crosswalks (Staging)

*(Note: Consolidated framework crosswalk tables across §3.2, §5.3.4, §5.4.3, and §7.3.3 will be merged here under Requirement 6.)*

| Framework | Existing Focus | Relationship to DFD Pipeline Locations (from §5.3.4) |
|---|---|---|
| **NIST AI 100-2e2025** | Adversarial machine-learning terminology, attack lifecycle concepts, attacker objectives, capabilities, and knowledge. | Provides a broader threat taxonomy. DFD roles and path crossings identify operational locations within a target system's inference-time execution flow. |
| **MITRE ATLAS** | Adversarial tactics and techniques targeting AI-enabled systems. | Identifies techniques such as prompt injection and exfiltration through agent tools. Annotated DFD paths locate where these techniques enter, activate, and take effect. |
| **OWASP Top 10 for LLM Applications (2025)** | Application-level security risks, including Prompt Injection (LLM01), Improper Output Handling (LLM05), and Excessive Agency (LLM06). | Maps to sink constraints and crossings across `«follower»` (`LLM01`), `«executor»` (`LLM06`), and `«renderer»` (`LLM05`) nodes. |
| **MITRE CWE** | Software weaknesses and their underlying conditions. | Weaknesses such as `CWE-180` (Validate Before Canonicalize) map directly to `«guard» → «transform» → «follower»` crossings (`Meaning × Artifact State`). |


#### References

[1] NIST, *AI 100-2e2025*. https://doi.org/10.6028/NIST.AI.100-2e2025  
[2] NIST, *AI RMF 1.0*. https://airc.nist.gov/airmf-resources/airmf/5-sec-core/  
[3] IBM, *AI Risk Atlas*. https://www.ibm.com/docs/en/watsonx/w-and-w/2.4.x?topic=ai-risk-atlas  
[4] MITRE, *ATLAS*. https://atlas.mitre.org/  
[5] MITRE, *D3FEND*. https://d3fend.mitre.org/  
[6] Cloud Security Alliance, *MAESTRO*. https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro  
[7] Microsoft, *STRIDE threat modeling*. https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats