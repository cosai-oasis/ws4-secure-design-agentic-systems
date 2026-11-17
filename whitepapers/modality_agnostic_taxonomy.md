# A Modality-Independent Taxonomy for Multimodal Agentic Security

## OASIS Open Project: [Coalition for Secure AI (CoSAI)](https://github.com/cosai-oasis) Workstream 4 — Secure Design of Agentic Systems

## Additional artifacts: None

## Status: Working Draft

## Abstract

AI agents increasingly process images, audio, video, and structured data alongside text, introducing security risks that extend beyond individual inputs to their processing, transformation, and interaction across modalities. Existing security approaches remain largely modality-specific: techniques developed for text do not consistently generalize, research findings are difficult to compare, and defenses designed for individual input surfaces may fail to address vulnerabilities that span multiple modalities. These limitations point to a common problem: treating modality, rather than the underlying failure mechanism, as the unit of security analysis.

This whitepaper introduces a modality-agnostic taxonomy that classifies attacks by their underlying failure mechanisms. Each mechanism is defined by a three-part tuple, `⟨Invariant, Divergence, Representation⟩`, capturing the security property that is violated, why the violation is not detected or prevented, and the payload representation at the point where a security check could have been applied. Because these dimensions are independent of modality, the taxonomy provides a common framework for comparing attacks, assessing defensive coverage, extending security analyses to emerging modalities, and identifying vulnerabilities arising from cross-modal interactions.

The taxonomy is demonstrated through five independently disclosed real-world attacks spanning voice agents, IDE and enterprise tooling, physical robotics, and cross-modal composition. Its potential predictive value is further illustrated by analytically deriving a previously undocumented streaming-text attack scenario from the failure mechanism of a documented video attack. Together, these examples illustrate how mechanism-based analysis can reveal common security failures across modalities and help identify potential vulnerabilities beyond the contexts in which they were originally observed.

## Target Audience

This paper is written for practitioners who design, secure, or evaluate AI agents that process more than one modality:

- **Security architects and engineers** designing threat models and safeguards for multimodal agents, who need to evaluate whether defenses address underlying failure mechanisms rather than threats specific to individual input modalities.
- **AI red teamers and security researchers** studying prompt injection, jailbreaks, and adversarial perturbations, who need a shared vocabulary for comparing findings across modalities and existing taxonomies.
- **Practitioners already fluent in STRIDE, MITRE ATLAS/D3FEND/CWE, OWASP LLM Top 10, or CSA MAESTRO**, who want to extend that reasoning to multimodal pipelines without learning an unrelated mental model (Section 1.2 maps the taxonomy against each of these frameworks).
- **CoSAI/OASIS working-group members and standards contributors** reviewing, critiquing, or building on this workstream deliverable.


## 1. Introduction

### 1.1 Motivation
Modern AI agents increasingly operate beyond text, processing images, audio, video, and structured data. ChatGPT, Gemini, and Microsoft Copilot already support multiple modalities, while systems such as Google's Project Astra and Project Mariner, Anthropic's Claude computer use, and Gemini Robotics extend multimodal processing to applications, browsers, and physical environments.

As agents support more modalities, their attack surfaces expand. Attackers can exploit not only input content but also how information is processed, transformed, combined across modalities, or rendered downstream. Examples include:

- **Image preprocessing.** Trail of Bits (Morozova & Hussain, 2025) demonstrated an end-to-end attack against Google Gemini CLI in which an uploaded image looked benign at original resolution, revealed an injected prompt only after downscaling, and exfiltrated Google Calendar entries through auto-approved Zapier MCP tool calls.
- **Audio perception.** AudioHijack (Chen et al., 2026) demonstrated that reverberation-disguised audio perturbations imperceptible to human listeners can steer audio-language voice agents into unauthorized actions.
- **Output rendering.** In Cursor (`CVE-2025-54132`; GitHub, 2025) and M365 Copilot EchoLeak (`CVE-2025-32711`; National Vulnerability Database, 2025a), prompt injection induced the model to emit active Markdown or Mermaid markup whose preview renderer automatically fetched attacker-controlled URLs, exfiltrating sensitive context before user action.
- **Cross-modal composition.** NVIDIA's AI Red Team (Teixeira, 2026) demonstrated three-modal prompt injection against a multimodal model using jointly optimized image and audio assets alongside text. The adversarial behavior emerged only when all three modalities were present simultaneously — no single modality or pair triggered the attack, and per-modality input guardrails blocked none of the payloads. With M modalities, per-channel defenses inspect M of the 2^M - 1 non-empty subsets; the gap is the space an attacker can hide in.

The research demonstrations discussed above establish the feasibility of these attacks. While evidence of large-scale exploitation in production remains limited, the lack of documented incidents should not be mistaken for an absence of risk. As multimodal agents become more widely deployed, these attack mechanisms could translate into real-world incidents. Organizations therefore need a proactive approach to agentic security that explicitly addresses multimodal threats rather than waiting for extensive incident data to emerge. However, security teams seeking to implement such an approach face several key challenges, outlined below.
 
 - **Limited coverage of existing defenses.** Most guardrails, input filters, and red-teaming techniques were designed for text-based systems. Their effectiveness against attacks delivered through images, audio, and video remains less established, making it difficult to assess whether existing protections are sufficient.

- **Fragmented security research.** Attacks involving different modalities are often studied independently, using distinct terminology and evaluation methods. This makes it difficult to compare findings, identify shared weaknesses, and apply insights across modalities.

- **Poor scalability of modality-specific defenses.** Each new modality introduces potential attack paths that require assessment and mitigation. Treating modalities as separate security problems increases the effort needed to secure agents and can lead to duplicated work.

- **Cross-modal vulnerabilities.** Some attacks exploit interactions between modalities rather than weaknesses in individual inputs. Testing modalities independently can miss these attacks, while systematic methods for evaluating cross-modal failures remain limited.

These challenges share a root cause: they stem from treating the modality as the unit of security analysis. Yet attacks across modalities often rely on the same underlying mechanism. Image-scaling and audio-resampling attacks, for example, both exploit the gap between the input an attacker supplies and what the model receives after preprocessing. The modality differs; the failure is the same.

Organizing threats by mechanism rather than by modality helps address each challenge. Teams can evaluate whether a defense covers a mechanism, not just a single input type. Research from separate communities can be compared using a shared vocabulary. When a new modality is added, existing analysis carries over instead of starting from scratch. And because interactions between modalities can themselves be mechanisms, cross-modal failures fall within the same analysis.

**Together, these observations call for a modality-agnostic taxonomy of multimodal agent threats.**

Section 1.2 reviews existing frameworks, taxonomies, and current practices, and applies the frameworks to one attack. Section 1.3 presents the paper's core contributions: the taxonomy and the method for applying it.

### 1.2 Ecosystem Positioning

The taxonomy this paper proposes is not a replacement for existing security frameworks; it is a complementary layer that adds a mechanism-based lens that those frameworks do not provide. A team keeps its STRIDE threat model, its MITRE ATLAS technique mapping, or its CoSAI Risk Map coverage, and uses this taxonomy alongside them to classify *why* an attack works at the level of the processing pipeline, independent of the modality carrying it.

Before proposing a new taxonomy, we reviewed whether existing security frameworks already analyze multimodal threats in a modality-agnostic, mechanism-based way. We examined STRIDE, MITRE ATLAS, MITRE D3FEND, MITRE CWE, NIST AI 100-2, NIST AI RMF 1.0, the IBM AI Risk Atlas, the OWASP Top 10 for LLM Applications, CSA MAESTRO, and the CoSAI Risk Map. Each serves its purpose well, organizing threats by hazard, attacker technique, weakness, risk, or architectural layer, or organizing defenses by defensive technique. The walkthrough below applies them to one attack, and Appendix A compares them in detail.

**What existing frameworks see in one attack.** Consider the Trail of Bits disclosure from Section 1.1. A developer uploads an image to Gemini CLI that looks benign at full resolution. Before the model sees it, the system downscales the image, and the resizing reveals a hidden instruction. The model follows the instruction and sends the developer's Google Calendar entries to the attacker through a Zapier tool call that was approved automatically (**Figure 1**).

```mermaid
flowchart LR
    IMG["📷 Uploaded Image<br/><i>looks benign at full res</i>"]:::src
    DEV["👤 Developer<br/><i>views full-res image</i>"]:::guard
    DSC["🔻 Downscaler<br/><i>resizes before the model</i>"]:::xform
    LLM["🤖 CLI Model<br/><i>follows hidden instruction</i>"]:::follower
    CAL[("📅 Google Calendar<br/><i>(private data)</i>")]:::store
    MCP["⚡ Zapier Tool<br/><i>calls run without confirmation</i>"]:::executor
    EXT["🌐 External Host<br/><i>(attacker-controlled)</i>"]:::receiver

    IMG -- "ordinary-looking image" --> DEV
    DEV -- "approved upload" --> DSC
    DSC -- "① hidden text appears<br/>after resizing" --> LLM
    CAL -- "calendar entries" --> LLM
    LLM -- "② tool call<br/>(auto-approved)" --> MCP
    MCP -- "③ calendar entries<br/>sent to attacker" --> EXT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef store fill:#f3e8ff,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef receiver fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
```

*Figure 1. The Trail of Bits / Gemini CLI attack. The developer approves the image at full resolution, but the model reads the downscaled version. Each numbered step can be fixed independently: ① the downscaler reveals hidden instructions, ② the model triggers a tool call that runs without confirmation, and ③ calendar data reaches an attacker-controlled host. Figure 1c shows the same attack labeled with the taxonomy's mechanism tuples.*

The table below shows what each framework tells a security team about the Trail of Bits attack, and what it leaves out (full crosswalk in **Appendix A, Table A.1**):

| Framework | What it tells you about this attack | What it doesn't tell you |
| :---- | :---- | :---- |
| **STRIDE** | The outcomes: Tampering, Information Disclosure, and possibly Elevation of Privilege | What separates this attack from any other with the same outcomes, or that it involves three separately fixable steps: the downscaling, the auto-approved tool call, and the unrestricted data transfer |
| **MITRE ATLAS** | The techniques: indirect prompt injection (`AML.T0051.001`) and exfiltration through an agent tool (`AML.T0086`), including instructions hidden in images | Which resizing step reveals the payload, or how the image the attacker sent differs from the one the model read |
| **MITRE D3FEND** | Candidate defenses: file content analysis and outbound traffic filtering | Whether file analysis must run before or after the downscaler. If it runs before, it inspects the benign-looking original. |
| **MITRE CWE** | The weakness: improper neutralization of prompt input (`CWE-1427`) and validating before transforming (`CWE-180`) | How these weaknesses apply to images and to transforms such as resizing, OCR, or speech recognition |
| **NIST AI 100-2** | The attack class and attacker capability: indirect prompt injection through an external resource the attacker controls | How resizing changes what is visible, or the stage where hidden content becomes actionable |
| **NIST AI RMF 1.0** | Risk-management guidance: where to measure and manage this kind of risk (`MEASURE 2.7`, `MANAGE 1.3`) | The attack mechanism itself, the image transformation involved, or the pipeline stage where it activates |
| **IBM AI Risk Atlas** | The risk categories: Prompt Injection Attack and Indirect Instructions Attack, including tool-confidentiality risk | A way to separate this image-resizing attack from other indirect-injection attacks, since it has no field for transformation-dependent activation |
| **OWASP LLM Top 10** | The risks: prompt injection (`LLM01`), including a multimodal scenario, and excessive agency (`LLM06`) for the auto-approved tool | The pipeline step where the hidden instruction becomes readable. `LLM01` also covers attacks that need very different fixes. |
| **CSA MAESTRO** | The affected layers (data operations, foundation model, agent framework) and how the attack spreads across them | Which component within those layers failed. The downscaler is not a layer. |
| **CoSAI Risk Map** | The risk (prompt injection, including multimodal) and the affected components, from input handling to tools | The downscaler as a distinct component between input handling and the model |

Together, these frameworks name the attack, its consequences, and candidate defenses.

**Existing taxonomies.** We also reviewed recent taxonomies of multimodal and agentic attacks, along with MITRE's CAPEC catalog. Each covers part of what is needed (the security assumption an attack violates, the form the payload takes, or where in the pipeline it activates), and each can be used alongside the taxonomy this paper proposes:

- **PIAtlas** (Damianakis & Psounis, 2026) classifies prompt injections by how their wording influences the model, treating modality, rendering, and perturbation as delivery details. The two complement each other: PIAtlas describes how a payload persuades the model once it arrives, and this paper's taxonomy describes the path the payload took to get there.
- **Attack Atlas** (Rawat et al., 2024) and the **CSA research note on image-based prompt injection** (Cloud Security Alliance, 2026) order payload forms, from plain text to hidden or perturbed content, within text and images respectively. This paper extends that ordering to every modality (Section 3.4.1).
- **Farhana & Roy** (2026) classify image and document attacks by carrier, pipeline location, objective, and stealth. Their pipeline-location axis is the closest to this paper's approach, but their scheme is organized around the carrier, while this paper organizes around the security assumption that breaks.
- **Jain, Arık & Thakur** (2026) organize attacks on multimodal models by objective and identify modality-specific input processing as a root cause. This paper formalizes that root cause as a transformation that changes the input between when it is checked and when it is used (Section 3.2.2).
- **Shi et al.** (2025) trace agent vulnerabilities to a mismatch between dynamic trust and static authorization, a precedent for how this paper treats authority (Section 3.1.2).
- **Maloyan & Namiot** (2026) catalog attacks on coding agents, with modality as a primary axis, so each new input surface needs a new branch.
- **MLCommons Jailbreak Attack Taxonomy** (Maple et al., 2026) classifies single-turn, text-only jailbreak prompts into a closed Family > Category > Leaf hierarchy (18 leaves across Perturbation, Encoding Abuse, Overt Carriers, and Composition & Ordering), organized by the dominant prompt-manipulation strategy and validated against empirical prevalence in a large attack corpus. Its scope is narrower by design — single-turn, prompt-only, text-only, and explicitly excluding indirect prompt injection — and its "mechanism" axis corresponds to this paper's Representation (Section 3.4): its Encoding Abuse and Composition & Ordering families are closely related to this paper's *Encoded/Obfuscated* form and *Fragmented/Distributed* and *Sequence-Dependent* modifiers. It has no equivalent of this paper's Invariant or Divergence axes, so it does not classify why a check misses an attack or what security property breaks, and a team red-teaming direct, text-only jailbreaks can use its leaf catalog for prompt coverage alongside this paper's taxonomy for the pipeline-level mechanism.
- **CAPEC View 1000** (*Mechanisms of Attack*; MITRE, 2026) is the closest existing modality-agnostic mechanism hierarchy, but it is organized by attacker action and does not cover failures of machine perception.

**Appendix A, Table A.4** compares the multimodal and agentic-attack taxonomies in detail; CAPEC View 1000's relationship to the mechanism hierarchy as a whole is covered separately in **Table A.3**.

**Current practice.** Security teams today rely on two approaches, neither of which captures how multimodal pipelines actually fail:

1. **Coarse-grained STRIDE threat modeling.** Standard application threat models draw trust boundaries around whole services or around "the AI model" as a single opaque box. Inside an inference pipeline, however, security-critical transformations happen *between* components that sit inside the same traditional trust zone: a guardrail inspects a full-resolution image before a downscaler resizes it for the model, or a human reviewer previews an HTML draft whose embedded image tags trigger outbound network fetches before approval.
2. **Per-surface guardrails.** Guided by technique- and risk-level catalogs, engineering teams add defenses one input surface at a time: a text prompt filter on chat inputs, an image classifier on file uploads, an audio check on voice lines. Each guardrail checks its own channel as received, so it cannot see changes introduced by preprocessing or effects that arise when channels combine.

**What is missing.** Across the frameworks, taxonomies, and practices reviewed as of October 2026, no existing approach does all three at once, for any modality: classify attacks by the security assumption they violate, describe the form the payload takes, and record the pipeline step where the attack activates. In the Trail of Bits attack, none captures that the developer and the model saw different versions of the same image, that the attack activated at the downscaler, or that the same pattern predicts an audio attack through a resampler. Schemes that treat modality as a delivery detail cannot isolate the preprocessing step where a payload activates, and schemes organized by modality or carrier need a new branch for every new input surface. Section 1.3 introduces a taxonomy built to fill this gap.

### 1.3 Core Contributions

**This paper argues that multimodal agent attacks, whatever modality carries them, come down to a small set of failure mechanisms, each determined by how the processing pipeline is built.** In the Trail of Bits attack, the developer inspected the image at one resolution while the model read it at another. The same mismatch recurs when a guardrail scans a text stream chunk by chunk while the model reads the assembled stream, and when a video moderation model checks a sample of frames while viewers see every frame. As a testable prediction, it should also recur when an audio front end downsamples a recording through an aliasing resampler before speech recognition. The modality differs in each case, but the broken assumption is the same: two parts of the system that are assumed to see the same input do not.

**The approach.** The paper describes each mechanism by answering three questions (Section 3):

- *What security property breaks?* For example, whether two components agree on what an input says, or whether an action was authorized by the right party.
- *Why do two parts of the system disagree?* For example, because a transformation changed the input between when it was checked and when it was used.
- *What form does the payload take?* The form ranges from plainly readable text, through hidden or encoded content, to perturbations tuned to a specific model.

The three answers form a mechanism tuple, `⟨Invariant, Divergence, Representation⟩`. This paper defines the tuple and the taxonomy it produces.

**Contributions.** Compared with the frameworks and taxonomies reviewed in Section 1.2, this paper contributes:

1. **A modality-agnostic taxonomy of attack mechanisms.** Each category combines the security property that breaks with the reason two parts of the system disagree. Combinations with no known case yet are left open rather than ruled out, so a new case extends the taxonomy without restructuring it. Perception models, guard models, and human reviewers are treated as evaluators that can disagree, alongside parsers and other software components (Sections 3.1–3.3).
2. **A shared vocabulary that reuses existing security literature where it already fits.** The Invariant × Divergence Table names each mechanism and aligns it with a CWE, OWASP, or NIST identifier where one exists, so a team does not need to learn an entirely new mental model for a multimodal finding (Section 3.3).
3. **Prediction across modalities.** Because the tuple never names a modality, a mechanism classified on one input surface becomes a concrete, testable prediction for any other surface with the same structural shape — demonstrated directly in this paper by predicting an undocumented streaming-text attack from a documented video attack (Section 3.5.5).
4. **A worked account of what transfers and what does not when a fix moves across modalities.** The diagnosis and the shape of a remedy transfer with the mechanism; the modality-specific implementation of a check does not (Section 4, use case 2).
5. **Five uses the classification is put to in practice.** Triaging a disclosure, choosing where a fix belongs, reviewing an architecture before it ships, sharing a finding without disclosing proprietary architecture, and auditing existing defenses for coverage gaps (Section 4).

## 2. Scope and Key Terms

### 2.1 Scope

This paper covers security failures that occur at inference time in AI agents that process one or more modalities. It applies whether an agent uses a unified, fragmented, or hybrid architecture (Section 2.3). A failure is in scope when it can be described as a mechanism: a security property that breaks, the reason two parts of the system disagree, and the form the payload takes (Section 2.3). The number and type of modalities involved do not matter. Each entry in the Invariant × Divergence Table (Section 3.3) is included only where a documented attack or research demonstration supports it.

In scope:

* Adversarially constructed inputs presented at inference time, including text, image, audio, video, structured data, tool responses, and composite artifacts.
* Adversarially constructed outputs, including covert exfiltration channels and outputs that become active when rendered or consumed downstream.
* Prompt and control-flow injection, perception manipulation, filter bypass, attacks that activate only after a transformation, parser differentials, adversarial examples, and resource amplification.
* Agentic contexts where model-derived decisions influence tools, external communication, files, APIs, financial operations, or physical actions.
* Data produced by adversarial means, including attacks that leave training data untouched.

### 2.2 Anti-Scope

* Training-dataset poisoning, parameter backdoors, and model-weight compromise.
* Long-term retrieval poisoning and persistent memory poisoning (deferred until this inference-time taxonomy is more established; Section 5 notes retrieval poisoning as the most natural near-term extension).
* Provenance spoofing, identity impersonation, and replay attacks as standalone families.
* Side-channel and timing attacks that leak information through observed processing behavior (response latency, token-by-token streaming timing, resource consumption patterns); conventional side-channel analysis already covers these.
* A new impact or severity taxonomy. The paper instead attaches an existing STRIDE category to each Invariant it breaks (Appendix A).
* Model-safety failures that arise from benign data, signals, or outputs.
* Infrastructure-operator access to plaintext prompts, context, or outputs during inference (e.g., a cloud operator reading unencrypted inference memory); confidential-compute and hardware-attestation frameworks cover this.

### 2.3 Key Terms and Terminology

The following terms are used throughout the paper.

**Modalities**

- **Modality.** A category of information an AI system represents or processes, such as text, images, audio, or video (Baltrušaitis et al., 2019). Structured data (JSON, CSV, API responses) and composite sources (PDFs, web pages, GUIs, tool responses) can carry one or several modalities.
- **Unimodal.** A system is unimodal at a given component or interface when only one modality crosses it. A screenshot containing written instructions is image input.
- **Multimodal.** A system is multimodal at a given component or interface when two or more modalities are processed together. The same screenshot sent with a separate text question is multimodal input.
- **Cross-modal.** Describes something that happens *between* modalities. The term has two senses:
  - *Cross-modal operation:* converting or relating information across modalities, such as captioning an image or retrieving images with text (Baltrušaitis et al., 2019).
  - *Cross-modal attack:* an attack whose effect depends on inputs from two or more modalities together, as in cross-modal prompt injection (Wang et al., 2025). Sections 3.4.2 and 3.4.3 distinguish attacks whose pieces are incomplete fragments that must be reassembled from attacks in which complete artifacts produce the effect only when paired.
- **Modality surface.** A specific input or output channel through which a single modality enters or leaves the system, for example a file-upload endpoint that accepts images, a telephony channel that carries audio, or a staff HTML preview that renders rich output (part of the system's attack surface; Manadhata & Wing, 2011).
- **Cross-modality-surface prediction.** Taking a mechanism found on one modality surface and checking whether the same structural failure can occur on a different surface, demonstrated directly in Section 3.5.5. Unlike a cross-modal attack, the prediction concerns separate surfaces, not inputs combined in a single interaction. This is an instance of the general security practice of variant analysis (GitHub, n.d.) — using one known bug to find its siblings — applied across modalities rather than across source files.

**Architectures**

- **Unified architecture.** Several modalities are integrated in one model (e.g., GPT-4o; OpenAI, 2024). Unified models still sit behind modality-specific encoders and preprocessing.
- **Fragmented architecture.** Specialized components are chained together, for example separate speech recognition, language, and speech generation models.
- **Hybrid architecture.** A system that combines unified and fragmented components.
- **AI agent.** A system that adds orchestration on top of models: it uses them to pursue goals through tools, APIs, applications, or other agents. An agent may run on any of the architectures above.

**Analysis**

- **Mechanism.** A reusable explanation of why an attack works, independent of the modality that carries it. Each mechanism is described by the security property that breaks, the reason two parts of the system disagree, and the form the payload takes, written as the tuple `⟨Invariant, Divergence, Representation⟩` (Section 3). A mechanism can be located on the data-flow diagrams practitioners already draw for STRIDE threat modeling (Shostack, 2014), as Section 4's architecture-review use case shows.

Modality, architecture, and orchestration vary independently, and security outcomes depend on how information moves between components. This is why the taxonomy classifies mechanisms by this structure rather than by modality or architecture (Section 3).

## 3. Defining a Mechanism

### 3.0 Taxonomy Overview

Every mechanism is classified as a three-part tuple -  **`M = ⟨Invariant, Divergence, Representation⟩`**, where M represents the word Mechanism. Each answering three specific questions as shown in Figure 1b.
1. **Invariant**: What broke?
2. **Divergence**: Why didn't the system catch it?
3. **Representation**: What did the attack payload look like? 

```mermaid
%%{init: {"theme": "base", "flowchart": {"nodeSpacing": 40, "rankSpacing": 60, "htmlLabels": true}, "themeVariables": {"fontSize": "18px"}}}%%
flowchart TD
    ROOT["<b>M = ⟨Invariant, Divergence, Representation⟩</b><br/>Mechanism Tuple"]

    ROOT --> INV["<b>Invariant</b><br/>What security property breaks"]
    ROOT --> DIV["<b>Divergence</b><br/>Why two evaluations disagree"]
    ROOT --> REP["<b>Representation</b><br/>How the payload travels"]

    INV --> ME["<b>Meaning</b><br/>Semantic Integrity"]
    INV --> AU["<b>Authority</b><br/>Entitlement to act"]
    INV --> CO["<b>Confidentiality</b><br/>Secret confinement"]
    INV --> CS["<b>Cost</b><br/>Resource bounding"]

    DIV --> EV["<b>Evaluator</b><br/>Same artifact, two readers"]
    DIV --> AS["<b>Artifact State</b><br/>Transform changes content"]
    DIV --> TI["<b>Time</b><br/>State drifts t → t+Δ"]
    DIV --> PO["<b>Position</b><br/>Level not allowed at component"]

    REP --> FORMS["<b>Primary Forms</b>"]
    REP --> MODS["<b>Modifiers</b>"]
    REP --> COMP["<b>Composition-Dependent</b>"]

    FORMS --> OS["Overt Semantic"]
    FORMS --> EO["Encoded / Obfuscated"]
    FORMS --> ST["Steganographic"]
    FORMS --> AP["Adversarial Perturbation"]

    MODS --> FR["Fragmented / Distributed"]
    MODS --> SD["Sequence-Dependent"]

    COMP --> CC["Cross-channel"]
    COMP --> IA["Intra-artifact"]

    classDef root fill:#f0ede8,stroke:#1c1917,stroke-width:2px,color:#1c1917
    classDef branch fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#1c1917
    classDef meaning fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#1e3a5f
    classDef authority fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef confid fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef cost fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef divergence fill:#f0f9ff,stroke:#0891b2,stroke-width:1.5px,color:#164e63
    classDef rep fill:#f8fafc,stroke:#64748b,stroke-width:1px,color:#1c1917

    class ROOT root
    class INV,DIV,REP branch
    class ME meaning
    class AU authority
    class CO confid
    class CS cost
    class EV,AS,TI,PO divergence
    class FORMS,MODS,COMP,OS,EO,ST,AP,FR,SD,CC,IA rep
```

*Figure 1b. The taxonomy hierarchy. Each mechanism is classified by three components: Invariant (what breaks), Divergence (why), and Representation (how the payload travels). Sections 3.1–3.4 define each node; Section 3.3 lists the subclasses.*

As shown in Figure 1b, the invariant can take four possible values: Meaning (everyone reads the input the same way), Authority (only the right party decides what the AI does), Confidentiality (secrets reach only those allowed to see them), and Cost (processing stays within its limits). The divergence can take four possible values: Evaluator (two readers looked at the same input and saw different things), Artifact State (what was checked is not what the AI received), Time (the input was fine when approved but changed before it was used), and Position (information was read correctly but accepted where it is not allowed). The representation takes one of four primary forms: Overt Semantic (the payload is plainly readable), Encoded/Obfuscated (a disguised but decodable symbol stream), Steganographic (hidden in a sub-channel an ordinary reading skips), and Adversarial Perturbation (looks benign; only a specific model responds to it).

There are several possible combinations of Invariant, Divergence, and Representation, each describing a distinct mechanism. Because none of the three parts of the tuple depend on modality, a mechanism found on one modality can recur on another — which is how a single mechanism can explain structurally similar attacks across different input surfaces.

To understand it better, let's walk through one of the documented trail of bits example.

#### Worked Example: Trail of Bits / Gemini CLI

To see the tuple in action before the detailed definitions, consider the Trail of Bits disclosure against Google Gemini CLI (Morozova & Hussain, 2025). A developer uses Gemini CLI with a Zapier MCP server configured with `trust=True` (tool calls execute automatically). The model can read the developer's Google Calendar, and the CLI downscales every uploaded image before the model sees it.

An attacker publishes an image that looks ordinary at full resolution. Specific pixels are arranged so that after the CLI's aliasing downscaler shrinks the image, legible text appears — instructions to read the calendar and send it to an external address. The developer views the image, sees nothing suspicious, uploads it, and the model exfiltrates their calendar. Three things went wrong (**Figure 1c**):

```mermaid
flowchart LR
    IMG["📷 Uploaded Image<br/><i>looks benign at full res</i>"]:::src
    DEV["👤 Developer<br/><i>views full-res image</i>"]:::guard
    DSC["🔻 Aliasing Downscaler<br/><i>hidden text appears</i>"]:::xform
    LLM["🤖 CLI Model<br/><i>reads injected prompt</i>"]:::follower
    CAL[("📅 Google Calendar<br/><i>(secret)</i>")]:::store
    MCP["⚡ Zapier MCP<br/><i>trust=True, no confirmation</i>"]:::executor
    EXT["🌐 External Host<br/><i>(attacker-controlled)</i>"]:::receiver

    IMG -- "ordinary-looking image" --> DEV
    DEV -- "approved upload" --> DSC
    DSC -- "① Meaning × Artifact State<br/>Steganographic → Overt Semantic" --> LLM
    CAL -- "secret calendar data" --> LLM
    LLM -- "② Authority × Position<br/>tool call (auto-approved)" --> MCP
    MCP -- "③ Confidentiality × Position<br/>calendar entries exfiltrated" --> EXT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef store fill:#f3e8ff,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef receiver fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
```

*Figure 1c. Trail of Bits / Gemini CLI attack chain. The three numbered edges correspond to the three mechanism tuples in the table below: ① the downscaler reveals hidden instructions, ② the model drives an auto-approved tool call, and ③ calendar data reaches an attacker-controlled host. Figure 1 shows the same attack in plain terms.*

The taxonomy classifies mechanisms, not attacks. A single attack is usually a chain of several mechanisms, and each one gets its own tuple — so the table below has three rows, not one, even though it describes one disclosure.

| Step | What Happened | Mechanism Tuple |
| :---- | :---- | :---- |
| **1. Downscaler reveals hidden text** | The developer and the model see different content because the downscaler changes the artifact between check and use. Hidden pixels become legible instructions. | `⟨Meaning, Artifact State, Steganographic → Overt Semantic⟩` |
| **2. Model calls a tool** | The injected instructions drive a tool call reserved for the authenticated user. `trust=True` skips confirmation. | `⟨Authority, Position, Overt Semantic⟩` |
| **3. Calendar data exfiltrated** | The tool sends secret calendar entries to the attacker's host. No outbound recipient restriction exists. | `⟨Confidentiality, Position, Overt Semantic⟩` |



Now that the tuple has been shown in action, the rest of Section 3 defines each of its three parts in turn — starting with the invariant.

### 3.1 Invariants

**Formal definition.** An **invariant** is a security property the system relies on as information is read, transformed, passed between components, and acted on. It breaks when adversarial input makes that property fail at a component whose consequential behavior depends on it. There are four invariants, and each applies in any modality (classical precedents are in Section 3.3.1). Each subsection below gives the definition, why it matters for multimodal agents, its subclasses, grouped by the divergence each one pairs with (defined in the **Invariant × Divergence Table**, Section 3.3), and an example in plain terms.

**In simple words.** An invariant is a safety promise the system must always keep. A successful attack breaks one of these promises, so the invariant answers the question *"What went wrong?"* There are four, shown below; Sections 3.1.1–3.1.4 each give a worked example of the promise it names being broken (**Figure 1d**):

```mermaid
flowchart TD
    ROOT["<b>Invariant</b><br/>The safety promise a successful attack breaks"]

    ROOT --> ME["<b>Meaning</b><br/><i>Semantic Integrity</i><br/>Everyone reads the input the same way"]
    ROOT --> AU["<b>Authority</b><br/>Only the right party decides what the AI does"]
    ROOT --> CO["<b>Confidentiality</b><br/>Secrets reach only those allowed to see them"]
    ROOT --> CS["<b>Cost</b><br/><i>Resource Bounding</i><br/>Processing stays within its limits"]

    classDef root fill:#f0ede8,stroke:#1c1917,stroke-width:2px,color:#1c1917
    classDef meaning fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#1e3a5f
    classDef authority fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef confid fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef cost fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f

    class ROOT root
    class ME meaning
    class AU authority
    class CO confid
    class CS cost
```

*Figure 1d. The four invariants. Meaning, Authority, and Confidentiality govern whether information and control flow correctly between parties; Cost governs whether processing stays within its resource budget. An attack is in scope only when a consequential component's behavior depends on the broken promise (Section 3.0).*

Invariants matter for two reasons:

* **They say what is at stake.** A label such as "prompt injection" does not say whether money was lost, a secret leaked, or a service stalled. The invariant does.
* **They separate security failures from ordinary errors.** If the AI misreads a receipt and nothing acts on it, that is a quality defect. It becomes a security failure only when something consequential depends on the promise: a payment, a message sent, a tool run.

None of the promises mentions text, images, or audio. Whether an attack arrives as a picture, a voice, or a video, the broken promise has the same name, which is what lets a finding in one modality inform another. 

An invariant says *what* broke, not *why the system missed it* (the divergence, Section 3.2) or *what the attack looked like* (the representation, Section 3.4).


#### 3.1.1 Meaning (*Semantic Integrity*)

*Meaning* holds when every component that reads an artifact—whether a human reviewer, security guard, parser, or AI model—interprets it consistently wherever an important decision depends on that interpretation. A Meaning failure occurs when different components understand the same input differently, and that disagreement affects a decision or action.

*Example* The Trail of Bits disclosure involving Google Gemini CLI shows this problem clearly. An attacker uploads an image that looks completely ordinary at full resolution. The developer examines it and approves the upload. However, the CLI automatically shrinks uploaded images before passing them to the model. The attacker crafted the image so that resizing it reveals hidden instructions that were not visible to the developer.

```mermaid
flowchart LR
    IMG["📷 Uploaded Image<br/><i>one file</i>"]:::src

    DEV["👤 Developer<br/><i>views full resolution</i>"]:::guard
    OUT1["💬 'looks ordinary'<br/><i>approves the upload</i>"]:::guard

    DSC["🔻 Downscaler<br/><i>shrinks the image</i>"]:::xform
    LLM["🤖 Model<br/><i>reads the shrunk version</i>"]:::follower
    OUT2["⚠️ Hidden instruction<br/><i>reads calendar, send to attacker</i>"]:::follower

    IMG --> DEV --> OUT1
    IMG --> DSC --> LLM --> OUT2

    OUT1 -. "disagree" .- OUT2

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1e. The Meaning failure in the Trail of Bits case. The same uploaded image produces two different interpretations. The developer sees an ordinary image at full resolution, while the model receives a resized version that reveals hidden instructions. The failure occurs because the two interpretations disagree, allowing instructions that were not apparent during review to influence the model's behavior.*

As shown in Figure 1e, the developer and the model process the same image but interpret it differently. The developer sees an ordinary picture, while the model encounters hidden instructions attempting to access calendar information and send it to an attacker.

*Why it matters:* This problem is not limited to humans and AI models. Any two components, such as a security checker and a model, a parser and a model, or two software systems, can interpret the same input differently. A security check can only reliably protect a decision if its interpretation matches what the component making that decision will actually encounter. This becomes especially important in multimodal systems, where image resizing, OCR, speech recognition, and other processing steps can change how information is interpreted.

#### 3.1.2 Authority

*Authority* means having permission to direct an important action. It holds when only authorized sources can direct actions, while untrusted content can provide information but cannot issue commands. An Authority failure occurs when instructions from an untrusted source are treated as if they came from someone with permission to direct the action.

*Example* The Trail of Bits disclosure involving Google Gemini CLI also demonstrates an Authority failure. After the image is resized and its hidden instructions become visible to the model (Section 3.1.1), those instructions tell the model to use a tool to send calendar information to an external address. Although the developer never requested this action, the CLI's Zapier connection is configured with trust=True, allowing the tool call to execute automatically without asking for confirmation.

```mermaid
flowchart LR
    OUT2["⚠️ Hidden instruction<br/><i>reads calendar, send to attacker</i>"]:::follower
    DEV["👤 Developer<br/><i>holds real permission,<br/>never asked for this</i>"]:::guard
    MCP["⚡ Zapier Tool<br/><i>trust=True, no confirmation</i>"]:::executor
    ACT["💸 Tool call<br/><i>executes</i>"]:::executor2

    OUT2 -- "directs the call" --> MCP
    DEV -. "no approval requested" .-> MCP
    MCP --> ACT

    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef executor2 fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
```
*Figure 1f. The Authority failure in the Trail of Bits case. The developer has legitimate permission to use the tool but never requested this particular action. Instead, hidden instructions embedded in an untrusted image direct the model to make the tool call. Because the Zapier connection is configured with trust=True, the action executes without an additional confirmation step, allowing untrusted content to influence how legitimate tool permissions are used.*

The problem is not that the model has access to the tool. The problem is that an instruction hidden inside an image is treated as a reason to use that access. The developer authorized the system to use its tools, but did not authorize the hidden instruction to control them. This is an Authority failure: an untrusted source influences an action that should only be directed by an authorized source.

*Why it matters:* AI agents often process external information while having legitimate permission to perform actions, such as reading files, accessing calendars, or sending messages. Authority failures can occur whenever untrusted content is allowed to direct those actions, regardless of whether the content comes from an image, webpage, document, email, or another source. The combination is most dangerous when an agent simultaneously has access to private data, processes untrusted content, and can communicate externally — the "lethal trifecta" (Willison, 2025) that the Trail of Bits case exhibits exactly. This is also related to the confused deputy problem (Hardy, 1988), in which a system with legitimate permissions is manipulated into using them on behalf of an unauthorized party.

#### 3.1.3 Confidentiality

*Confidentiality* means keeping sensitive information from reaching unauthorized recipients. It holds when private data is shared only with people or systems that have permission to receive it, regardless of how the information is transmitted, such as through a response, tool call, or URL. A Confidentiality failure occurs when sensitive information reaches an unauthorized destination, even if the system originally had permission to access that information. While Authority controls which sources are allowed to direct actions, Confidentiality controls where sensitive information is allowed to go (Biba, 1977; Bell & LaPadula, 1976; Denning, 1976).

*Example* The Trail of Bits disclosure involving Google Gemini CLI also demonstrates a Confidentiality failure. After the hidden instructions cause the model to make an unauthorized Zapier tool call (Section 3.1.2), the tool sends the developer's Google Calendar entries to an attacker-controlled external host. Although the assistant has legitimate access to the calendar, the attacker is not authorized to receive its contents.

```mermaid
flowchart LR
    ACT["💸 Tool call<br/><i>executes</i>"]:::executor
    CAL[("📅 Google Calendar<br/><i>secret to the developer</i>")]:::store
    EXT["🌐 External Host<br/><i>attacker-controlled</i>"]:::receiver

    CAL -- "calendar entries" --> ACT
    ACT -- "no recipient restriction" --> EXT

    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef store fill:#f3e8ff,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef receiver fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
```

*Figure 1g. The Confidentiality failure in the Trail of Bits case. The tool call from Section 3.1.2 transfers the developer's Google Calendar entries to an attacker-controlled external host. Although the assistant has permission to access the calendar, the information is sent to a recipient who is not authorized to receive it. The failure occurs because the system does not prevent sensitive data from leaving through an unauthorized output channel.*

The problem is not that the assistant reads the calendar. Accessing the calendar is part of its legitimate functionality. The problem is that the information is sent to an external destination without the developer's authorization. This is a Confidentiality failure: the system is allowed to access sensitive information but fails to keep that information from reaching an unauthorized recipient.

Why it matters: Systems that handle sensitive information must control not only who can access that information but also where it can be sent. Confidentiality failures can occur through many output channels, including tool calls, generated responses, external URLs, emails, or other data transfers. This is especially important for AI agents that can access private information and communicate with external services, because legitimate access to data does not automatically mean permission to disclose it.

#### 3.1.4 Cost (*Resource Bounding*)

*Cost* means keeping the resources needed to process an input within acceptable limits. It holds when a system processes requests without exceeding the time, memory, computing power, inference, or tool usage allowed for them. A Cost failure occurs when an input causes the system to consume more resources than permitted, potentially slowing down the service, increasing expenses, or preventing other requests from being processed. Cost is therefore an availability property focused on the resources consumed by each input.

*Example*: Imagine a service that accepts video uploads smaller than 10 MB because it assumes small files will be inexpensive to process. An attacker uploads a 5 MB video that passes the size check. However, when the system decodes the video, it expands into hours of high-resolution frames, requiring much more processing time and memory than expected. As a result, the service becomes occupied for hours processing a file that initially appeared harmless.

```mermaid
flowchart LR
    VID["🎞️ 5 MB Video<br/><i>passes the size check</i>"]:::src
    ADM["✅ Admission Check<br/><i>estimates cost from size</i>"]:::guard
    DEC["🔻 Decoder<br/><i>expands into hours of<br/>high-res frames</i>"]:::xform
    SVC["⚙️ Service<br/><i>tied up for hours</i>"]:::follower

    VID --> ADM -- "admitted: looks cheap" --> DEC --> SVC

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1h.* The Cost failure in the video-decoding case. A 5 MB video passes the admission check because its file size is below the permitted limit. However, decoding reveals a much larger processing workload than the system anticipated. The failure occurs because the system accepts the input based on its compressed size without ensuring that the resources required to process it will remain within the allowed limits.

The problem is not that the system accepts a small video. The problem is that the file requires far more resources to process than its size suggests. The admission check considers how much storage space the file occupies, but not how much work is needed to decode and process it. This is a Cost failure: an input passes the initial checks but causes the system to exceed its permitted resource limits during processing.

The same problem can occur with text-based requests. For example, a simple instruction such as "Summarize every email since 2015" may appear inexpensive because the request itself is short. However, completing it could require retrieving, reading, and processing thousands of emails, potentially consuming hours of execution time and substantial AI inference and tool resources. If this workload exceeds the system's allowed limits, it represents another Cost failure.

*Why it matters:* Systems often decide whether to accept an input before knowing how expensive it will be to process. A file-size limit or a short request may suggest low cost, but the actual workload depends on what the input contains and what processing it triggers. Cost failures can arise from the input's structure, such as a small compressed image that expands into gigapixel dimensions, or from the work it requests, such as "Check every invoice since 2019." As discussed in Section 3.4.4, both can cause resource consumption to exceed the limits intended for an individual request.

### 3.2 Divergences

**In simple words.** Every safety check relies on two things agreeing, usually *what the check saw* and *what the AI acted on*. A divergence is the way those two things ended up different. The invariant answers *"What went wrong?"*; the divergence answers *"Why didn't the system catch it?"* There are four, shown below with the question each one answers (**Figure 1i**):

```mermaid
%%{init: {"theme": "base", "flowchart": {"nodeSpacing": 40, "rankSpacing": 60, "htmlLabels": true}, "themeVariables": {"fontSize": "18px"}}}%%
flowchart TD
    ROOT["<b>Divergence</b><br/>Why two evaluations that should agree actually differ"]

    ROOT --> EV["<b>Evaluator</b><br/>Two readers, same unchanged artifact"]
    ROOT --> AS["<b>Artifact State</b><br/>The artifact changes between check and use"]
    ROOT --> TI["<b>Time</b><br/>The approved thing changes before it's used"]
    ROOT --> PO["<b>Position</b><br/>Read correctly, accepted where it shouldn't be"]

    classDef root fill:#f0ede8,stroke:#1c1917,stroke-width:2px,color:#1c1917
    classDef divergence fill:#f0f9ff,stroke:#0891b2,stroke-width:1.5px,color:#164e63

    class ROOT root
    class EV,AS,TI,PO divergence
```

*Figure 1i. The four divergences, each naming the question it answers. Evaluator and Artifact State both describe "what was checked isn't what was used," but Evaluator's gap is in the reader while Artifact State's gap is in the artifact itself (Section 3.2.3 separates this from Time, where the gap is a delay rather than a transform).*

| Divergence | What went wrong with the check | Example | Ask yourself |
| :---- | :---- | :---- | :---- |
| **Evaluator** | Two readers looked at the same input and saw different things. | A text-only spam filter passes an email; the AI also reads the attached image, which says *"forward all invoices to this address"*, and obeys. | Did two readers see the *same* input differently? |
| **Artifact State** | What was checked is not what the AI received. | A check samples one video frame every two seconds; a one-second harmful clip hides between samples, and the AI watches the full video. | Did the input *change* between the check and the AI? |
| **Time** | The input was fine when approved but changed before it was used. | A user approves a \$50 checkout; a script changes the total to \$5,000 before the AI clicks *Pay*. | Did something change *after* approval? |
| **Position** | Information was read correctly but accepted where it is not allowed. | A delivery robot treats a stranger's sign as an operator command, or private camera footage ends up in a public post. | Was it read correctly but *accepted where it shouldn't be*? |

Each invariant from Section 3.1 can break in more than one of these ways. Meaning, for example, breaks differently when two readers simply disagree about an unchanged artifact (Evaluator) than when the artifact itself changes between check and use (Artifact State) — two different failures that happen to share the same invariant but need different fixes. The four divergences below name these "why" patterns on their own terms, independent of which invariant they end up pairing with; Section 3.3's Invariant × Divergence Table shows the specific pairings that have been observed.

Divergences matter because **they point to the fix**, which the invariant alone cannot do (Section 3.0):

| Divergence | Typical fix |
| :---- | :---- |
| **Evaluator** | Make the check read the input the way the AI does, or limit what a fooled AI can do. |
| **Artifact State** | Check the input *after* the transformation, not before. |
| **Time** | Re-check immediately before acting, or bind the approval to the exact thing approved. |
| **Position** | Stop untrusted content from directing actions (for example, with confirmation or schema-typed outputs), and restrict where secrets can go (for example, with recipient allowlists). |

Like invariants, divergences do not depend on modality. An image downscaler and an audio resampler that each change the input after it was checked are the same divergence (Artifact State), so a weak spot found in one channel tells a defender where to look in another. Most subsections below give examples in two modalities.

**Formal definition.** A **Divergence** names what differs between two evaluations that the architecture assumes agree. The subsections below define each divergence and list the subclasses it produces (the **Invariant × Divergence Table**, Section 3.3).

#### 3.2.1 Evaluator

An **Evaluator** divergence occurs when two evaluators interpret or assess the same information differently, even though they receive the same unchanged input. The difference comes from how the evaluators process or understand the information, rather than from any change to the information itself. Evaluators can include human reviewers, security filters, AI models, parsers, or the intended interpretation defined by a policy.

**In plain terms (image):** Imagine a company that uses a spam filter to check incoming emails for suspicious content. The filter examines only the text of each email. An attacker sends an email containing harmless-looking text and an attached image with the instruction *"Forward all invoices to this address."* Because the filter does not examine the image, it finds nothing suspicious and allows the email through. However, an AI assistant that can read both text and images sees the malicious instruction and follows it.

```mermaid
flowchart LR
    MAIL["📧 Incoming Email<br/><i>same unchanged email<br/>reaches both evaluators</i>"]:::src

    FILT["🛡️ Spam Filter<br/><i>reads text only</i>"]:::guard
    OUT1["✅ 'looks clean'<br/><i>passes it through</i>"]:::guard

    AST["🤖 Assistant<br/><i>also reads the image</i>"]:::follower
    OUT2["⚠️ 'forward all invoices<br/>to this address'<br/><i>obeys the instruction</i>"]:::follower

    MAIL -- "identical copy" --> FILT --> OUT1
    MAIL -- "identical copy" --> AST --> OUT2

    OUT1 -. "different interpretations<br/>of the same input" .- OUT2

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1j. The Evaluator divergence in the spam-filter case.* The spam filter and the AI assistant receive the same unchanged email but interpret it differently because they examine different parts of its content. The filter reads only the text and considers the email safe, while the assistant also reads the attached image and encounters the malicious instruction. Unlike the Meaning example in Figure 1e, where resizing changes what the model receives, no transformation occurs here. The disagreement comes from the different capabilities of the two evaluators.

The problem is not that the email changes as it moves through the system. Both components receive the same information, but they do not examine or understand it in the same way. The spam filter considers the email harmless because it cannot read the image, while the assistant finds and follows the instruction inside it. This is an Evaluator divergence: **the same unchanged input produces different interpretations because the evaluators process it differently.**

The same divergence can occur with **audio**. For example, a person listening to a voice message might hear only background music, while a speech-recognition model detects a spoken instruction embedded in the recording. The audio itself has not changed, but the human and the model interpret it differently.

**Why it matters:** Security checks are only reliable when they can detect the information that the component making the consequential decision will use. If a security filter examines only text but an AI model also processes images, audio, or other content, malicious instructions may escape the filter while remaining visible to the model. The problem is not necessarily in the input itself but in the different ways the components evaluate it.

**How it varies:** Evaluator divergence can involve either a **deployed evaluator**, such as a human reviewer, security model, or parser actually used in the system, or an **idealized evaluator**, such as the interpretation a human would reasonably make or the behavior intended by a security policy. It can appear in several forms:

- **Guard-Model Capability:** A security filter checks an input and finds nothing suspicious, but the AI model can detect and follow malicious instructions that the filter misses. For example, a text-only filter approves an email containing an image with hidden instructions.

- **Human-Machine Perception:** A human and an AI model perceive the same information differently. For example, an attacker creates an image that looks harmless to a person but contains instructions recognizable by the model.

- **Parser / Interpreter Differential:** Two components interpret the same structured information differently. For example, an approval interface displays a payment to one account, while the component processing the underlying request interprets it as a payment to another account.

- **Semantic Stability:** A system's interpretation of a request differs from the intended meaning of its governing policy. For example, an attacker rephrases a prohibited request so that a policy evaluator incorrectly approves it, even though the underlying request remains disallowed.

- **Resource Accounting:** A system's estimate of how expensive an input will be differs from the resources actually required to process it. For example, a request passes an admission check based on file size but consumes more processing time or memory than the system's permitted limits.




#### 3.2.2 Artifact State

An **Artifact State** divergence occurs when information is transformed or combined with other inputs between the time it is checked and the time it is used. As a result, the component making a decision may receive different security-relevant information from what was originally checked. The difference comes from **how the system processes or combines the information**, rather than from the information changing later over time. Unlike a Time divergence, an Artifact State divergence can happen immediately, without any delay between the check and use (see Section 3.2.3).

**In plain terms (image):** The Trail of Bits disclosure involving Google Gemini CLI (Section 3.0, Figure 1c) demonstrates this problem. An attacker uploads an image that looks ordinary at full resolution. The developer examines the original image and approves it. However, before the AI model processes the image, the CLI automatically resizes it. This transformation reveals hidden instructions that were not visible in the original full-resolution view. The model therefore encounters instructions that the developer did not see during the initial check.

```mermaid
flowchart LR
    IMG["📷 Uploaded Image<br/><i>one file, checked once</i>"]:::src
    DSC["🔻 Downscaler<br/><i>transforms the image<br/>before model processing</i>"]:::xform
    LLM["🤖 Model<br/><i>reads the transformed version</i>"]:::follower
    DEV["👤 Developer<br/><i>checks the original<br/>before transformation</i>"]:::guard

    IMG -- "original checked" --> DEV
    IMG -- "image passed<br/>for processing" --> DSC --> LLM

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1k. The Artifact State divergence in the Trail of Bits case.* The developer checks the original image, while the AI model processes a resized version produced by the downscaler. Unlike the Evaluator divergence in Figure 1j, where both components receive the same unchanged input, this example includes a transformation between checking and use. The transformation exposes hidden instructions that were not visible during the original review. The failure occurs because the security check does not account for the version of the image that the model actually processes.

The problem is not necessarily that the developer checks the image incorrectly. The developer examines the original version, but the model receives a transformed version that reveals instructions the developer did not see. The approval therefore does not reliably establish that the version used by the model is safe. This is an Artifact State divergence: **the information used by the system differs in a security-relevant way from the information that was originally checked.**

The same divergence can occur with **video**. For example, imagine a moderation system that checks an uploaded video by examining one frame every two seconds. An attacker places a one-second clip containing harmful instructions between the sampled frames. Because the moderation system examines only selected frames, it misses the instructions and approves the video. However, an AI model that later processes the full video can encounter the instructions that the moderation check missed.

**Why it matters:** Security checks must account for the information that a system will actually process, not just the information available before processing. Operations such as image resizing, decoding, normalization, OCR, truncation, and combining multiple inputs can change or expose security-relevant content. If a check examines one version of an artifact while the model acts on another, malicious content may bypass the check. Unlike a Time divergence, where information becomes outdated or changes between checking and use, an Artifact State divergence arises from the processing pipeline itself.

**How it varies:** Artifact State divergence can occur through a transformation of a single input or through the aggregation of multiple inputs. Both fall under **Transform Consistency**, but they differ in how the security-relevant information changes.

- **Transform Consistency (single transformation):** A processing step changes, removes, or exposes information that the original check did not account for. For example, an attacker creates an image containing hidden text that becomes visible only after resizing. The original image passes review, but the transformed version reveals malicious instructions. Similar problems can occur when decoding, normalization, or truncation causes the checked content and the content used by the model to differ.

- **Transform Consistency (aggregation):** Multiple inputs are combined or processed together, producing a security-relevant result that individual checks do not capture. For example, an attacker divides a large payment into several smaller requests. Each request falls below the automatic-approval threshold and passes its individual check, but their combined amount exceeds the intended approval limit. The failure occurs because the system evaluates each request separately without accounting for their combined effect.


#### 3.2.3 Time

A **Time** divergence is a validated artifact, store, or permission grant changing state between validation (`t`) and use (`t + Δ`). The gap here requires an actual window of elapsed time in which something is edited or revoked after approval — not a transform the pipeline runs immediately, which is Artifact State (Section 3.2.2 compares the two directly); the thing that was checked and the thing that was used are the same object, just at two different moments.

*In plain terms (physical access):* a delivery robot is granted temporary access to a building's loading-dock door for one delivery run, valid for 30 minutes. The task finishes in 10 minutes, but nobody revokes the grant:

```mermaid
flowchart LR
    GRANT["🔑 Door Credential<br/><i>granted for 30 min,<br/>one delivery run</i>"]:::src
    TASK["📦 Delivery Task<br/><i>finishes in 10 min</i>"]:::guard
    DELAY(("⏱️ elapsed time<br/><i>NO transform —<br/>same credential, waits</i>")):::time
    DOOR["🚪 Loading Dock<br/><i>2 hours later</i>"]:::follower

    GRANT --> TASK --> DELAY
    DELAY -- "grant never revoked" --> DOOR

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef time fill:#f0f9ff,stroke:#0891b2,stroke-width:2px,color:#164e63
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1l. The Time divergence in the delivery-robot case. Compare to Figure 1k: there, a transform node produced a second version immediately, with no delay needed. Here, there is no transform at all — the same credential simply remains valid after a real window of elapsed time passes, and the door still opens for it long after the task that justified the access ended.*

The grant was correct when it was issued; nothing about it changed — it simply outlived the task it was issued for. The failure is that what was approved at one moment is still being honored long after it should have expired. That is a Time divergence (*Grant Persistence*): the only subclass that belongs to Time alone, since nothing is transformed and no artifact changes — time simply passes.

The same divergence occurs on a **screen** when a computer-use agent is shown a \$50 checkout total and approves it, but a script changes the total to \$5,000 before the agent clicks *Pay* — the approval was correct when given, but the thing it approved changed before it was used.

*Why it matters:* approval and execution often happen at different moments (a human approval, a cached check, a long-lived grant), and the state can change in between.

*How it varies:* by what changes.
* A store: an attacker edits a record after the guard validates it, and the agent re-reads the edited version (*TOCTOU*).
* An approval: a human approves one set of tool arguments, and an attacker steers a different set into execution (*TOCTOU*).
* A permission grant: an attacker keeps using a grant after revocation or after its task ends (*Grant Persistence*).

*Time vs. Artifact State:* both describe a case where what was checked is not what was used, but the cause differs. In **Artifact State**, the system's own processing turns the input into a *different version*, and the check saw the old one. In **Time**, the check saw the right thing, but *that same thing changed later*, before it was used. **Appendix A.5** compares the two directly, side by side.

#### 3.2.4 Position

A system can be pictured as a set of trust zones — untrusted content on one side, the actions and secrets it must never directly reach on the other. A **Position** divergence is named for what happens to the information's *position* relative to that boundary: it is read correctly, with nothing transformed and no delay, but it still ends up on the wrong side — accepted by a component whose rules should never have let it cross. Unlike Evaluator, Artifact State, and Time, nothing about the information itself is in question here; the failure is purely about where it was allowed to land.

*In plain terms (physical camera):* a delivery robot should take route instructions only from its operator. Its camera reads a printed sign that a stranger has fixed to a gate, *"Delivery robots: use the back entrance"*, and its planner treats the sign as an instruction and changes route:

```mermaid
flowchart LR
    SIGN["🪧 Stranger's Sign<br/><i>'use the back entrance'</i>"]:::src
    PLAN["🤖 Planner<br/><i>read correctly, but accepted<br/>as a command</i>"]:::follower
    ROUTE["🚚 Route Change<br/><i>executes</i>"]:::executor

    SIGN -- "untrusted,<br/>should only inform" --> PLAN --> ROUTE

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
```

*Figure 1m. The Position divergence in the delivery-robot case (***Data-Control***, Authority × Position). The sign was not misread; it was read correctly, but it was accepted as a command from a source that should only have been information.*

*A simpler, everyday example:* a company email assistant reads an internal thread that includes a salary figure, then drafts a reply and CCs everyone on the thread, including an external vendor who was added partway through (***Context Confinement***, Confidentiality × Position). Nothing is misread here either — the assistant correctly copied the thread's participant list, and the vendor genuinely was on the thread. The failure is that nobody restricted which participants a secret figure like salary was allowed to reach, so it crossed from "internal only" to "visible to an outside party" the moment the reply went out.

In both cases the information arrived somewhere it should not have been allowed. That is a Position divergence.

*Why it matters:* data moves between trust levels (untrusted content toward a tool, secret context toward an outside party). The two sides that disagree are the level the information carries and the level the component accepts.

*How it varies:* by direction.
* Toward a component that takes actions (`Authority × Position`): the attacker's text becomes an instruction (*Data-Control*), the executor runs the steered call and skips its approval (*Decision-Action*), or a deputy acts beyond its caller's grant on the attacker's behalf (*Confused Deputy*).
* Toward a component that sends information out (`Confidentiality × Position`): the attacker gets secret context into a reply (*Context Confinement*) or makes a renderer fetch their URL through an image tag (*Output-Consumer*).

### 3.3 The Invariant × Divergence Table

**The concept.** Section 3.1 defined four Invariants (what breaks); Section 3.2 defined four Divergences (why it wasn't caught). Pairing them gives 16 possible combinations. This section names the combinations actually observed in real, documented attacks and research demonstrations, plus two further pairs where no disclosure has been documented yet but the mechanism is already demonstrated elsewhere in this paper or named by an existing framework — 9 of the 16 pairs have a named entry so far, and the table lists 15 entries in total, because some pairs hold more than one. A pair holds more than one entry when the attacks that land in it, despite sharing the same invariant and the same divergence, still need different defenses from each other. In Meaning × Evaluator, for example, a guard that simply cannot read images (*Guard-Model Capability*) and two parsers that read the same request differently (*Parser / Interpreter Differential*) break the same invariant for the same reason, but one is fixed by giving the guard the right perceptual capability and the other by reconciling how the two parsers interpret structured input — different fixes, so the pair holds two separate entries rather than one.

**Why this matters.** The table turns the tuple from a classification method into a shared vocabulary: instead of describing a finding as a raw tuple every time, a team can name it — "this is a *Transform Consistency* issue" — and know that any other team using this taxonomy means the same structural thing by that name, even on a completely different system. Several entries also connect directly to decades of existing security literature: *TOCTOU* is the classical time-of-check-to-time-of-use problem (`CWE-367`); *Confused Deputy* is the confused deputy (Hardy, 1988). A security engineer does not need to learn an entirely new mental model — they can map a new multimodal finding onto reasoning they likely already have. The remaining empty pairs are not gaps to ignore; they are not claimed to be impossible, and they mark the most promising places to look for a genuinely new finding, since the list is a starting point rather than a finished catalog.

**Why not just use CWE.** Eight of the fifteen entries in the table already cite a CWE identifier, which raises a fair question: if CWE already names several of these weaknesses, what does this table add? The answer is the structure CWE does not have. CWE is a flat catalog — each weakness is described on its own, with no field linking `CWE-180` (Validate Before Canonicalize) to `CWE-367` (TOCTOU) as two ways the same underlying property can fail. This table's two axes make that link explicit and load-bearing: both entries are classified as `Meaning`, which is why a team can tell at a glance that they threaten the same thing (two parts of a system disagreeing on content) even though the `Divergence` column also tells them they need different fixes — one by moving a check past a transform, the other by re-checking immediately before use. CWE has no equivalent to either axis on its own, and three of this table's entries — *Guard-Model Capability*, *Semantic Stability*, and *Context Confinement* — have no CWE match at all, because CWE was built to catalog software weaknesses, not mismatches in machine perception between a human, a guard model, and the model acting on an input, which is a distinctly agentic problem. CWE also carries an implicit modality in most of its entries, written with code, text, or network packets in mind; it has no mechanism for taking a weakness observed on one input channel and asking whether the identical pattern exists on an unrelated channel, which is exactly what Section 3.5.5 demonstrates. Where CWE already has the right identifier, this table reuses it rather than renaming it — the goal is not to replace CWE, but to organize a layer above it that CWE's flat structure cannot express.

| Entry | Invariant | Divergence | Definition | Existing Framework Alignment |
| :---- | :---- | :---- | :---- | :---- |
| *Human-Machine Perception* | Meaning | Evaluator | A person and a machine perceive the same artifact differently, so a safeguard that relies on human review fails. | `CWE-451` |
| *Guard-Model Capability* | Meaning | Evaluator | A protective check cannot perceive content that the model acts on. | No direct match found |
| *Parser / Interpreter Differential* | Meaning | Evaluator | Two parsers or interpreters read the same input differently. | `CWE-436` |
| *Semantic Stability* | Meaning | Evaluator | Inputs with the same meaning receive different decisions, judged against what the policy intends. This includes rephrased requests and conflicts between modalities. | No direct match found |
| *Transform Consistency* | Meaning | Artifact State | A transformation, or the combination of several inputs, changes or exposes content after it was checked. | `CWE-180` |
| *TOCTOU* | Meaning | Time | An input or stored state changes between when it is checked and when it is used. | `CWE-367` |
| *Grant Persistence* | Authority | Time | A permission stays usable after it expires, is revoked, or its task ends. | `CWE-613` |
| *Data-Control* | Authority | Position | Untrusted content is treated as an instruction. | `OWASP LLM01:2025` |
| *Decision-Action* | Authority | Position | A tool runs a model-requested operation without the authorization that operation requires. | `NIST SP 800-53 AC-3` |
| *Confused Deputy* | Authority | Position | A component acting on another's behalf exceeds the authority it was given. | `NIST SP 800-53 AC-6` |
| *Context Confinement* | Confidentiality | Position | Secret context, or data the model has memorized (Carlini et al., 2021, 2023), reaches a recipient not allowed to receive it. | No direct match found |
| *Output-Consumer* | Confidentiality | Position | Generated output makes a downstream renderer or client release data to parties not allowed to receive it, for example by fetching an external URL. | `OWASP LLM05:2025`; `CWE-1426` |
| *Resource Accounting* | Cost | Evaluator | An input, or the work it induces, consumes more compute, memory, inference, or tool execution than allowed for it. | `CWE-400` |
| *Decompression Amplification* | Cost | Artifact State | A decoding or decompression step expands an admitted artifact into a far larger processing workload than the pre-transform check measured. | `CWE-405`; `CWE-409` |
| *Budget Delegation* | Cost | Position | A resource budget correctly enforced at one trust level is inherited, unchecked, by a nested or delegated context with no comparable limit of its own. | `OWASP LLM10:2025` |

*The Invariant × Divergence Table. The fifteen named entries, with the invariant and divergence each one combines, and whether an existing framework already names the same pattern. Entries marked "No direct match found" appear to be genuinely new categories, without a close equivalent in the frameworks reviewed as of October 2026.*

Thirteen of these entries are each grounded in an independently documented disclosure or research demonstration, several of which are worked through in full in Section 3.5. *Decompression Amplification* and *Budget Delegation* are the two exceptions: no independent disclosure anchors them, but the mechanism itself is already demonstrated elsewhere in this paper — Section 3.4.4's PNG-decoding example is a direct instance of *Decompression Amplification* — or is already named as a risk by an existing framework, as *Budget Delegation* is by OWASP's Unbounded Consumption category. Both are included because the mechanism is structurally identical to an already-accepted entry (*Transform Consistency* and *Confused Deputy*, respectively) for a different invariant, not because a new case was found; a documented disclosure that fits either would strengthen it to the same evidentiary footing as the other thirteen.

Invariant × Divergence pairs that do not appear in this table had no matching case among the attacks reviewed through October 2026. They are not claimed to be impossible; a case that fits one would add an entry.

#### 3.3.1 Classical Security and Safety Precedents

The table's "Existing Framework Alignment" column pointed to specific identifiers; this section says more about how each one fits, and compares the table against the older, non-AI-specific security and safety literature that several of its entries draw on directly — distinct from Section 1.2's comparison against existing *AI* security frameworks and taxonomies.

Most subclasses in the table have direct classical ancestors, and naming them lets practitioners reuse established reasoning (**Appendix A, Table A.3**). *TOCTOU* is time-of-check to time-of-use (`CWE-367`). *Parser / Interpreter Differential* is the parser differential of language-theoretic security (Momot et al., 2016; `CWE-436`). *Transform Consistency* extends validate-before-canonicalize (`CWE-180`), which applies directly to a check that runs before a transform and a consequential component that acts on the transform's output, and network intrusion-detection insertion and evasion (Ptacek & Newsham, 1998), in which a monitor and an end host reassemble the same packets differently; the streaming-text attack derived in Section 3.5.5 is that structure at chunk boundaries. *Confused Deputy* is the confused deputy (Hardy, 1988), *Decision-Action* is a failure of complete mediation (Saltzer & Schroeder, 1975), and the `Authority` and `Confidentiality` invariants are the integrity and confidentiality directions of the information-flow lattice (Denning, 1976). CAPEC View 1000 (*Mechanisms of Attack*) is the closest existing modality-agnostic mechanism hierarchy; its categories are organized by attacker action, and the machine-perception subclasses of the table are additions to it.

Against these precedents, two aspects of the contributions listed in **Section 1.3** are new:

* **The classification combines two independent questions** (contribution 1). Each subclass pairs the invariant that breaks with what differs between two evaluations assumed to agree. Combinations with no known case are left open, so a new case extends the Invariant × Divergence Table without changing its structure.
* **Perception models, guard models, and human reviewers are evaluators** (contribution 1). Treating them alongside parsers brings *Human-Machine Perception*, *Guard-Model Capability*, and *Semantic Stability* into the same classification as the classical differentials.

### 3.4 Representation

**In simple words.** The invariant says what broke, and the divergence says why the system missed it. The representation answers a third question: *"What did the attack look like at the point a check could have seen it?"* For Meaning, Authority, and Confidentiality mechanisms, that question is answered by one of four primary forms, optionally qualified by a modifier (a condition on how one payload was delivered) or further classified as a composite dependency (when the effect only emerges from several separate, complete artifacts combining); for Cost mechanisms, it is answered instead by a resource-amplification characteristic (**Figure 1n**):

```mermaid
%%{init: {"theme": "base", "flowchart": {"nodeSpacing": 50, "rankSpacing": 70, "htmlLabels": true}, "themeVariables": {"fontSize": "15px"}}}%%
flowchart TD
    ROOT["<b>Representation</b><br/>What the payload looks like<br/>at the point a check could see it"]

    ROOT -- "for Meaning, Authority,<br/>Confidentiality" --> FORMS["<b>Primary Forms</b><br/>(Section 3.4.1)"]
    ROOT -- "optional, one payload" --> MODS["<b>Modifiers</b><br/>(Section 3.4.2)"]
    ROOT -- "multiple complete artifacts" --> COMP["<b>Composition-Dependent</b><br/>(Section 3.4.3)"]
    ROOT -- "for Cost only" --> AMP["<b>Resource-Amplification<br/>Characteristics</b><br/>(Section 3.4.4)"]

    FORMS --> OS["<b>Overt Semantic</b><br/>Plainly readable"]
    FORMS --> EO["<b>Encoded / Obfuscated</b><br/>Disguised but decodable"]
    FORMS --> ST["<b>Steganographic</b><br/>Hidden in a skipped sub-channel"]
    FORMS --> AP["<b>Adversarial Perturbation</b><br/>Only a specific model responds"]

    MODS --> FR["Fragmented / Distributed"]
    MODS --> SD["Sequence-Dependent"]

    COMP --> CC["Cross-channel<br/><i>separate artifacts,<br/>separate checks</i>"]
    COMP --> IAF["Intra-artifact<br/><i>one file, separately-checkable<br/>components</i>"]

    AMP --> IA["Intrinsic Amplification<br/><i>the artifact's structure</i>"]
    AMP --> SA["Semantic Amplification<br/><i>the work it induces</i>"]

    classDef root fill:#f0ede8,stroke:#1c1917,stroke-width:2px,color:#1c1917
    classDef branch fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#1c1917
    classDef rep fill:#f8fafc,stroke:#94a3b8,stroke-width:1px,color:#334155
    classDef cost fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f

    class ROOT root
    class FORMS,MODS,COMP branch
    class AMP cost
    class OS,EO,ST,AP,FR,SD,CC,IAF rep
    class IA,SA cost
```

*Figure 1n. Representation's four branches. Primary Forms, Modifiers, and Composition-Dependent describe the payload for Meaning, Authority, and Confidentiality mechanisms — Modifiers cover a condition on how one payload is delivered, while Composition-Dependent covers an effect that only emerges once several separate, complete artifacts combine, whether those artifacts arrive through separate channels (Cross-channel) or as separately-checkable components bundled in one file (Intra-artifact). Resource-Amplification Characteristics is the parallel vocabulary used only for Cost mechanisms, since "how visible is this payload" does not apply to a decompression bomb the way it applies to hidden text.*

The four representation forms are ordered by how visible the payload is: Overt Semantic is plainly readable, Encoded/Obfuscated requires decoding, Steganographic hides in a sub-channel an ordinary reading skips, and Adversarial Perturbation is imperceptible to any ordinary reader at all. A payload's form can change as it crosses a transform (Section 3.2.2) — the same content can be Steganographic before a downscaler and Overt Semantic after it.

Section 3.4.1 (**Table 2**) defines each form in full, with cross-modal examples.

*Why it's needed.* Representation tells a defender *what a check would have to perceive to catch the attack*, which the invariant and divergence cannot. Two attacks can share the same invariant and divergence and still need different defenses because of what the payload looks like: plainly visible text can be caught by a filter that reads the right modality, but an adversarial perturbation cannot be reliably detected by any filter and instead calls for containment — limiting what the model is allowed to do (Section 3.0's screenshot-vs-audio example).

None of the four forms mentions a modality. Plaintext in a chat message, legible text in an image, and a clear spoken command are all **Overt Semantic**; a Base64 string and a QR code are both **Encoded / Obfuscated**, whether carried by text or image. The form names what the payload looks like at a given point in the pipeline, not what channel carries it, so a representation seen in one modality tells a defender what to look for in another.

Representation is the third and last part of the mechanism tuple: the invariant names the harm, the divergence names the weak spot, and the representation names what a defense could perceive (Section 3.0).

**Formal definition.** **Representation** describes how adversarial information or influence is embodied in an artifact and becomes interpretable at a specified processing boundary. It records properties of the artifact at the specific state being examined; how the attacker built it is recorded separately.

#### 3.4.1 Primary Forms

A **primary form** is how adversarial content appears to an upstream guard or ordinary human observer. The four forms build on encoding, obfuscation, steganography (e.g., imperceptible Unicode perturbations in text; Boucher et al., 2022), and adversarial evasion, and they are ordered by what that observer perceives (**Table 2**).

*Why it matters:* a guard or reviewer catches only what it perceives, and a payload's form can change as it moves through the pipeline.

| Representation Form | What an Upstream Guard or Ordinary Reader Perceives | Cross-Modal Examples |
| :---- | :---- | :---- |
| **Overt Semantic** | Adversarial content is readable through ordinary interpretation at the observation point. | Plaintext prompt; legible typographic text in an image; clear spoken command. |
| **Encoded / Obfuscated** | Perceives the symbol stream, which is concealed through encoding, symbolic substitution, or obfuscation recoverable using known conventions. | Base64, hex, or URL-encoded text; HTML entities; substitution cipher; QR code; DTMF tones. |
| **Steganographic** | Perceives an ordinary carrier; adversarial information sits in a sub-channel that ordinary reading skips. | Zero-width or Unicode tag characters; white-on-white or off-page PDF text; sparse pixels sampled by an aliasing downscaler; near-ultrasonic audio. |
| **Adversarial Perturbation** (termed *adversarial examples* in NIST AI 100-2e2025) | Perceives benign content; the effect triggers through internal features of a specific target model. | Gradient-optimized token suffixes (GCG; Zou et al., 2023); adversarial visual patches; reverberation-blended audio perturbations (AudioHijack). |

*Table 2. Primary representation forms and cross-modal examples.*

*How it varies:* by artifact state, so representation is classified at each one (Quiring et al., 2020). The Trail of Bits disclosure against Google Gemini CLI (Section 3.0, Figure 1c) shows this directly: the developer's image is `Steganographic` at the point the developer checks it, since the hidden pixels sit in a sub-channel an ordinary viewer skips. The CLI's aliasing downscaler then shrinks it, and injected text appears to the model:

```mermaid
flowchart LR
    IMG["📷 Uploaded Image<br/><i>looks benign at full size</i>"]:::src
    DEV["👤 Developer<br/><i>checks it</i>"]:::guard
    OUT1["✅ Steganographic<br/><i>hidden pixels, skipped</i>"]:::guard

    DSC["🔻 Aliasing Downscaler<br/><i>shrinks the image</i>"]:::xform
    MOD["🤖 CLI Model<br/><i>reads the shrunk version</i>"]:::follower
    OUT2["⚠️ Overt Semantic<br/><i>now legible text</i>"]:::follower

    IMG --> DEV --> OUT1
    IMG --> DSC --> MOD --> OUT2

    OUT1 -. "same payload,<br/>reclassified" .- OUT2

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1o. The Trail of Bits payload's representation changing across the downscaler. The same image is `Steganographic` to the developer, who checks it before the downscaler runs, and `Overt Semantic` to the model, which only ever sees the downscaled version. The fault: the payload becomes readable only after the downscaler, past the point where the developer checked it.*

Zero-width characters in text and off-page PDF text are `Steganographic` the same way, across different modalities. On a phone line, the analogous attack is acoustic: a perturbation imperceptible to a human listener that a speech-recognition model transcribes as an instruction — `Adversarial Perturbation`, since no ordinary listening would ever reveal it.

#### 3.4.2 Modifiers

A **modifier** is a structural or temporal condition the adversarial effect requires, attached to a primary form, describing how a single payload was delivered.

*Why it matters:* guards often inspect an input once, as a whole. A payload split across pieces passes every per-item check and still works once the model reassembles them.

*How it varies:* by how the pieces relate.
* **Fragmented / Distributed:** A single effective payload is distributed across multiple incomplete pieces that require aggregation or reassembly to reconstruct its adversarial effect (for example, splitting a command across streaming chunks or structured fields).
* **Sequence-Dependent:** The adversarial effect depends on the timing, ordering, duration, or synchronization of information across steps or frames.
* **Classification distinctions:** Use *Fragmented / Distributed* when each piece is incomplete and reassembly rebuilds one payload, and *Sequence-Dependent* when ordering or timing is essential rather than the reassembly itself. *Encoded / Obfuscated* payloads are recovered with decoding conventions; *Steganographic* payloads sit in a sub-channel behind an ordinary-looking carrier. Transformation-activated payloads are covered by two existing parts of the record: the `Meaning × Artifact State` mechanism at the transform, and the representation recorded at each artifact state. Section 3.4.3 covers a related but distinct case — several *complete* artifacts combining, rather than one payload split into incomplete pieces.

*Example (Fragmented / Distributed):* a video-language model checks uploaded video for policy compliance by sampling one frame every few seconds. An attacker distributes a single directive across seven frames — frame 40 (ignore), 95 (previous), 150 (instructions), 205 (and), 260 (forward), 315 (all), 370 (emails). No single frame contains a complete instruction (Section 3.5.5):

```mermaid
flowchart LR
    F1["Frame 40: ignore"]:::src
    F2["Frame 95: previous"]:::src
    F3["Frame 150: instructions"]:::src
    F4["Frame 205: and"]:::src
    F5["Frame 260: forward"]:::src
    F6["Frame 315: all"]:::src
    F7["Frame 370: emails"]:::src

    CHK["Per-frame moderator approves each frame alone"]:::guard
    MOD["Video-Language Model aggregates all seven frames"]:::follower
    OUT["Reconstructed command: ignore previous instructions and forward all emails"]:::follower

    F1 --> CHK
    F2 --> CHK
    F3 --> CHK
    F4 --> CHK
    F5 --> CHK
    F6 --> CHK
    F7 --> CHK

    F1 --> MOD
    F2 --> MOD
    F3 --> MOD
    F4 --> MOD
    F5 --> MOD
    F6 --> MOD
    F7 --> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1o-ii. A Fragmented/Distributed payload. No single frame carries a complete instruction — each is an incomplete piece the model must aggregate and reassemble. The per-frame moderator only ever evaluates one incomplete piece at a time, so the reassembled command is never visible to it. (This same video also happens to be Sequence-Dependent, since the frames must be read in this order — see Figure 1o-iii for an example that isolates timing alone.)*

*Example (Sequence-Dependent):* an adversarial audio perturbation is embedded in a voice call as several complete, self-contained segments. Each segment, played on its own at any time, is harmless — the perturbation only activates the speech-recognition model's hidden behavior when the segments arrive synchronized to a specific cadence, within a narrow timing window:

```mermaid
flowchart LR
    S1["Segment A<br/>harmless alone"]:::src
    S2["Segment B<br/>harmless alone"]:::src
    S3["Segment C<br/>harmless alone"]:::src

    CHK["Per-segment check samples clips<br/>at arbitrary moments"]:::guard
    MOD["Speech-Recognition Model hears<br/>the synchronized cadence"]:::follower
    OUT["Hidden behavior activates<br/>only within the timing window"]:::follower

    S1 --> CHK
    S2 --> CHK
    S3 --> CHK

    S1 --> MOD
    S2 --> MOD
    S3 --> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1o-iii. A Sequence-Dependent payload with no fragmentation. Unlike Figure 1o-ii, nothing here is incomplete — each segment is a full, self-contained clip. The fault is purely in *when* the segments arrive relative to one another: a per-segment check that samples clips at arbitrary moments, with no regard for their timing, never observes the synchronized pattern the model responds to (`Adversarial Perturbation` + `Sequence-Dependent`, with no `Fragmented/Distributed` component).*

#### 3.4.3 Composition-Dependent

A **composite dependency** describes an adversarial effect that emerges only through the joint interpretation of multiple complete, self-contained artifacts — unlike a modifier, which describes a condition on how one payload was delivered, a composite dependency is a relationship between two or more separately-checkable payloads, none of which is incomplete on its own.

*Why it matters:* guards typically inspect each input on its own. A payload that stays within one artifact is visible to a per-artifact check; a payload confined to the *combination* of several artifacts is not, because no single check ever sees the combination.

*How it varies:* by where the separately-checkable pieces come from.
* **Cross-channel:** the pieces arrive as separate artifacts, through separate channels, each with its own check.
* **Intra-artifact:** the pieces are bundled inside one file, as separate components (e.g., a video's frames and its caption track), each still separately-checkable even though they travel together.

*Example (cross-channel):* An attacker sends a harmless message (*"Please apply the goodwill credit we agreed on"*) and a harmless-looking chat screenshot (*"Agent: agreed, \$25 credit to account 48213"*). Each passes review on its own:

```mermaid
flowchart LR
    MSG["💬 Text Request<br/><i>'apply the goodwill<br/>credit we agreed on'</i>"]:::src
    CHK1["✅ Checked alone<br/><i>looks harmless</i>"]:::guard

    SCRN["🖼️ Chat Screenshot<br/><i>'agreed, $25 credit<br/>to account 48213'</i>"]:::src
    CHK2["✅ Checked alone<br/><i>looks harmless</i>"]:::guard

    MOD["🤖 Model<br/><i>reads both together</i>"]:::follower
    OUT["⚠️ Credit issued<br/><i>action + target account</i>"]:::follower

    MSG --> CHK1 -.-> MOD
    SCRN --> CHK2 -.-> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1p. A cross-channel composite dependency (*Composition-Dependent*). Each input arrives through its own channel and passes its own review individually — neither the text request nor the screenshot alone tells the model to issue a credit. Together, the model reads the action from one and the target account from the other, and acts on the pair.*

*Example (intra-artifact):* a single uploaded video has two separately-checkable components — its frames and its caption track. The frames, checked on their own, are benign; the caption, checked on its own, is also benign:

```mermaid
flowchart LR
    VID["🎞️ Video File<br/><i>one upload</i>"]

    FRM["📹 Video Frames<br/><i>benign on their own</i>"]:::src
    CHK1["✅ Checked alone<br/><i>looks harmless</i>"]:::guard

    CAP["💬 Caption Track<br/><i>benign on its own</i>"]:::src
    CHK2["✅ Checked alone<br/><i>looks harmless</i>"]:::guard

    MOD["🤖 Model<br/><i>reads both tracks together</i>"]:::follower
    OUT["⚠️ Malicious meaning<br/><i>emerges only from the pair</i>"]:::follower

    VID --> FRM --> CHK1 -.-> MOD
    VID --> CAP --> CHK2 -.-> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1p-ii. An intra-artifact composite dependency. The frames and the caption are bundled inside one file, but they are still two separately-checkable components — a frame check and a caption check would each pass individually. The malicious meaning exists only in their combination, which the model reads but no per-component check ever evaluates.*

Both shapes share the same mechanism and the same name (*Composition-Dependent*): the attack is confined to a combination no single check evaluates. What differs is only where the boundary between the separately-checkable pieces falls — across channels, or across components of one file.

Together they give the model the action and the target account, and it issues the credit. The fault: each input is checked alone, while the model acts on the pair.

The combinatorial surface grows with modality count. Teixeira (2026) demonstrated *three-modal prompt injection* against a multimodal model: jointly optimized image and audio assets produced adversarial behavior only when all three modalities (text, image, audio) were present simultaneously — every proper subset (each single modality and each pair) produced benign output, and per-modality input guardrails blocked none of the payloads. With M input modalities, a model reasons over 2^M - 1 non-empty subsets, but per-channel inspection covers only M of them. The *Composition-Dependent* category records this combinatorial dependency; the minimum subset that activates the effect is part of the record so that defenders know which ablation tests to run.

#### 3.4.4 Resource-Amplification Characteristics

A **resource-amplification characteristic** is how an artifact makes processing consume disproportionate resources (`Cost × Evaluator`, *Resource Accounting*), recorded in the `Representation` slot of `Cost` records.

*Why it matters:* the two kinds need different controls (limits on decoding complexity for one, execution and tool-call budgets for the other).

*How it varies:* by the source of the cost.
* **Intrinsic Amplification:** The artifact's structure or encoding alone causes disproportionate resource consumption during processing (for example, decompression bombs (`CWE-409`) and pathological media bitstreams, which require limits on decoding complexity).
* **Semantic Amplification:** The interpreted content of an artifact induces disproportionate resource consumption through system behavior (for example, long output generation, recursive agent delegation, repeated tool invocation, and uncontrolled retry loops (`ATLAS AML.T0034.002`), which require execution and tool-call budgets).

*Example:* an attacker uploads a PNG under 5 MB that decodes to gigapixel dimensions and exhausts decode memory:

```mermaid
flowchart LR
    PNG["🖼️ PNG, under 5 MB<br/><i>passes the size check</i>"]:::src
    DEC["🔻 Decoder<br/><i>expands to gigapixel<br/>dimensions</i>"]:::xform
    MEM["💥 Decode Memory<br/><i>exhausted</i>"]:::follower

    PNG --> DEC --> MEM

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1q. Intrinsic Amplification. The admitted file's own structure, not its size, is what makes it expensive — the size check never sees the gigapixel dimensions the decoder actually has to produce.*

A different kind of amplification needs no decoder at all. A request asking for a 50-paragraph policy breakdown drives generation past the inference budget:

```mermaid
flowchart LR
    REQ["Short text request<br/>passes the size check"]:::src
    MOD["Model interprets the request<br/>as asking for extensive work"]:::xform
    GEN["Generation runs past<br/>the inference budget"]:::follower

    REQ --> MOD --> GEN

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef xform fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1r. Semantic Amplification. The admitted request is small and the size check passes it easily — nothing about its structure is unusual. The cost comes entirely from the work the model interprets the request as asking for, which the size check has no way to anticipate.*

The fault in both Intrinsic and Semantic Amplification is the same: the size check at admission underestimates the real cost, because it measures the artifact's size, not what processing it will actually require.

### 3.5 Transfer to Other Domains

The tuple describes structure, not modality, so the same mechanism can appear in very different systems. The examples below classify the disclosures introduced in Section 1.1 and demonstrate cross-modality-surface prediction from one surface to another, showing that the same mechanisms recur across a voice agent, IDE and enterprise tools, a physical robot, cross-modal composition, and video-to-streaming-text transfer.

Each example below follows the same three-part structure: **Scenario** describes what the system normally does, **Exploit** describes what the attacker did, and **Fault** classifies why it actually broke, using the mechanism tuple and the Invariant × Divergence Table's named entries. Watching this same structure produce a correct, specific diagnosis across five unrelated, independently-documented disclosures is itself the evidence that the taxonomy generalizes — not just an assertion of it.

#### 3.5.1 Voice Agent: AudioHijack

*Scenario:* AudioHijack (Chen et al., 2026) is a research demonstration against audio-language voice agents — systems that accept spoken instructions from a caller, transcribe them with a speech-recognition model, and can execute actions (tool calls, transfers, account changes) on the caller's behalf. The agent trusts whatever its speech-recognition model transcribes, on the assumption that a transcription reflects what was actually said — an assumption that a broader body of work on speech-recognition security shows does not generally hold (Chen, Y. et al., 2021).

*Exploit:* the attacker adds reverberation-disguised perturbations to an audio clip — a distortion pattern layered into the clip's echo characteristics, engineered so that it is inaudible to a human listener but still shifts what the speech-recognition model's internal features respond to. A human listener hears ordinary speech; the speech-recognition model transcribes an injected command that steers the agent into an unauthorized action. The diagram below traces this: one audio clip reaches two different listeners — a human and the model — who disagree about what it says, and that disagreement, if acted on, drives a tool call:

```mermaid
flowchart LR
    CLIP["Audio clip<br/>one recording"]:::src

    LIS["Human listener<br/>hears ordinary speech"]:::guard
    OUT1["Sounds normal<br/>no concern raised"]:::guard

    ASR["Speech-recognition model<br/>transcribes the same clip"]:::follower
    OUT2["Hidden command transcribed<br/>steers the agent"]:::follower

    TOOL["Tool call<br/>executes"]:::executor

    CLIP --> LIS --> OUT1
    CLIP --> ASR --> OUT2
    OUT2 --> TOOL

    OUT1 -.disagree.- OUT2

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
```

*Figure 1s. The AudioHijack attack chain. The listener and the speech-recognition model hear the same clip and disagree about what was said — the listener hears ordinary speech, the model transcribes a hidden command. If the agent then acts on that transcription, a second fault fires when the tool executes it.*

*Fault:* this attack breaks down into two separate mechanisms, chained one after the other. Each one is classified the same way — Invariant, then Divergence, then the named entry their Invariant × Divergence Mapping points to, then Representation:

**Step 1 — the listener and the model disagree about what was said.**
1. *Invariant:* `Meaning` — the listener and the model read the same clip and come away with different content.
2. *Divergence:* `Evaluator` — nothing about the clip changed; two different readers (human ear, speech-recognition model) simply perceive it differently.
3. *Invariant × Divergence Mapping:* `Meaning × Evaluator` is named *Human-Machine Perception*, since the two disagreeing readers are a human and the model — the spam-filter case in Section 3.2.1 shares the same `Meaning × Evaluator` pair, but is named *Guard-Model Capability* instead, since there the two readers are a text-only filter and a multimodal model, not a human and a model.
4. *Representation:* `Adversarial Perturbation` — the perturbation is engineered to be imperceptible to the human ear, so no amount of careful listening reveals it.

Written as a tuple: `⟨Meaning, Evaluator, Adversarial Perturbation⟩`.

**Step 2 — if the agent then executes the transcribed command through a tool.**
1. *Invariant:* `Authority` — only the authorized caller should be able to direct the agent's actions; here, content with no verified source does.
2. *Divergence:* `Position` — the transcribed command was read correctly by this point; the fault is that it crossed into "instruction" territory a component should never have accepted it into.
3. *Invariant × Divergence Mapping:* `Authority × Position` covers *Data-Control* (untrusted content becomes an instruction) leading into *Decision-Action* (the tool runs it without the authorization that action requires) — the same pairing used for the Trail of Bits tool call in Section 3.1.2.
4. *Representation:* `Overt Semantic` — by this point the transcribed command is just plain text; nothing about it is hidden anymore.

Written as a tuple: `⟨Authority, Position, Overt Semantic⟩`.

The structural pattern in Step 1 matches the `Meaning × Evaluator` pair from the text-only filter example in Section 3.2.1 — one evaluator perceives the input one way, the model perceives it another way — but the specific named entry differs: the modality is audio instead of image, the evaluator is a human instead of a text-only filter (*Human-Machine Perception* rather than *Guard-Model Capability*), and the Representation is `Adversarial Perturbation` instead of `Overt Semantic`.

#### 3.5.2 Output Rendering: Cursor and EchoLeak

*Scenario:* an IDE agent (Cursor, `CVE-2025-54132`) or an enterprise copilot (M365 Copilot EchoLeak, `CVE-2025-32711`) processes external content — repository files, emails, or documents — and generates a response that includes active markup (Mermaid diagrams, Markdown image references).

*Exploit:* prompt injection hidden in the external content steers the model to emit markup containing an attacker-controlled URL. The client's preview renderer automatically fetches that URL on render, and the fetch request carries sensitive context (conversation data, email content) in the URL query string — before any human reviews the output:

```mermaid
flowchart LR
    DOC["External content<br/>repository file or email"]:::src
    MOD["Model generates markup<br/>containing attacker URL"]:::follower
    REND["Preview renderer<br/>fetches the URL automatically"]:::executor
    EXT["Attacker-controlled host<br/>receives the fetch, with<br/>sensitive context in the query string"]:::receiver

    DOC --> MOD --> REND --> EXT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
    classDef receiver fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
```

*Figure 1t. The Cursor/EchoLeak attack chain. Untrusted external content directs the model to emit a URL, and the renderer fetches it automatically — no human ever reviews the output before the fetch carries sensitive context out to an attacker-controlled host.*

*Fault:* this attack breaks down into two separate mechanisms, chained one after the other.

**Step 1 — untrusted external content directs the model's output.**
1. *Invariant:* `Authority` — only the user's own request should direct what the model does; here, content from an external file or email does.
2. *Divergence:* `Position` — the external content is read correctly; the fault is that it crosses into "instruction" territory a component should never have accepted it into.
3. *Invariant × Divergence Mapping:* `Authority × Position` is named *Data-Control* — the same entry used for the Trail of Bits tool call in Section 3.1.2 and the AudioHijack tool call in Section 3.5.1.
4. *Representation:* `Overt Semantic` — the injected instruction is plain text embedded in the file or email, not hidden.

Written as a tuple: `⟨Authority, Position, Overt Semantic⟩`.

**Step 2 — the renderer fetches the attacker's URL, exfiltrating context.**
1. *Invariant:* `Confidentiality` — sensitive context (conversation data, email content) should only reach parties allowed to see it.
2. *Divergence:* `Position` — the renderer fetches any URL the model emits, with no check on where that URL points or what it carries.
3. *Invariant × Divergence Mapping:* `Confidentiality × Position` is named *Output-Consumer* — generated output makes a downstream renderer release data to a party not allowed to receive it.
4. *Representation:* `Overt Semantic` — the exfiltrated data rides along in a plainly-formed URL query string, not disguised.

Written as a tuple: `⟨Confidentiality, Position, Overt Semantic⟩`.

The fix is to restrict or disable remote fetches in the renderer, which closes Step 2 regardless of what directs the model in Step 1.

#### 3.5.3 Delivery Robot: RP2 Stop-Sign Stickers

*Scenario:* a small delivery robot drives around a campus at walking speed (2 m/s). It has a camera, and it uses that camera to read street signs as it goes. Reading a sign is split into two deliberately separate steps. First, a **sign classifier** looks at whatever the camera sees and outputs exactly one label from a small, fixed list it is allowed to choose from — `STOP`, `Speed Limit 25`, `Speed Limit 45`, and so on; it can never output anything outside that list. Second, a **brake planner** — a simple, deterministic rule, not a learned model — acts on whatever label the classifier outputs: if the label is `STOP`, it halts the robot; otherwise, it doesn't. The system is built this way on purpose, so the only place real uncertainty exists is in the sign-reading step, and the action taken on that reading is as simple and predictable as possible.

*Exploit:* this is a real, published attack (Eykholt et al., 2018), the origin of "Robust Physical Perturbation" (RP2). The attacker never touches the robot or its software. Instead, they physically stick small, carefully shaped and colored stickers onto a real stop sign out in the world. The stickers are specifically engineered, using machine-learning techniques, to shift the classifier's internal calculations without changing how the sign looks to a person — a human walking by still sees the familiar red octagon and the word `STOP`, and reads it as a stop sign without a second thought. The classifier, however, doesn't "read" the sign the way a person does; it processes pixel patterns through its internal math, and the stickers are tuned to push that specific math toward the wrong answer. The result: the classifier outputs `Speed Limit 45` instead of `STOP` — and this wasn't a rare fluke. When the researchers drove past the sticker-covered sign repeatedly and recorded video, the classifier misread it as `Speed Limit 45` in 84.8% of the resulting drive-by video frames, making it a reliable, repeatable failure rather than a one-off coincidence:

```mermaid
flowchart LR
    SIGN["Stop sign<br/>with RP2 stickers"]:::src
    PERSON["Human reader<br/>reads STOP"]:::guard
    OUT1["Sign says STOP<br/>no concern"]:::guard

    CLASS["Sign classifier<br/>reads the same sign"]:::follower
    OUT2["Classified as Speed Limit 45<br/>wrong percept"]:::follower

    PLAN["Brake planner<br/>runs authorized logic on<br/>the wrong percept"]:::executor
    CROSS["Robot does not brake<br/>enters the intersection"]:::executor

    SIGN --> PERSON --> OUT1
    SIGN --> CLASS --> OUT2 --> PLAN --> CROSS

    OUT1 -.disagree.- OUT2

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef executor fill:#ede9fe,stroke:#7c3aed,stroke-width:1.5px,color:#3b0764
```

*Figure 1u. The RP2 stop-sign attack. A human and the classifier read the same physical sign and disagree about what it says. The brake planner then runs exactly the logic it is authorized to run, on a wrong percept — nothing about the robot's authority is exceeded; the harm follows purely from the mismatched perception.*

*Fault:* unlike the previous two examples, this attack is a single mechanism, not a chain.
1. *Invariant:* `Meaning` — the human reader and the classifier disagree about what the same physical sign says.
2. *Divergence:* `Evaluator` — nothing about the sign changed; two different readers (human eye, classifier) simply perceive it differently.
3. *Invariant × Divergence Mapping:* `Meaning × Evaluator` is named *Human-Machine Perception* — the same entry used for AudioHijack in Section 3.5.1.
4. *Representation:* `Adversarial Perturbation` — the RP2 stickers are engineered to be imperceptible to a human looking at the sign, while still shifting what the classifier's internal features respond to.

Written as a tuple: `⟨Meaning, Evaluator, Adversarial Perturbation⟩`.

`Authority` holds throughout: the brake planner only ever runs the logic it was already authorized to run — "halt at every `STOP` sign" — and the classifier can only emit one class from a fixed list. No untrusted content ever acquires authority it shouldn't have. The physical harm follows from the Meaning failure alone, which is what makes this example useful: it shows a Meaning failure causing real-world harm with no second, Authority-type mechanism needed at all.

#### 3.5.4 Cross-Modal Composition: NVIDIA Three-Modal Prompt Injection

*Scenario:* an application summarizes web pages for its users. A typical page can carry text, an embedded image, and an embedded audio clip all at once — think of an article with a photo and an audio player on it. The application feeds all three into one multimodal model at the same time and asks it to produce a summary (Teixeira, 2026).

*Exploit:* the attacker doesn't hide a bad instruction in any single one of these three inputs. Instead, using an optimization process — computationally searching for the right combination, the same kind of technique behind the RP2 stickers in Section 3.5.3 — they craft a specific image file (PNG) and a specific audio file (WAV) together, as a matched pair, designed to work only in combination. The image alone produces entirely normal output. The audio alone produces entirely normal output. Even the image and audio together, without the text, still produce normal output. The malicious behavior — the model producing a phishing message with a dangerous link — only emerges when all three pieces (the text, the rigged image, and the rigged audio) are present at the same time, the way a combination lock needs every part to open at once, not just some of them. All three are components of the same single page — not three separately-submitted artifacts arriving through independent channels — so this is the *Intra-artifact* flavor of Composition-Dependent (Section 3.4.3): one artifact, three separately-checkable components, bundled together. This is exactly why checking each component on its own fails: a guardrail that only looks at the page's image finds nothing wrong, because the image genuinely is harmless by itself; the same is true for the audio and the text checked individually. Only a check on the model's final output — after it has already combined all three — catches the violation:

```mermaid
flowchart LR
    PAGE["Web page<br/>one artifact"]

    TXT["Text component<br/>benign alone"]:::src
    IMG["Adversarial PNG component<br/>benign alone, per its own guard"]:::src
    AUD["Adversarial WAV component<br/>benign alone, per its own guard"]:::src

    G1["Text guard<br/>checks text only"]:::guard
    G2["Image guard<br/>checks image only"]:::guard
    G3["Audio guard<br/>checks audio only"]:::guard

    MOD["Multimodal model<br/>reasons over all three together"]:::follower
    OUT["Phishing message<br/>with malicious URL"]:::follower

    PAGE --> TXT --> G1 -.-> MOD
    PAGE --> IMG --> G2 -.-> MOD
    PAGE --> AUD --> G3 -.-> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1v. The NVIDIA three-modal attack. Text, image, and audio are three components of one page, not three separately-arriving artifacts. Each per-modality guard checks only its own component and finds nothing wrong — because nothing is wrong in any single component. The malicious effect exists only in the combination of all three, which no guard ever evaluates, but the model does.*

*Fault:* this attack breaks down into two separate mechanisms, chained one after the other.

**Step 1 — the per-component guards and the model disagree, because each guard only ever sees its own component of the page.**
1. *Invariant:* `Meaning` — the three guards conclude the input is benign; the model, reasoning over all three together, reaches a malicious reading.
2. *Divergence:* `Evaluator` — nothing about any single component changed; each guard simply never evaluates the combination the model does.
3. *Invariant × Divergence Mapping:* `Meaning × Evaluator` is named *Guard-Model Capability* — the same entry used for the spam-filter case in Section 3.2.1, here at its most extreme: each per-component guard cannot perceive what only the full, joint input reveals.
4. *Representation:* `Adversarial Perturbation`, combined with the *Composition-Dependent* category and its *Intra-artifact* variant (Section 3.4.3) — the image and audio are jointly optimized so that the malicious effect exists only in the combination of all three components of one page. With M components, a model reasons over 2^M - 1 non-empty subsets, but per-component inspection covers only M of them; the attacker confines the payload to a subset no single-component check evaluates.

Written as a tuple: `⟨Meaning, Evaluator, Adversarial Perturbation [Composition-Dependent, Intra-artifact]⟩`.

**Step 2 — if the application then acts on the phishing output.**
1. *Invariant:* `Authority` — only the user's own request should direct what the application does; here, the model's output (itself steered by the three-modal payload) does.
2. *Divergence:* `Position` — the phishing output is read correctly by this point; the fault is that it crosses into "instruction" territory — rendering a clickable URL or sending a message — that a component should never have accepted it into.
3. *Invariant × Divergence Mapping:* `Authority × Position` is named *Data-Control* — the same entry used for the Trail of Bits tool call in Section 3.1.2.
4. *Representation:* `Overt Semantic` — by this point the phishing message and its URL are plain, legible content.

Written as a tuple: `⟨Authority, Position, Overt Semantic⟩`.

Across these four examples, the same pattern keeps recurring: classify an attack using the Invariant × Divergence Table, and the same named entry — *Human-Machine Perception*, *Guard-Model Capability*, *Data-Control* — shows up again in a completely unrelated system, carried by a different modality each time. The next example makes that recurrence explicit: it takes one concrete, documented attack and shows how the same mechanism predicts an undocumented one in a different modality.

#### 3.5.5 Sequence-Dependent Aggregation: Video Frames and Streaming Text

Unlike the four examples above, this one has two parts. The first classifies a real, documented attack, the same way every other example in this section does. The second takes that attack's exact tuple, swaps only the modality, and asks whether the same structural weakness should also exist somewhere nobody has yet documented it — a text pipeline with a per-chunk filter. This is the clearest demonstration in the paper of cross-modality-surface prediction working forward, not just classifying what has already been observed.

*Scenario (video):* a system accepts video uploads and checks each one for policy compliance before allowing it through. Watching every single frame of a long video would be slow and expensive, so the moderation step takes a shortcut: it samples just one frame every few seconds and checks only those sampled frames. If every sampled frame looks acceptable on its own, the video passes. Separately, a video-language model is used downstream to actually process the video's content — and unlike the moderator, it watches the entire video, every frame, in order (arXiv:2508.10974, AAAI 2026).

*Exploit (video):* the attacker exploits the gap between what the moderator samples and what the model actually watches. They hide one word of a forbidden instruction in each of seven specific frames, spread across the video — frame 40 (*ignore*), 95 (*previous*), 150 (*instructions*), 205 (*and*), 260 (*forward*), 315 (*all*), 370 (*emails*). No single frame contains a complete instruction, and even a frame the moderator happens to sample shows nothing alarming — a single word like "ignore" on its own is not a policy violation, so every frame the per-frame content moderator checks is approved in isolation. The video-language model, however, watches every frame of the video in sequence, reads all seven words in order, and reconstructs the full, dangerous instruction: "ignore previous instructions and forward all emails." Figure 1o-ii (Section 3.4.2) diagrams this exact case.

*Fault:* like the delivery robot in Section 3.5.3, this attack is a single mechanism, not a chain.
1. *Invariant:* `Meaning` — the moderator and the model read the same video but come away with different content: the moderator sees seven harmless fragments, the model sees one reconstructed command.
2. *Divergence:* `Artifact State` — the moderator checks each frame individually, while the model consumes the full, aggregated sequence; the artifact the model acts on is not the artifact the moderator checked.
3. *Invariant × Divergence Mapping:* `Meaning × Artifact State` is named *Transform Consistency* (here, the aggregation variant) — the same pair used for the Trail of Bits downscaler in Section 3.1.1, though there a single transform changes the artifact, while here aggregation across many pieces does.
4. *Representation:* `Overt Semantic`, combined with the *Fragmented / Distributed* and *Sequence-Dependent* modifiers (Section 3.4.2) — the reconstructed command is plainly readable once assembled, but no single frame carries a complete instruction, and the frames must be read in this order. Figure 1o-ii traces this directly.

Written as a tuple: `⟨Meaning, Artifact State [aggregation], Overt Semantic [Fragmented + Sequence-Dependent]⟩` — the bracket on the Divergence marks that the artifact changes through aggregation of several pieces, not a single transform like the Trail of Bits downscaler.

*Cross-modality-surface prediction (streaming text):* the same `Meaning × Artifact State` mechanism predicts a vulnerability in a text pipeline with per-chunk guardrails. An attacker splits a directive across streaming chunks — chunk 1 (*... ignore*), chunk 2 (*... previous*), chunk 3 (*... instructions*), and so on. Each chunk passes a stateless content filter individually; the LLM's context window aggregates them into an active command:

```mermaid
flowchart LR
    C1["Chunk 1: ... ignore"]:::src
    C2["Chunk 2: ... previous"]:::src
    C3["Chunk 3: ... instructions"]:::src
    C4["Chunk 4: ... and forward all emails"]:::src

    CHK["Stateless content filter<br/>approves each chunk alone"]:::guard
    MOD["LLM context window<br/>aggregates all chunks"]:::follower
    OUT["Reconstructed command:<br/>ignore previous instructions<br/>and forward all emails"]:::follower

    C1 --> CHK
    C2 --> CHK
    C3 --> CHK
    C4 --> CHK

    C1 --> MOD
    C2 --> MOD
    C3 --> MOD
    C4 --> MOD
    MOD --> OUT

    classDef src fill:#fee2e2,stroke:#dc2626,stroke-width:1.5px,color:#7f1d1d
    classDef guard fill:#e5e7eb,stroke:#6b7280,stroke-width:1.5px,color:#1f2937
    classDef follower fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
```

*Figure 1w. The predicted streaming-text case, carrying the exact structure of Figure 1o-ii (Section 3.4.2) into a new modality. A stateless filter checks each chunk alone, exactly as the video moderator checked each frame alone; the LLM's context window aggregates every chunk, exactly as the video-language model aggregated every frame. Nobody has yet documented this specific attack — the diagram is a prediction, not a classification of an observed case.*

The classification is identical: `⟨Meaning, Artifact State [aggregation], Overt Semantic [Fragmented + Sequence-Dependent]⟩`. The modality changes from video to streaming text; the mechanism does not.

This is how the prediction actually works: holding the tuple fixed and asking which parts of a different system play the same roles. `Meaning × Artifact State [aggregation]` says the attack needs a checker that only ever sees isolated pieces and a consumer that aggregates them into something the checker never saw combined — in a text pipeline, that role pair is the stateless per-chunk filter and the LLM's full context window. `Fragmented` says no single piece may be complete, which translates directly into splitting the directive across chunks the way it was split across frames. `Sequence-Dependent` says the pieces must be read in the order they were split in, which carries over unchanged. Each part of the tuple becomes one concrete instruction for building the predicted attack, not just a note that the two cases are similar.

The fix is shared for the same reason: the guard must evaluate the same assembled artifact the model consumes, not the individual pieces, whichever modality the pieces happen to be carried in. A team that found the video attack and holds this record would generate the streaming-text test without needing a separate threat catalog entry — though until someone actually runs that test, the streaming-text case remains a prediction, not a confirmed finding: the video attack is demonstrated; the text attack is only feasible until it is tried.

This is the point of the example: a mechanism tuple can be used to proactively predict attacks in a different modality, by recognizing the same structural roles in a new system — not by transferring the original attack from one modality to another, but by constructing a new, independent attack that follows the same pattern.

The tuple itself is deliberately minimal — just enough to classify a mechanism and predict across modalities, as shown above. A real finding usually carries a few more pieces of bookkeeping (where in the pipeline it occurs, which modality it was observed on, how much the attacker needed to know) that make the record useful in practice without being part of what makes two mechanisms the same or different; **Appendix A.6** collects these.

## 4. Using This Taxonomy

The sections above define the vocabulary; this section names the uses a classified mechanism is put to in practice.

1. **Triaging a new disclosure or incident report.** Given an attack, real or hypothesized, answer the tuple's three questions in order: *what broke* (Invariant), *why didn't the system catch it* (Divergence), and *what did the payload look like at the point a check could have seen it* (Representation). The Invariant × Divergence Table names the result if the pair has a known subclass. This turns a vague label like "prompt injection" into a record that can be compared against other findings on its own terms.

2. **Deciding where a fix belongs, and finding the same weakness on other surfaces.** The Invariant alone cannot choose a defense — it says what is at stake, not where to intervene. The Divergence says where (retrain or replace the check, move it past a transform, re-check immediately before use, or restrict what untrusted content may direct); the Representation says whether a perceptual filter can catch the payload at all, or whether the only real lever is containing what a fooled component is allowed to do. Because neither answer names a modality, a classified finding also becomes a question about the rest of the system: does any other data flow have the same shape — a check, then a transform or a trust boundary, then a consequential use? Section 3.5's five worked examples (a voice agent, IDE and enterprise output rendering, a delivery robot, cross-modal composition, and video-to-streaming-text transfer) demonstrate exactly this: the same `Invariant × Divergence` pair, carried across a different modality, correctly predicts a parallel failure before it is observed.

   *Illustration.* The Trail of Bits mechanism from Section 3.0, `⟨Meaning, Artifact State, Steganographic → Overt Semantic⟩`, has a fix stated purely in terms of pipeline position: *check the input after the transformation, not before.* An audio pipeline with the same shape — a check on an uploaded clip, a resampler that downsamples it, a speech-recognition model that acts on the resampled audio — has the identical structure, so the fix transfers without translation: *move the check to run after the resampler.* What transfers is the diagnosis (this pipeline has a check-before-transform shape) and the shape of the remedy (move the check downstream); what does not transfer is the implementation of the check itself — someone still has to build an audio-aware equivalent of the image check. The taxonomy does not remove that engineering work; it removes the discovery step, by turning "where else might this bite us" into a precise, testable question instead of a fresh red-teaming effort.

3. **Reviewing an architecture before anything ships.** The four Divergence categories double as a walk-through checklist for a data-flow diagram: for each place where a check runs, ask whether anything downstream of it acts on a different version of the same artifact (Artifact State), a different reader's interpretation of it (Evaluator), a later, changed state of it (Time), or a context the check never cleared it for (Position). Finding one of these shapes at design time is cheaper than finding it after a disclosure.

4. **Sharing a finding without disclosing architecture.** Because a mechanism is described by role (a check, a transform, an evaluator) rather than by product or implementation, a team can report "we had a `⟨Confidentiality, Position, Overt Semantic⟩` finding in an output path" to a partner, customer, or standards body without revealing which model, renderer, or pipeline produced it — close to how a CVE describes a vulnerability class without exposing the vulnerable code.

5. **Auditing existing defenses for gaps.** The Invariant × Divergence Table can be read as a coverage map rather than only an attack catalog: a team can check which cells their current guardrails actually address — for example, a text-only filter covers `Meaning × Evaluator` but says nothing about `Meaning × Artifact State` — and treat the remaining cells as an explicit, prioritized gap list rather than an unknown unknown.

## 5. Conclusion

**What this paper presented.** Multimodal agent attacks are usually described by the modality that carries them, which forces security teams to rediscover the same failure for every new input surface. This paper proposed an alternative: classify the mechanism instead of the modality, using a tuple, `⟨Invariant, Divergence, Representation⟩`, that names what security property broke, why the system failed to catch it, and what the payload looked like at the point a check could have seen it. Because none of the three parts names a modality, the same tuple that classifies an image attack can predict a parallel failure on an audio, video, or text surface before it is observed — demonstrated concretely across the five worked examples in Section 3.5.

**What we learned building it.** Working through real disclosures against this structure surfaced a few things worth stating plainly. First, the Invariant alone is not enough to choose a defense — two attacks that break the same promise can still need opposite fixes, which is why the taxonomy needed a second, independent axis (Divergence) rather than one richer category. Second, several categories resisted a clean fit even after repeated revision — Cost sits awkwardly among the other three Invariants, and Position is the Divergence with the weakest claim to the "two evaluations disagree" pattern its siblings share — and we chose to leave those seams visible rather than force a tidier structure the evidence does not yet support. Third, applying the taxonomy correctly takes real judgment: several classification calls in this paper's own worked examples turned out to be wrong on first pass and needed correction against the formal definitions, which says as much about the work ahead for consistent adoption as it does about any individual mistake.

**Limitations.** Four are worth naming directly:

1. **Reducible-only classes lack per-cell control prescriptions.** The taxonomy locates *Human-Machine Perception*, *Guard-Model Capability*, and *Semantic Stability* mechanisms and explains *why* they resist deterministic closure, but the *what to do about it* question is answered only at the level of architectural strategy (context separation, as in CaMeL or FIDES; Debenedetti et al., 2025; Costa et al., 2025; or type narrowing), not per-cell defensive controls — adaptive attacks have repeatedly shown that probabilistic, filter-based defenses at these boundaries can be bypassed (Nasr et al., 2025).
2. **Cross-modality-surface prediction can over-produce.** Holding a mechanism fixed and swapping modality can generate many structurally plausible hypotheses on a real system, most of which will not be worth testing. Left unmanaged, this risks turning a diagnostic tool into a flood of low-value speculation rather than a prioritized set of findings.
3. **Classification consistency across independent users is untested.** The categories and worked examples in this paper come from a small authoring group applying the taxonomy to a bounded set of disclosures. Whether independent teams converge on the same tuple for the same finding — the premise the "shared vocabulary" claim depends on — has not yet been tested outside that group.
4. **Completeness of the classification is an open question.** The four invariants and four divergences cover all instances reviewed through October 2026, but the paper does not claim they are exhaustive. Combinations that do not appear in the Invariant × Divergence Table had no matching case; a counterexample that fits one would add a subclass, not invalidate the taxonomy.

Deferred threat families — training-time poisoning, retrieval and memory poisoning, provenance spoofing, and side-channel attacks — are out of scope by design (Section 2.2) rather than a limitation of the classification itself; retrieval poisoning is the most natural near-term extension, since a poisoned record retrieved from a store and then acted on has the same check-then-use shape as Transform Consistency and TOCTOU, just with the store standing in for the transform or the elapsed time.

## References

Ball, S., Gluch, G., Goldwasser, S., Kreuter, F., Reingold, O., & Rothblum, G. N. (2025). On the impossibility of separating intelligence from judgment: The computational intractability of filtering for AI alignment. arXiv:2507.07341. https://arxiv.org/abs/2507.07341

Baltrušaitis, T., Ahuja, C., & Morency, L.-P. (2019). Multimodal machine learning: A survey and taxonomy. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 41(2), 423–443. https://doi.org/10.1109/TPAMI.2018.2798607

Bell, D. E., & LaPadula, L. J. (1976). *Secure computer system: Unified exposition and Multics interpretation* (MTR-2997). The MITRE Corporation.

Biba, K. J. (1977). *Integrity considerations for secure computer systems* (MTR-3153). The MITRE Corporation.

Boucher, N., Shumailov, I., Anderson, R., & Papernot, N. (2022). Bad characters: Imperceptible NLP attacks. *IEEE Symposium on Security and Privacy*. https://arxiv.org/abs/2106.09898

Carlini, N., et al. (2021). Extracting training data from large language models. *30th USENIX Security Symposium*. arXiv:2012.07805. https://arxiv.org/abs/2012.07805

Carlini, N., et al. (2023). Extracting training data from diffusion models. *32nd USENIX Security Symposium*. arXiv:2301.13188. https://arxiv.org/abs/2301.13188

Chen, Wang, Lu, Zhang, & Zhang. (2026). AudioHijack. *IEEE Symposium on Security and Privacy*. arXiv:2604.14604. https://arxiv.org/abs/2604.14604

Chen, Y., Zhang, J., Yuan, X., Zhang, S., Chen, K., Wang, X., & Guo, S. (2021). SoK: A modularized approach to study the security of automatic speech recognition systems. arXiv:2103.10651. https://arxiv.org/abs/2103.10651

Cloud Security Alliance. (2026, March 8). *CSA research note: Image-based prompt injection in multimodal LLMs*. https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/

Coalition for Secure AI (CoSAI). (2026). *CoSAI Risk Map* (risks.yaml, revision of 2026-08-27). https://github.com/cosai-oasis/secure-ai-tooling/tree/main/risk-map

Costa, M., et al. (2025). Securing AI agents with information-flow control (FIDES). arXiv:2505.23643. https://arxiv.org/abs/2505.23643

Damianakis, & Psounis, K. (2026). PIAtlas. arXiv:2610.24999. https://arxiv.org/abs/2610.24999

Debenedetti, E., et al. (2025). Defeating prompt injections by design (CaMeL). arXiv:2503.18813. https://arxiv.org/abs/2503.18813

Denning, D. E. (1976). A lattice model of secure information flow. *Communications of the ACM*, 19(5), 236–243. https://doi.org/10.1145/360051.360056

Eykholt, K., Evtimov, I., Fernandes, E., Li, B., Rahmati, A., Xiao, C., Prakash, A., Kohno, T., & Song, D. (2018). Robust physical-world attacks on deep learning visual classification. *Proceedings of CVPR 2018*. https://arxiv.org/abs/1707.08945

Farhana, & Roy. (2026). Multimodal prompt injection: A formal 4D taxonomy. *IEEE QPAIN 2026*. https://doi.org/10.1109/QPAIN69676.2026.11545895

GitHub. (n.d.). *About CodeQL* (variant analysis). https://codeql.github.com/docs/codeql-overview/about-codeql/

GitHub. (2025). *Security advisory GHSA-43wj-mwcc-x93p: Cursor Mermaid remote image fetch* (`CVE-2025-54132`). https://github.com/advisories/GHSA-43wj-mwcc-x93p

Glukhov, D., Shumailov, I., Gal, Y., Papernot, N., & Papyan, V. (2023). LLM censorship: A machine learning challenge or a computer security problem? arXiv:2307.10719. https://arxiv.org/abs/2307.10719

Google. (n.d.). *Secure AI Framework (SAIF): Risks*. https://saif.google/secure-ai-framework/risks

Hardy, N. (1988). The confused deputy (or why capabilities might have been invented). *ACM SIGOPS Operating Systems Review*, 22(4), 36–38. https://doi.org/10.1145/54289.871709

Huang, K. (2025, February 6). *Agentic AI threat modeling framework: MAESTRO*. Cloud Security Alliance. https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro

IBM. (n.d.). *AI Risk Atlas*. https://www.ibm.com/docs/en/watsonx/saas?topic=ai-risk-atlas

Jain, Arık, & Thakur. (2026). Adversarial attacks on multimodal large language models. *Transactions on Machine Learning Research*. arXiv:2603.27918. https://arxiv.org/abs/2603.27918

Maloyan, N., & Namiot, D. (2026). Prompt injection attacks on agentic coding assistants. arXiv:2601.17548. https://arxiv.org/abs/2601.17548

Manadhata, P. K., & Wing, J. M. (2011). An attack surface metric. *IEEE Transactions on Software Engineering*, 37(3), 371–386. https://doi.org/10.1109/TSE.2010.60

Maple, C., et al. (2026). *A robust, defensible, and reproducible methodology for benchmarking single-turn jailbreak attacks on large language models*. MLCommons Security Initiative. https://mlcommons.org/wp-content/uploads/2026/02/MLCommons___Security___Jailbreak_0_7_Paper_Collaborative.pdf ; taxonomy at https://github.com/mlcommons/jailbreak-taxonomy

MITRE. (2026). *ATLAS: Adversarial Threat Landscape for Artificial-Intelligence Systems* (data release v2026.09). https://atlas.mitre.org/ ; https://github.com/mitre-atlas/atlas-data

MITRE. (2026). *CAPEC: Common Attack Pattern Enumeration and Classification* (version 3.9; View 1000, Mechanisms of Attack). https://capec.mitre.org/data/definitions/1000.html

MITRE. (2026). *CWE: Common Weakness Enumeration* (version 4.20). https://cwe.mitre.org/

MITRE. (2026). *D3FEND* (ontology version 1.6.0). https://d3fend.mitre.org/

Momot, F., Bratus, S., Hallberg, S. M., & Patterson, M. L. (2016). The seven turrets of Babel: A taxonomy of LangSec errors and how to expunge them. *IEEE Cybersecurity Development (SecDev)*.

Morozova, K., & Hussain, S. (2025, August 21). *Weaponizing image scaling against production AI systems*. Trail of Bits. https://blog.trailofbits.com/2025/08/21/weaponizing-image-scaling-against-production-ai-systems/

Nasr, M., et al. (2025). The attacker moves second: Stronger adaptive attacks bypass defenses against LLM jailbreaks and prompt injections. arXiv:2510.09023. https://arxiv.org/abs/2510.09023

National Institute of Standards and Technology. (2020). *Security and privacy controls for information systems and organizations* (NIST SP 800-53 Rev. 5). https://doi.org/10.6028/NIST.SP.800-53r5

National Institute of Standards and Technology. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (NIST AI 100-1). https://doi.org/10.6028/NIST.AI.100-1

National Vulnerability Database. (2025a). *CVE-2025-32711: Microsoft 365 Copilot information disclosure (EchoLeak)*. https://nvd.nist.gov/vuln/detail/CVE-2025-32711

OpenAI. (2024, May 13). *Hello GPT-4o*. https://openai.com/index/hello-gpt-4o/

OWASP Foundation. (2025). *Agentic AI – Threats and Mitigations* (version 1.0). https://genai.owasp.org/

OWASP Foundation. (2025, December 9). *OWASP Top 10 for Agentic Applications* (ASI01 Agent Goal Hijack; ASI02 Tool Misuse; ASI03 Identity & Privilege Abuse). https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/

OWASP Foundation. (2025). *OWASP Top 10 for LLM Applications 2025* (LLM01 Prompt Injection; LLM05 Improper Output Handling; LLM06 Excessive Agency). https://genai.owasp.org/llm-top-10/

Ptacek, T. H., & Newsham, T. N. (1998). *Insertion, evasion, and denial of service: Eluding network intrusion detection*. Secure Networks, Inc. https://insecure.org/stf/secnet_ids/secnet_ids.html

Quiring, E., Klein, D., Arp, D., Johns, M., & Rieck, K. (2020). Adversarial preprocessing: Understanding and preventing image-scaling attacks in machine learning. *Proceedings of the 29th USENIX Security Symposium*. https://www.usenix.org/conference/usenixsecurity20/presentation/quiring

Rawat, A., et al. (2024). Attack Atlas: A practitioner's perspective on challenges and pitfalls in red teaming GenAI. arXiv:2409.15398. https://arxiv.org/abs/2409.15398

Saltzer, J. H., & Schroeder, M. D. (1975). The protection of information in computer systems. *Proceedings of the IEEE*, 63(9), 1278–1308. https://doi.org/10.1109/PROC.1975.9939

Shi, et al. (2025). SoK: Trust–authorization mismatch in LLM agents. arXiv:2512.06914. https://arxiv.org/abs/2512.06914

Shostack, A. (2014). *Threat modeling: Designing for security*. Wiley.

Teixeira, D. (2026, September 21). *When modalities combine: The combinatorial blind spot in AI security*. NVIDIA AI Security. https://research.nvidia.com/ai-security/when-modalities-combine-combinatorial-blind-spot-ai-security

Vassilev, A., Oprea, A., Fordyce, A., Anderson, H., Davies, X., & Hamin, M. (2025). *Adversarial machine learning: A taxonomy and terminology of attacks and mitigations* (NIST AI 100-2e2025). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-2e2025

Video LLM frame-sampling omission. (2025). Failures to surface harmful contents in video LLMs. *Proceedings of AAAI 2026*. arXiv:2508.10974. https://arxiv.org/abs/2508.10974

Wang, L., et al. (2025). Manipulating multimodal agents via cross-modal prompt injection (CrossInject). *Proceedings of ACM Multimedia 2025*. https://arxiv.org/abs/2504.14348

Willison, S. (2025, June 16). *The lethal trifecta for AI agents: Private data, untrusted content, and external communication*. https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/

Xiao, Q., Chen, Y., Shen, C., Chen, Y., & Li, K. (2019). Seeing is not believing: Camouflage attacks on image scaling algorithms. *Proceedings of the 28th USENIX Security Symposium*. https://www.usenix.org/conference/usenixsecurity19/presentation/xiao

Zou, A., Wang, Z., Carlini, N., Nasr, M., Kolter, J. Z., & Fredrikson, M. (2023). Universal and transferable adversarial attacks on aligned language models (GCG). arXiv:2307.15043. https://arxiv.org/abs/2307.15043

---

## Appendix A: Framework and Standards Crosswalks

**Framework alignment notes.** The notes below expand the summary in **Section 1.2**; Tables A.1–A.4 follow.

**Adversary catalogs (MITRE ATLAS, NIST AI 100-2e2025).** ATLAS's 2026 releases describe multimodal behavior in detail: triggers placed in "a modality that is not inspected, or is inspected differently from text" (`AML.T0129`), obfuscation across images, audio, and video frames (`AML.T0068`), and content served differently to AI systems than to humans (`AML.T0134`). For the Trail of Bits disclosure, ATLAS records indirect prompt injection (`AML.T0051.001`) and exfiltration through agent tool invocation (`AML.T0086`); the three-step chain in Section 3.0 places those techniques on its three steps and names the downscaler as the activation point. ATLAS mitigation `AML.M0010` lists resampling as an input-restoration defense and notes that adaptive adversaries account for preprocessing, which this paper expresses as the conservative survival of `Adversarial Perturbation` across a transform (Section 3.4.1, **Table 2**). NIST AI 100-2e2025 provides a broader threat taxonomy organized by learning method, lifecycle phase, attacker objective, capability, and knowledge; its *resource control* capability corresponds to an untrusted input reaching a component from outside the system, and its knowledge dimension aligns with this paper's *Attacker Knowledge / Access* annotation (**Appendix A.6**).

**Hazard and risk frameworks (STRIDE, OWASP, CoSAI Risk Map, MAESTRO).** A STRIDE category attaches to each Invariant by the hazard it names: Confidentiality findings correspond to Information Disclosure, Authority findings to Elevation of Privilege, Cost findings to Denial of Service, and Meaning findings to Tampering. A STRIDE-per-element review therefore keeps its own vocabulary while gaining the finer-grained Invariant × Divergence pairs this paper locates inside a trust zone a coarse diagram would treat as one process. OWASP `LLM01:2025` (Prompt Injection), `LLM05:2025` (Improper Output Handling), and `LLM06:2025` (Excessive Agency) correspond respectively to `Data-Control` (Authority × Position), `Output-Consumer` (Confidentiality × Position), and the broader set of Authority × Position findings. The CoSAI Risk Map's component axis (Input Handling, Reasoning Core, Output Handling, Tools) is the most stage-like construct among the reviewed frameworks; this paper's taxonomy refines it to the level of an individual check, transform, or evaluator, and a mechanism record can carry the corresponding Risk Map risk identifier as a supporting annotation (**Appendix A.6**). MAESTRO's seven architectural layers locate the affected subsystem, and the Invariant × Divergence pair locates the specific mechanism within it.

**Defensive ontologies (MITRE D3FEND).** D3FEND links offensive and defensive techniques through shared digital artifacts and already defines media artifact classes (`DigitalImage`, `DigitalAudio`, `DigitalVideo`). Those classes correspond to the artifacts this paper's Representation forms describe, which makes D3FEND a strong candidate vocabulary for a future per-cell control catalog (**Section 5**, limitation 1).

### A.1 Comparative Coverage of Existing AI Security Frameworks: Trail of Bits Image-Scaling Attack

| Framework | Relevant Identifiers | What the Framework Captures Well | What the Framework Leaves Implicit | Additional Detail Provided by the Mechanism Record |
| :---- | :---- | :---- | :---- | :---- |
| **NIST AI 100-2e2025** | `NISTAML.015` (Indirect Prompt Injection); `NISTAML.039` (Compromising Connected Resources) | Classifies inference-time indirect prompt injection, attacker control over external resources, and potential integrity and confidentiality impacts. Also discusses injection hiding and obfuscation. | The image-resampling algorithm, how resizing changes payload visibility, and the processing stage where hidden content becomes actionable. | Separates the three mechanisms the attack chains together: transformation activation (`Meaning × Artifact State`), instruction authority (`Authority × Position`), and egress authorization (`Confidentiality × Position`) — Section 3.0. |
| **NIST AI RMF 1.0** | `MEASURE 2.7`; `MANAGE 1.3` | Supports risk identification, security evaluation, resilience assessment, and mitigation planning. | Attack-mechanism identifiers, image transformation, payload representation, and activation sequence. | Specifies the mechanism and pipeline point to evaluate. |
| **IBM AI Risk Atlas** | Prompt Injection Attack; Indirect Instructions Attack; Sharing IP/PI/Confidential Information with Tools | Identifies malicious instructions embedded in untrusted content, model manipulation, and confidentiality risks associated with connected tools. | Structured fields for interpolation, concealment, and transformation-dependent activation that would separate image-resizing injection from other indirect attacks. | Distinguishes pre-/post-transform content, authority takeover, and execution failure. |
| **MITRE ATLAS (v2026.09)** | `AML.T0051.001` (Indirect Prompt Injection); `AML.T0068` (LLM Prompt Obfuscation); `AML.T0086` (Exfiltration via AI Agent Tool Invocation); related: `AML.T0129` (Triggers in Multimodal Inputs), `AML.T0123` (Obfuscated Files or Information), `AML.T0134` (AI Targeted Cloaking), `AML.T0034.002` (Agentic Resource Consumption); mitigations `AML.M0010` (Input Restoration, which lists resampling) and `AML.M0036` | Describes attacker techniques, untrusted multimodal content, payload concealment, and adversarial behavior. Recognizes hidden instructions in image pixels and multimodal triggers. | A structured description of the exact resampling primitive, the differences between original and transformed representations, and the activation stage. | Links representation-state changes to distinct violated security assumptions and effect locations. |
| **MITRE D3FEND (1.6.0)** | `D3-FCOA` (File Content Analysis); `D3-FCR` (File Content Rules); `D3-OTF` (Outbound Traffic Filtering) | Provides candidate defensive techniques for inspecting files, applying content-analysis rules, and restricting unauthorized data transmission. | The offensive image-scaling mechanism and detection of instructions revealed by resizing. The listed controls are candidate defenses pending an attack-specific mapping. Version 1.6.0 imports 189 ATLAS technique classes as bare identifiers and definitions, and predates `AML.T0129`. | Locates where candidate controls should be evaluated, as candidates pending validation. |
| **MAESTRO** | `L2` (Data Operations); `L1` (Foundation Model); `L3` (Agent Frameworks); `L7` (Agent Ecosystem); related OWASP *Agentic AI – Threats and Mitigations* threats `T2` (Tool Misuse) and `T6` (Intent Breaking & Goal Manipulation) | Identifies affected architectural layers, cross-layer attack propagation, trust boundaries, and potential misuse of connected tools. | Pixel-level manipulation, the exact resampling algorithm, pre-/post-transformation semantic differences, and the precise activation condition. | Adds Representation detail and the specific Divergence, with processing stages kept separate from architectural layers. |
| **STRIDE** | `T` (Tampering); `I` (Information Disclosure); `E` (Elevation of Privilege, conditional) | Classifies security threats involving input manipulation, confidential data exposure, and potential authorization-boundary violations. | What separates image-scaling attacks from other attacks with the same security consequences, plus payload representation, transformation, and activation mechanisms. | Identifies the specific mechanisms producing those broader threat categories; each category attaches to the Invariant it breaks. |
| **OWASP `LLM01:2025`** | Prompt Injection, scenarios #6 (payload splitting), #7 (multimodal injection), #8 (adversarial suffix), #9 (multilingual or obfuscated input) | Enumerates representation variants, including instructions in images that accompany benign text, and flags cross-modal attacks as an open defense problem. | The pipeline step at which a hidden instruction becomes legible to the model. | Classifies each scenario by Invariant × Divergence and records the Representation the payload has when the model acts on it. |
| **MITRE CWE (4.20)** | `CWE-1427` (Improper Neutralization of Input Used for LLM Prompting); `CWE-180` (Validate Before Canonicalize) | States the data/directive invariant for LLM prompts directly; `CWE-180` names the check-before-transform ordering. | Non-text carriers and model-based transforms such as resizing, OCR, and speech recognition. | Extends the same invariants across modalities through `Meaning × Artifact State` and `Authority × Position` (**Table A.3**). |
| **CoSAI Risk Map** | `riskPromptInjection` (covers multimodal injection); `riskCovertChannelsInModelOutputs` | Component axis (Input Handling, Reasoning Core, Output Handling, Tools) and risk entries that name multimodal injection and steganographic encoding in outputs. | Transformation and perception components between input handling and the reasoning core. | Locates the check and the transform as distinct components between Input Handling and the Reasoning Core; the risk ID is attached to the mechanism record as a supporting annotation. |
| **CSA research note on image-based prompt injection (March 2026)** | Embedding techniques: typographic text, steganographic, adversarial perturbation and patched injectors, physical/3D | Representation taxonomy for image payloads, with the observation that current defenses only partly neutralize image injection. | Scaling and resampling as activation steps; carriers in other modalities. | Generalizes the same representation ordering across modalities (**Section 3.4.1**) and locates the activating transform. |

*Table A.1. Comparative coverage of existing AI security frameworks for the Trail of Bits image-scaling attack, expanding the summary in **Section 1.2**.*

### A.2 Relationship to the Invariant × Divergence Pair

| Framework | Existing Focus | Relationship to the Invariant × Divergence Pair |
| :---- | :---- | :---- |
| **NIST AI 100-2e2025** | Adversarial machine-learning terminology, attack lifecycle concepts, attacker objectives, capabilities, and knowledge. | Provides a broader threat taxonomy. The Divergence axis identifies where in a system's inference-time execution a check and the component it protects stop agreeing. |
| **MITRE ATLAS** | Adversarial tactics and techniques targeting AI-enabled systems. | Identifies techniques such as prompt injection and exfiltration through agent tools. The Invariant × Divergence pair locates where each technique enters, activates, and takes effect. |
| **OWASP Top 10 for LLM Applications (2025)** | Application-level security risks, including Prompt Injection (LLM01), Improper Output Handling (LLM05), and Excessive Agency (LLM06). | Corresponds to `Authority × Position` (`LLM01:2025`, `LLM06:2025`) and `Confidentiality × Position` (`LLM05:2025`). |
| **CoSAI Risk Map / Google SAIF** | Component × risk × control × lifecycle, including `riskPromptInjection` (covers multimodal injection). | Component axis (Input Handling, Reasoning Core, Output Handling, Tools) refined to the level of an individual check and the transform it should run after; risk ID carried as a supporting annotation. |
| **MITRE CWE** | Software weaknesses and their underlying conditions. | Weaknesses such as `CWE-180` (Validate Before Canonicalize) map directly to `Meaning × Artifact State` (*Transform Consistency*); full per-subclass mapping in **Table A.3**. |

*Table A.2. Framework focus and relationship to the Invariant × Divergence pair.*

### A.3 Classical Security Precedents by Invariant × Divergence Entry

Relationship tags: **Exact** means the classical concept names the same invariant and divergence; **Broader** means this paper's cell generalizes the classical concept to machine-learning transforms, perception, or aggregation; **Related** means the two share structure with different scope; **New** means the cell originates in this paper among the reviewed classical literature.

| Invariant × Divergence Entry | Classical Precedent | Relationship |
| :---- | :---- | :---- |
| *TOCTOU* | Time-of-check to time-of-use (`CWE-367`; `CAPEC-29`) | Exact |
| *Parser / Interpreter Differential* | Language-theoretic security parser differentials (Momot et al., 2016); Interpretation Conflict (`CWE-436`); HTTP request smuggling (`CWE-444`; `CAPEC-33`) | Exact |
| *Transform Consistency* | Validate before canonicalize (`CWE-180`); Alternate Encoding (`CAPEC-267`); NIDS insertion and evasion (Ptacek & Newsham, 1998) | Broader (extends to media transforms and multi-input aggregation) |
| *Human-Machine Perception* | User-interface misrepresentation (`CWE-451`); homograph attacks (`CAPEC-632`) | Broader (extends to images, audio, and physical signals) |
| *Guard-Model Capability* | Formal limits on filtering by a weaker evaluator (Glukhov et al., 2023; Ball et al., 2025) | New |
| *Semantic Stability* | — | New |
| *Grant Persistence* | Insufficient session expiration (`CWE-613`) | Related |
| *Data-Control* | Command injection and in-band signaling (`CWE-77`); LLM prompt neutralization (`CWE-1427`) | Exact for text; Broader across non-text modalities |
| *Decision-Action* | Complete mediation (Saltzer & Schroeder, 1975); Missing Authorization (`CWE-862`) | Related |
| *Confused Deputy* | The confused deputy (Hardy, 1988; `CWE-441`) | Exact |
| *Context Confinement* | Bell-LaPadula confidentiality; lattice model of secure information flow (Denning, 1976) | Exact |
| *Output-Consumer* | Improper output encoding and second-order injection (`CWE-116`; `CWE-79`); generative AI output validation (`CWE-1426`) | Related |
| *Resource Accounting* | Uncontrolled and asymmetric resource consumption (`CWE-400`; `CWE-405`; `CWE-409`) | Exact |
| `Authority` row | Biba integrity; lattice model of secure information flow (Denning, 1976) | Exact |
| Mechanism hierarchy as a whole | CAPEC View 1000 (*Mechanisms of Attack*) | Related (organized by attacker action; machine-perception cells added here) |

*Table A.3. Classical security and safety precedents for each Invariant × Divergence Table entry.*

### A.4 Comparable AI Taxonomies

| Taxonomy | Organizing Axes | Treatment of Modality | Relationship to the Mechanism Record |
| :---- | :---- | :---- | :---- |
| **PIAtlas** (Damianakis & Psounis, 2026) | Six subversion mechanisms (instruction manipulation, structural spoofing, obfuscation, social engineering, scenario framing, output coercion) | Assigned to the delivery layer | Orthogonal and composable; a PIAtlas class describes how a payload persuades the model once it has already crossed into Authority × Position, and can be carried as a supporting annotation |
| **Attack Atlas** (Rawat et al., 2024) | Prompt syntax, form, and semantics | Text only, single turn | Representation ladder within text; generalized by the four forms in **Section 3.4.1** |
| **CSA research note on image prompt injection** (2026) | Typographic, steganographic, adversarial perturbation, physical | Image only | Representation ladder within images; same ordering as **Section 3.4.1** |
| **Farhana & Roy** (2026) | Carrier type × pipeline location × attacker objective × stealth level | Carrier as a primary axis (image and document pipelines) | Closest neighbor on pipeline location; objective delegated to ATLAS and STRIDE; invariant replaces carrier as key |
| **Jain, Arık & Thakur** (2026) | Attacker objective × knowledge | Across modalities; modality-specific input processing named as a root cause | Objective-first; root cause formalized as `Meaning × Artifact State` |
| **Shi et al.** (2025) | Belief → intention → permission; trust–authorization mismatch | Modality-agnostic | Direct precedent for the `Authority` row |
| **Maloyan & Namiot** (2026) | Delivery vector × attack modality × propagation | Modality as a primary axis | Catalog of instances; records derive cross-modality-surface analogs from existing entries |
| **MLCommons Jailbreak Attack Taxonomy** (Maple et al., 2026) | Dominant prompt-manipulation strategy, closed Family > Category > Leaf hierarchy (4 families, 8 categories, 18 leaves) | Text only, single-turn, prompt-only; excludes indirect prompt injection | Representation ladder within text prompts; its Encoding Abuse and Composition & Ordering families map to this paper's *Encoded/Obfuscated* form and *Fragmented/Distributed*/*Sequence-Dependent* modifiers (**Section 3.4.1–3.4.2**); has no Invariant or Divergence analog |

*Table A.4. Comparable AI taxonomies and their relationship to the mechanism record.*

### A.5 Disambiguating Time from Artifact State

Both divergences describe a case where what was checked is not what was used, but the cause differs. In **Artifact State**, the system's own processing turns the input into a *different version*, and the check saw the old one. In **Time**, the check saw the right thing, but *that same thing changed later*, before it was used (Sections 3.2.2 and 3.2.3).

| | Artifact State (Section 3.2.2) | Time (Section 3.2.3) |
| :---- | :---- | :---- |
| **What causes the gap** | A processing step inside the pipeline (resizing, decoding, truncating, aggregating) | A change after approval (an attacker's edit, a page script, a permission that was not revoked) |
| **How many versions** | Two: the original was checked, a transformed copy was used | One, which changed over time |
| **Does a delay matter** | No; it occurs even if check and use are milliseconds apart | Yes; it needs a window between check and use |
| **Example** | A user approves a full-size image; the system shrinks it and reveals hidden text | A door credential is granted for one delivery run; nobody revokes it once the run ends |
| **Fix** | Move the check to after the transformation | Re-check immediately before use, or bind the approval to exactly what was approved |
| **Classical precedent** | Validation before canonicalization (`CWE-180`) | Time-of-check to time-of-use (`CWE-367`) |

*Table A.5. Artifact State and Time compared directly.*

Each fix does nothing for the other problem. Re-checking the full-size image immediately before use still shows a clean image, because the hidden text appears only after shrinking. Checking after the transformation does not help a stale credential, because nothing was transformed. One case belongs only to Time: a permission that should have expired but still works (*Grant Persistence*), where nothing is transformed and time simply passes.

### A.6 Supporting Annotations Beyond the Core Tuple

Section 3's tuple, `⟨Invariant, Divergence, Representation⟩`, is kept deliberately minimal: those three parts are what make two mechanisms the same or different, independent of modality. Recording a real finding, however, usually calls for a bit more bookkeeping than that — not because the taxonomy needs it to classify the mechanism, but because a usable record also needs to say where the mechanism sits and how it was found. This appendix collects those supporting annotations, which belong to the method of applying the taxonomy rather than to the taxonomy itself.

Two attributes complete the record in most cases: **System Processing Stage** (*where in the pipeline attacker-controlled information enters or becomes security-relevant*) and **Modality** (*the implementation surface across which mechanisms generalize*). Both are derived from the system's architecture when the taxonomy is applied; **System Processing Stage** follows from where the mechanism sits in the pipeline.

Records can also carry optional annotations when evidence supports them: **Construction Method** (*Manual Construction*, *Adaptive Search*, or *Optimization*, including transformation-invariant optimization), **Attacker Knowledge / Access** (*Black-box*, *Partial Knowledge*, or *White-box*), and **Transfer Context** (*Direct-Target Development* or *Surrogate Transfer*). Knowledge is recorded per component, since an attacker can know an image resizer exactly while treating the downstream model as a black box.

---

## Glossary and Terminology Alignment

This glossary lists the terms this paper defines and relates each one to the closest term in existing frameworks and literature, so readers who know those sources can map between them. **Relationship** uses four tags: **Same** (same term and meaning); **Equivalent** (the same concept under a different name); **Broader** (this paper widens the existing concept, usually to non-text modalities, machine perception, or human reviewers acting as guards); **New** (no equivalent found in the sources reviewed as of November 2026). ATLAS identifiers refer to data release v2026.09.

### Core model

| Term | Defined in | Meaning in this paper | Closest existing term(s) | Relationship |
| :---- | :---- | :---- | :---- | :---- |
| Mechanism | 2.3 | A reusable explanation of why an attack works, independent of modality | Vulnerability class; CWE weakness entry | Equivalent |
| Mechanism tuple `⟨Invariant, Divergence, Representation⟩` | 3.0 | Three-part key that classifies a mechanism | — | New |
| Invariant | 3.1 | The security property a mechanism breaks | Security property / objective (CIA triad) | Equivalent |
| Divergence | 3.2 | Why two evaluations assumed to agree actually differ | Interpretation conflict (`CWE-436`) | New (as a classification axis) |
| Representation | 3.4 | Form the adversarial payload takes at a given processing point | Payload; adversarial examples (NIST AI 100-2e2025) for one form | New (as a classification axis) |
| Reducible-only boundary | 5, limitation 1 | A mechanism that resists a deterministic architectural fix; only probabilistic defenses exist | Deterministic vs. probabilistic controls (Glukhov et al., 2023) | New |

### Invariants and divergences

| Term | Defined in | Meaning in this paper | Closest existing term(s) | Relationship |
| :---- | :---- | :---- | :---- | :---- |
| Meaning (*Semantic Integrity*) | 3.1.1 | Readers agree on what an artifact says | Integrity; interpretation conflict (`CWE-436`) | Broader |
| Authority | 3.1.2 | Entitlement to drive a consequential action | Access enforcement (NIST SP 800-53 AC-3); Biba integrity | Equivalent |
| Confidentiality | 3.1.3 | Secret context reaches only permitted recipients | Confidentiality; Bell-LaPadula; Denning (1976) | Same |
| Cost (*Resource Bounding*) | 3.1.4 | Resource use stays within the admitted budget | Availability; `CWE-400`; OWASP `LLM10:2025` Unbounded Consumption | Equivalent |
| Evaluator | 3.2.1 | Two evaluators read the same artifact state differently | `CWE-436`; ATLAS `AML.T0129` Triggers in Multimodal Inputs | Broader |
| Artifact State | 3.2.2 | A transform or aggregation changes content between check and use | `CWE-180` Validate Before Canonicalize; image-scaling attacks (Xiao et al., 2019; Quiring et al., 2020) | Broader |
| Time | 3.2.3 | State changes between validation (`t`) and use (`t + Δ`) | Time-of-check to time-of-use (`CWE-367`) | Equivalent |
| Position | 3.2.4 | A flow's trust or sensitivity label violates the sink's policy | Information-flow policy violation (Denning, 1976; NIST SP 800-53 AC-4) | Equivalent |

### Mechanism classes (Invariant × Divergence Table)

| Term | Cell | Closest existing term(s) | Relationship |
| :---- | :---- | :---- | :---- |
| Human-Machine Perception | Meaning × Evaluator | `CWE-451` UI Misrepresentation of Critical Information; `CWE-1039` Inadequate Detection or Handling of Adversarial Input Perturbations in Automated Recognition Mechanism | Broader |
| Guard-Model Capability | Meaning × Evaluator | ATLAS `AML.T0129` Triggers in Multimodal Inputs | New (as a named class) |
| Parser / Interpreter Differential | Meaning × Evaluator | `CWE-436`; parser differentials (Momot et al., 2016) | Same |
| Semantic Stability | Meaning × Evaluator | ATLAS `AML.T0054` LLM Jailbreak; `AML.T0015` Evade AI Model | New (as a named class) |
| Transform Consistency | Meaning × Artifact State | `CWE-180`; insertion and evasion (Ptacek & Newsham, 1998) | Broader |
| TOCTOU | Meaning × Time | `CWE-367` | Same |
| Grant Persistence | Authority × Time | `CWE-613` Insufficient Session Expiration; OWASP Agentic `ASI03` Identity & Privilege Abuse | Equivalent |
| Data-Control | Authority × Position | Prompt injection: OWASP `LLM01:2025`; ATLAS `AML.T0051`; `CWE-1427` (text only); OWASP Agentic `ASI01` Agent Goal Hijack | Broader (beyond text) |
| Decision-Action | Authority × Position | OWASP `LLM06:2025` Excessive Agency; OWASP Agentic `ASI02` Tool Misuse; `CWE-862` Missing Authorization | Equivalent |
| Confused Deputy | Authority × Position | Confused deputy (Hardy, 1988; `CWE-441`) | Same |
| Context Confinement | Confidentiality × Position | OWASP `LLM02:2025` Sensitive Information Disclosure; ATLAS `AML.T0086` Exfiltration via AI Agent Tool Invocation | Equivalent |
| Output-Consumer | Confidentiality × Position | ATLAS `AML.T0077` LLM Response Rendering; OWASP `LLM05:2025` Improper Output Handling; `CWE-1426` | Equivalent |
| Resource Accounting | Cost × Evaluator | `CWE-400`; ATLAS `AML.T0029` Denial of AI Service, `AML.T0034` Cost Harvesting | Equivalent |

### Representation forms, modifiers, and optional annotations

| Term | Defined in | Closest existing term(s) | Relationship |
| :---- | :---- | :---- | :---- |
| Overt Semantic | 3.4.1 | Plaintext prompt injection; typographic image injection | Equivalent |
| Encoded / Obfuscated | 3.4.1 | ATLAS `AML.T0068` LLM Prompt Obfuscation (encoding cases such as base64 or rot13) | Same |
| Steganographic | 3.4.1 | Steganography; ATLAS `AML.T0068` (hidden-text cases such as same-color text). ATLAS groups these with encoding; this paper separates them because normalization removes one but not the other | Same |
| Adversarial Perturbation | 3.4.1 | Adversarial examples (NIST AI 100-2e2025); ATLAS `AML.T0043` Craft Adversarial Data; `CWE-1039` | Equivalent |
| Fragmented / Distributed | 3.4.2 | Payload splitting (OWASP `LLM01:2025`, scenario 6) | Equivalent |
| Sequence-Dependent | 3.4.2 | — | New |
| Composition-Dependent | 3.4.3 | Cross-modal prompt injection (Wang et al., 2025) | New (as a composite dependency) |
| Intrinsic Amplification | 3.4.4 | Decompression bomb (`CWE-409`); asymmetric resource consumption (`CWE-405`) | Equivalent |
| Semantic Amplification | 3.4.4 | ATLAS `AML.T0034.001` Resource-Intensive Queries, `AML.T0034.002` Agentic Resource Consumption | Equivalent |
| Construction Method | Appendix A.6 | ATLAS `AML.T0043.000` White-Box Optimization, `.001` Black-Box Optimization, `.003` Manual Modification | Equivalent |
| Attacker Knowledge / Access (*Partial Knowledge*) | Appendix A.6 | White-box, black-box, and gray-box attacks (NIST AI 100-2e2025, Section 2.1.4) | Equivalent (*Partial Knowledge* = gray-box) |
| Transfer Context (*Surrogate Transfer*) | Appendix A.6 | ATLAS `AML.T0043.002` Black-Box Transfer | Equivalent |

### Terms used in applying the taxonomy

| Term | Defined in | Closest existing term(s) | Relationship |
| :---- | :---- | :---- | :---- |
| Modality surface | 2.3 | Attack surface, per input or output channel (Manadhata & Wing, 2011) | Equivalent |
| Cross-modality-surface prediction | 2.3 | Variant analysis (GitHub, n.d.) | Broader (extends variant analysis across modalities) |
| Demonstrated / Feasible (informal evidence-strength distinction) | 3.5.5 | ATLAS case-study type *Incident* / *Exercise* | Broader |
| Context separation | 5, limitation 1 | Control/data-flow separation (Debenedetti et al., 2025) | Equivalent |

---

## Acknowledgements

*[To be added.]*

## Workstream Leads

*[To be added — WS Lead Chair Name (email), Organization.]*

## Editors

*[To be added — Editor Name (email), Organization.]*

## Contributors

*[List of active contributors to be added.]*

---

## CoSAI Focus

CoSAI is an OASIS Open Project, bringing together an open ecosystem of AI and security experts from industry-leading organizations. The project is dedicated to sharing best practices for secure AI deployment and collaborating on AI security research and product development. The scope of CoSAI is specifically focused on the secure building, integration, deployment, and operation of AI systems, with an emphasis on mitigating security risks unique to AI technologies. Other aspects of Trustworthy AI are deemed important but beyond the scope of the project including, ethics, fairness, explainability, bias detection, safety, consumer privacy, misinformation, hallucinations, deep fakes, or content safety concerns like hateful or abusive content, malware, or phishing generation. By concentrating on developing robust measures, best practices, and guidelines to safeguard AI systems against unauthorized access, tampering, or misuse, CoSAI aims to contribute to the responsible development and deployment of resilient, secure AI technologies.

## Guidelines on Usage of AI Systems for Drafting Documents for OASIS CoSAI

tl;dr: CoSAI contributions are actions performed by humans, who are responsible for the content of those contributions, based on their signed OASIS iCLA (and eCLA, if applicable). Each contributor must confirm whether they are entitled to donate that material under the applicable open source license; OASIS and the CoSAI Project do not separately confirm that. Each contributor is responsible for ensuring that all contributions comply with these AI use guidelines, including disclosure of any use of AI in contributions.

* Selection of AI systems: CoSAI recommends the use of reputable AI systems (lowering the risk of inadvertently incorporating infringing material).
* Model constraints: Currently, CoSAI or OASIS are not required to have a contract or financial agreement for using AI systems from specific vendors. However, CoSAI editors should consider employing varying tools to avoid potential fairness concerns among vendors.
* IP infringement: It is the responsibility of the individual who subscribes/prompts and receives a response from an AI system to confirm they have the right to repost and donate the content to OASIS under our rules.
* Transparency: CoSAI's goal will be to maintain transparency throughout the process by documenting substantial use of AI systems whenever possible (e.g., the prompts and the AI system used), and to ensure that all content, regardless of production by human or AI systems, was reviewed and edited by human experts. This helps build trust in the standards development process and ensures accountability.
* Human-edited content and quality control: CoSAI mandates human-reviewed or -edited results for any final outputs. A robust quality control process should be in place, involving careful review of the generated content for accuracy, relevance, and alignment with CoSAI's goals and principles. Human experts should scrutinize the output of AI systems to identify any errors, inconsistencies, or potential biases.
* Iterative refinement: The use of AI systems in drafting standards should be seen as an iterative process, with the generated content serving as a starting point for further refinement and improvement by human experts. Multiple rounds of review and editing may be necessary to ensure the final standards meet the required quality and reliability thresholds.

## Disclaimer

The views represented in this paper do not necessarily represent the views of all CoSAI members, including reviewers and their organizations.

## Copyright Notice

Copyright © OASIS Open 2025. All Rights Reserved. This document has been produced under the process and license terms stated in the OASIS Open Project rules: https://www.oasis-open.org/policies-guidelines/open-projects-process.

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published, and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this section are included on all such copies and derivative works. The limited permissions granted above are perpetual and will not be revoked by OASIS or its successors or assigns. This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. OASIS AND ITS MEMBERS WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF ANY USE OF THIS DOCUMENT OR ANY PART THEREOF. The name "OASIS" is a trademark of OASIS, the owner and developer of this document, and should be used only to refer to the organization and its official outputs. OASIS welcomes reference to, and implementation and use of, documents, while reserving the right to enforce its marks against misleading uses. Please see https://www.oasis-open.org/policies-guidelines/trademark/ for above guidance.

This is a Non-Standards Track Work Product. The patent provisions of the OASIS IPR Policy do not apply.

