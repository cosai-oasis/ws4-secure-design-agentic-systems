# Model Context Protocol (MCP) Security

# Table of contents
  - [Abstract](#abstract)
    - [Scope](#scope)
    - [Anti-scope](#anti-scope)
    - [Target Audience](#target-audience)
  - [1. MCP Overview](#1-mcp-overview)
    - [1.1 MCP Architecture](#11-mcp-architecture)
      - [1.1.1 MCP Deployment Patterns](#111-mcp-deployment-patterns)
  - [2. MCP Threat Model](#2-mcp-threat-model)
    - [2.1 Threat Landscape and Methodology](#21-threat-landscape-and-methodology)
    - [2.2 Why MCP Requires a Different Approach](#22-why-mcp-requires-a-different-approach)
  - [3. MCP Threats](#3-mcp-threats)
    - [3.1 MCP Specificity](#31-mcp-specificity)
      - [3.1.1 MCP Specific](#311-mcp-specific)
      - [3.1.2 MCP Contextualized](#312-mcp-contextualized)
    - [3.2 Controls and Mitigations](#32-controls-and-mitigations)
      - [3.2.1 Agent Identity](#321-agent-identity)
      - [3.2.2 Secure Delegation and Access Control](#322-secure-delegation-and-access-control)
      - [3.2.3 Input and Data Sanitization and Filtering](#323-input-and-data-sanitization-and-filtering)
      - [3.2.4 Cryptographic Integrity and Remote Attestation](#324-cryptographic-integrity-and-remote-attestation)
      - [3.2.5 Sandboxing and Isolation](#325-sandboxing-and-isolation)
      - [3.2.6 Cryptographic Verification of Resources](#326-cryptographic-verification-of-resources)
      - [3.2.7 Transport Layer Security](#327-transport-layer-security)
      - [3.2.8 Secure Tool and UX Design](#328-secure-tool-and-ux-design)
      - [3.2.9 Lifecycle and Governance](#329-lifecycle-and-governance)
- [4. Conclusion](#4-conclusion)
- [5. Contributors and Acknowledgements](#5-contributors-and-acknowledgements)
- [6. Appendix](#6-appendix)
  - [6.1 Deployment Pattern (DP) Security Considerations](#61-deployment-pattern-dp-security-considerations)
    - [6.1.1 Deployment Pattern 1: All-Local](#611-deployment-pattern-1-all-local)
    - [6.1.2 Deployment Pattern 2: Single-Tenant MCP Server](#612-deployment-pattern-2-single-tenant-mcp-server)
    - [6.1.3 Deployment Pattern 4: Multi-Tenant MCP Server](#613-deployment-pattern-4-multi-tenant-mcp-server)
    - [6.2 Threat Details](#62-threat-details)
      - [MCP-T1: Improper Authentication and Identity Management](mcp-t1-improper-authentication-and-identity-management)
      - [MCP-T2: Missing or Improper Access Control](#mcp-t2-missing-or-improper-access-control)
      - [MCP-T3: Input Validation/Sanitization Failures](#mcp-t3-input-validationsanitization-failures)
      - [MCP-T4: Input/Instruction Boundary Distinction Failure](#mcp-t4-inputinstruction-boundary-distinction-failure)
      - [MCP-T5: Inadequate Data Protection and Confidentiality Controls](#mcp-t5-inadequate-data-protection-and-confidentiality-controls)
      - [MCP-T6: Missing Integrity/Verification Controls](#mcp-t6-missing-integrityverification-controls)
      - [MCP-T7: Session and Transport Security Failures](#mcp-t7-session-and-transport-security-failures)
      - [MCP-T8: Network Binding/Isolation Failures](#mcp-t8-network-bindingisolation-failures)
      - [MCP-T9: Trust Boundary and Privilege Design Failures](#mcp-t9-trust-boundary-and-privilege-design-failures)
      - [MCP-T10: Resource Management/Rate Limiting Absence](#mcp-t10-resource-managementrate-limiting-absence)
      - [MCP-T11: Supply Chain and Lifecycle Security Failures](#mcp-t11-supply-chain-and-lifecycle-security-failures)
      - [MCP-T12: Insufficient Logging, Monitoring, and Auditability](#mcp-t12-insufficient-logging-monitoring-and-auditability)
  - [6.3 MCP Threats and Vulnerabilities](#63-mcp-threats-and-vulnerabilities)
    - [6.3.1 Conventional Security](#631-conventional-security)
  - [6.4 CoSAI Focus](#64-cosai-focus)
  - [6.5 Guidelines on usage of more advanced AI systems (e.g. large language models (LLMs), multi-modal language models. etc) for drafting documents for OASIS CoSAI](#65-guidelines-on-usage-of-more-advanced-ai-systems-eg-large-language-models-llms-multi-modal-language-models-etc-for-drafting-documents-for-oasis-cosai)
  - [6.6 Copyright Notice](#66-copyright-notice)



# Abstract

Since its emergence a year ago, MCP has rapidly established itself as the protocol for transmitting structured context between AI agents and services. Given the growing importance and attack surface of MCP and agentic systems, it is imperative that deployment specific security threats are identified and improvements are made to address the challenges and ambiguities inherent in MCP implementations. Our primary goal is to share actionable security guidance for today's MCP implementations while identifying areas where the protocol and ecosystem may need to evolve to address emerging threats. We introduce short and medium-term security implications related to MCP through the introduction of twelve core threat categories and almost forty threats. Our taxonomy distinguishes between traditional security threats amplified by AI and MCP, and novel attack vectors. For each threat and category, we propose mitigations, defenses, and best practices for using MCP across multiple deployment scenarios including enterprise use cases. .

## Scope

This paper focuses on the security aspects of MCP implementations, covering:

* Security analysis of [the latest](https://modelcontextprotocol.io/specification/2025-06-18) (2025-06-18) specification MCP transport and protocol layers  
* Threat modeling strategies for MCP-based agentic systems[^1]  
* Supply chain security considerations for MCP servers and tools  
* Identity and access management challenges in agentic architectures consuming MCP endpoints  
* Best practices for secure MCP deployment and operation  
* Recommendations for protocol enhancements to address identified security gaps

We are collaborating with Anthropic and the MCP maintainer community to ensure our recommendations are practical and implementable. This work also coordinates with CoSAI's Software Supply Chain Security workstream to ensure comprehensive coverage of agentic system security concerns.

## Anti-Scope

This paper does not address:

* Content safety, misinformation, or AI ethics concerns unrelated to security  
* General AI model safety or alignment issues beyond their security implications  
* Detailed implementation of specific security tools (we provide guidance, not implementation).  Follow on papers will provide reference implementations and recommendations for specific mitigation controls.  
* Non-security aspects of MCP performance, scalability, or functional capabilities  
* Legal or regulatory compliance requirements (though our recommendations may support compliance efforts). For these matters, see the assets being created from our [Workstream 3: AI Risk Governance](https://github.com/cosai-oasis/ws3-ai-risk-governance).

## Target Audience

Primary audience: 

- **Security professionals and developers securing, creating or connecting to MCP servers**. This includes developers, security practitioners, enterprise architects, and organizations who are implementing, deploying, or integrating MCP servers and clients into their agentic AI systems.   
- (longer term) MCP maintainers, the broader MCP ecosystem including contributors to MCP implementations and tooling, and the core protocol developers at Anthropic and beyond

## Status: Draft

# 1. MCP Overview

[MCP](https://modelcontextprotocol.io/introduction) is an open standard developed by Anthropic and a growing open source community that provides a structured framework for connecting large language models and AI agents to external tools, data sources, and services. MCP addresses a fundamental challenge in agentic AI systems: how to enable models to access and interact with real-world resources dynamically while maintaining security and reliability through standardization. MCP simplifies AI application integration with databases, APIs, file systems, web services, and other external resources reducing the need for custom integrations for each tool or service.

MCP operates through a client-server architecture where AI applications (hosts) use MCP clients to establish connections with MCP servers that expose specific capabilities such as tools, resources, and prompts. The protocol defines standardized methods for:

* discovering available capabilities including tools or services  
* invoking parametrized services  
* accessing data resources

MCP supports multiple transport mechanisms including standard I/O (stdio) for local processes and Streamable HTTP for networked communications, enabling flexible deployment scenarios from local development environments to distributed cloud architectures.[^2]

## 1.1 MCP Architecture

MCP follows a client-server architecture where host applications (such as AI assistants, IDEs, or workflow automation tools) use MCP clients to connect to local or remote MCP servers. Each client-server connection operates as a dedicated, stateful session that begins with initialization and capability negotiation. Communication is built on JSON-RPC, which defines the message format and protocol semantics including lifecycle management and core primitives (tools, resources, and prompts). The transport layer handles the delivery of these JSON-RPC messages between clients and servers, supporting stdio for local processes and Streamable HTTP for remote servers.

```mermaid
graph LR
    subgraph "Local machine"
        S1[Server 1<br>Files & Git]
        R1[("Local<br>Resource A")]
        C1 --> S1
        S1 <--> R1
        subgraph "Application Host Process"
          H[Host]
          C1[Client 1]
          C2[Client 2]
          C3[Client 3]
          H --> C1
          H --> C2
          H --> C3
        end
    end

    subgraph "Internal System"
        S2[Server 2<br>Database]
        R2[("Local<br>Resource B")]
        C2 ----> S2
        S2 <--> R2
    end

    subgraph "Internet"
        S3[Server 3<br>External APIs]
        R3[("Remote<br>Resource C")]

        C3 ----> S3
        S3 <--> R3
    end
```

### 1.1.1 MCP Deployment Patterns

MCP servers can be deployed across diverse environments with varying trust relationships and security implications. The security posture of an MCP deployment depends on several intersecting factors: where the server code originates (first-party, open source, third-party), where it executes (local machine, internal infrastructure, external cloud), and what resources it can access (local files, enterprise systems, external services).

Each deployment pattern creates distinct trust boundaries that fundamentally shape the threat model. Local deployments using `stdio` transport provide process-level isolation but require careful management of file system access. Internal network deployments using Streamable HTTP must consider lateral movement risks and authentication requirements. External cloud deployments introduce internet-facing attack surfaces and multi-tenancy concerns. 

1. **All-Local**: The MCP client and server are co-located leveraging stdio or http transports  
2. **Single-Tenant Hybrid**: The MCP client connects to a single-tenant hosted MCP server over http. The MCP client may run locally or be hosted remotely.  
3. **Multi-Tenant Cloud**: MCP clients from multiple tenants connect to a shared MCP server.  
   

These deployment patterns each carry a distinct threat model based on the trust boundaries between client and server. Threat models differ by which components are trusted or untrusted, single- vs. multi-tenant setups, and local vs. remote deployments.A deeper analysis of the security implications of each is presented in the Appendix.

# 2. MCP Threat Model

## 2.1 Threat Landscape and Methodology

As with many newly adopted technologies there are numerous examples of significant security incidents across MCP deployments.

* **Asana AI incident** (May 2025): Tenant isolation flaw allowed cross-organization data contamination affecting up to 1,000 enterprises. ([Read more](https://www.upguard.com/blog/asana-discloses-data-exposure-bug-in-mcp-server))
* **WordPress Plugin vulnerability**: Over 100,000 sites affected by privilege escalation via MCP in AI Engine plugin, patched June 18, 2025 ([Read more](https://nvd.nist.gov/vuln/detail/CVE-2025-5071))
* **Supabase MCP Issue** Researchers demonstrated how prompt injection via support ticket data could cause AI tools like Cursor to expose private tables through a connected MCP server with direct database access, exploiting excessive tools and overprivilege. ([Read more](https://supabase.com/blog/defense-in-depth-mcp))

This section examines current threats through documented incidents and establishes a threat model addressing MCP's unique interdependency challenges.

## 2.2 Why MCP Requires a Different Approach

While there are numerous, high quality frameworks addressing AI risk (e.g. MITRE ATLAS, NIST AI RMF, MAESTRO, etc.) MCP introduces fundamentally new security considerations:

* Protocol-level authentication between AI clients and tool servers  
* Dynamic capability negotiation that determines what tools AI can access  
* Distributed trust relationships across multiple independent tool providers  
* Session management complexities unique to long-lived AI conversations

Though existing frameworks are designed to assess complex multi-component systems, they assume components behave predictably according to predefined logic. MCP places an LLM, an agent whose behavior is shaped by natural language input, at the center of security-critical decisions, requiring a fundamentally different threat model.

# 3. MCP Threats

This framework organizes nearly forty threats to MCP deployments across twelve distinct categories, spanning the full technology stack—from foundational identity and access controls through AI-specific boundary failures to supply chain and operational visibility requirements. This model enables security teams to prioritize defenses based on the specific threats and attack surfaces relevant to their deployment. The taxonomy distinguishes between traditional security concerns amplified by AI mediation and novel attack vectors unique to LLM-tool interactions, providing clear guidance for implementing defense-in-depth strategies across the MCP ecosystem.  

![][threat_triangle]  

The first set of risk categories (T1–T2) covers foundational identity and access control risks critical to understanding the origins of a request and how it is being executed through the complex interactions of agents and tools. Next are threats related to input handling stemming from both traditional and AI-specific threats (T3–T4), protection of data and code confidentiality and integrity (T5–T6), and network and transport security (T7–T8). Lastly, MCP risks go beyond a protocol and reference implementation, and spans the MCP lifecycle, including how organizations use and manage MCP capabilities: managing trust relationships (T9), governing resources (T10), ensuring secure supply chains (T11), and maintaining visibility (T12).

## 3.1 MCP Specificity

The broad applicability and diverse deployment models and supported transports results in a large number of applicable threats. Threats are divided into three tiers:

* **Tier 1 \- MCP Specific Threats (7 Threats)**: Novel risks and threats due to MCP’s architecture and design decisions.   
* **Tier 2 \- MCP Contextualized Threats (8 Threats)**: known threats that manifest differently in MCP contexts or are amplified in MCP deployments  
* **Tier 3 \- Conventional Threats (25 Threats)**: security threats are are broadly applicable or derive from legacy, infrastructure, or transport implementation decisions

The table below organizes the threats by category and provides a mapping to controls and mitigations, discussed next.

| Threat | Threat Category | MCP Specific | MCP Contextualized | Conventional Security | Control and Mitigation |
| :---- | :---- | :---- | :---- | :---- | :---- |
| [MCP-T1](#mcp-t1-improper-authentication-and-identity-management) | Improper Authentication and Identity Management  | [1. Identity Spoofing](#identity-spoofing) | [8. Confused Deputy (OAuth Proxy)](privilege-escalation) | [16. Credential Theft/Token Theft](#credential-theft) </br> [17. Replay Attacks/Session Hijacking](#replay-attacks) </br>[18. OAuth/Legacy Auth Weaknesses](#auth-weakness) </br>[19. Session Token Leakage](#token-leakage) | [Agent Identity](#321-agent-identity) </br>[Secure Delegation (i.e. OAuth delegation)](#322-secure-delegation-and-access-control)  |
| [MCP-T2](#mcp-t2-missing-or-improper-access-control) | Missing or Improper Access Control  |  | [9. Insecure Human-in-the-Loop](#hil) [10. Improper Multitenancy](#improper-multitenancy) | [8. Privilege Escalation](#privilege-escalation) </br> [20. Excessive Permissions/Overexposure](#excessive-permissions) | [Secure Delegation Access Control](#322-secure-delegation-and-access-control)  |
| [MCP-T3](#mcp-t3-input-validationsanitization-failures) | Input Validation/Sanitization Failures |  |  | [21. Command Injection](#command-injection) </br> [22. File System Exposure/Path Traversal](#path-traversal) </br> [23. Insufficient Integrity Checks](#insufficient-integrity-checks) | [Data Sanitization Guardrails](#323-input-and-data-sanitization-and-filtering) </br>[Sandboxing and Isolation](#325-sandboxing-and-isolation) </br>([Roots](https://modelcontextprotocol.io/specification/2025-06-18/client/roots) support)  |
| [MCP-T4](#mcp-t4-inputinstruction-boundary-distinction-failure) | Data/Control Boundary Distinction Failure  | [2. Tool Poisoning](#tool-poisoning) </br> [3. Full Schema Poisoning](#fsp) </br> [4. Resource Content Poisoning](#resource-content-poisoning) | [11. Prompt Injection](#prompt-injection)  | [21. Command Injection](#command-injection) | [Input Sanitization, Guardrails Context Isolation](#323-input-and-data-sanitization-and-filtering) |
| [MCP-T5](#mcp-t5-inadequate-data-protection-and-confidentiality-controls) | Inadequate Data Protection and Confidentiality Controls |  |  | [24. Data Exfiltration & Corruption](#data-exfiltration) </br> [22. File System Exposure/Path Traversal](#path-traversal) | [Sandboxing and Isolation](#325-sandboxing-and-isolation) </br> [Access Control](#322-secure-delegation-and-access-control) </br> [Guardrails](#323-input-and-data-sanitization-and-filtering) |
| [MCP-T6](#mcp-t6-missing-integrityverification-controls) | Missing Integrity/Verification Controls | [4. Resource Content Poisoning](#resource-content-poisoning) </br> [5. Typosquatting/Confusion Attacks](#typosquatting) </br> [6. Shadow MCP Servers](#shadow-mcp) |  | [25. Supply Chain Compromise and Privileged host-base Attacks](#supply-chain)  | [Cryptographic Integrity Remote Attestation MCP server integrity](#326-cryptographic-verification-of-resources) |
| [MCP-T7](#mcp-t7-session-and-transport-security-failures) | Session and Transport Security Failures |  | [12. Man-in-the-Middle (MITM)](#mitm) | [26. Unrestricted Network Access](#unrestricted-network) </br> [27. Protocol Security Gaps](#protocol-security) </br> [28. Insecure Descriptor Handling](#insecure-descriptor) </br> [23. Insufficient Integrity Checks](#insufficient-integrity-checks) </br> [29. CSRF Protection Missing](#csrf) </br> [30. CORS/Origin Policy Bypass](#cors) | [Network and Transport Security](#327-transport-layer-security) |
| [MCP-T8](#mcp-t8-network-bindingisolation-failures) | Network Binding/Isolation Failures | [6. Shadow MCP Servers](#shadow-mcp) | [10. Improper Multitenancy](#improper-multitenancy) | [31. Malicious Command Execution](#malicious-command-execution) </br> [32. Dependency/Update Attack](#dependency-update-attack) </br> [26. Unrestricted Network Access](#unrestricted-network) | [Network and Transport Security](#327-transport-layer-security) </br> [Sandboxing and Isolation](#325-sandboxing-and-isolation) |
| [MCP-T9](#mcp-t9-trust-boundary-and-privilege-design-failures) | Trust Boundary and Privilege Design Failures | [7. Overreliance on the LLM](#overreliance) | [13. Consent/User Approval Fatigue](#user-fagitue) |  | [Secure tool design UX Design](#328-secure-tool-and-ux-design) |
| [MCP-T10](#mcp-t10-resource-managementrate-limiting-absence) | Resource Management/Rate Limiting Absence |   | [14. Resource exhaustion and denial of wallet](#resource-exhaustion) | [33. Payload Limit/DoS](#payload-limit) | [Network and Transport Security](#327-transport-layer-security) |
| [MCP-T11](#mcp-t11-supply-chain-and-lifecycle-security-failures) | Supply Chain and Lifecycle Security Failures | [6. Shadow MCP Servers](#shadow-mcp) |  | [25. Supply Chain Compromise](#supply-chain) | [Lifecycle Governance](#329-lifecycle-and-governance) |
| [MCP-T12](#mcp-t12-insufficient-logging-monitoring-and-auditability) | Insufficient Logging, Monitoring, and Auditability |  | [15. Invisible Agent Activity](#invisible-agent) | [34. Lack of Observability](#lack-of-observability) | [Lifecycle Governance](#329-lifecycle-and-governance) |

### 3.1.1 MCP Specific

<a id="identity-spoofing"></a>
**1. Identity Spoofing** Weak or misconfigured authentication in MCP deployments could allow attackers to impersonate legitimate clients or the agents acting on their behalf, corrupting audit trails or gaining unauthorized access to server resources.

<a id="tool-poisoning"></a>
**2. Tool Poisoning** Malicious modification of tool metadata, configuration, or descriptors injected into clients via the tools/list method. This can cause AI agents or MCP components to invoke, trust, or execute compromised tools, potentially leading to data leaks or system compromise. As the MCP specification notes, 'descriptions of tool behavior such as annotations should be considered untrusted, unless obtained from a trusted server' ([Key Principles](https://modelcontextprotocol.io/specification/draft/index#key-principles)), making tool poisoning a recognized risk when clients connect to unvetted servers.

<a id="fsp"></a>
**3. Full Schema Poisoning (FSP)** Attackers compromise entire tool schema definitions at the structural level, injecting hidden parameters, altered return types, or malicious default values that affect all subsequent tool invocations while maintaining apparent compatibility and evading detection by appearing legitimate to monitoring systems.

Unlike Tool Poisoning (\#2): Goes beyond poisoning individual tool metadata to compromise the entire structural definition and type system of tools.

<a id="resource-content-poisoning"></a>
**4. Resource Content Poisoning** Attackers embed hidden malicious instructions within data sources (databases, documents, API responses) that MCP servers retrieve and provide to LLMs, causing the poisoned content to execute as commands when processed, effectively achieving persistent prompt injection through trusted data channels rather than direct user input. Unlike Prompt Injection (\#12): Malicious instructions are embedded in backend data sources, not user-provided prompts. Unlike Tool Poisoning (\#2): Poisons the actual data/content retrieved by tools, not the tool definitions themselves. This attack surface may be expanded with transitive or composed MCP server calls.

<a id="typosquatting"></a>
**5. Typosquatting/Confusion Attacks** Malicious actors create MCP servers or tools with names/descriptions similar to legitimate ones, tricking clients or AI agents into invoking harmful tools due to naming confusion or LLM hallucination. The MCP specification provides guidance on making tool origins and inputs visible to users and recommends human-in-the-loop approval for tool invocations ([User Interaction Model](https://modelcontextprotocol.io/specification/draft/server/tools#user-interaction-model)), but consent fatigue—where users reflexively approve prompts without careful review—can significantly undermine these protections.

<a id="shadow-mcp"></a>
**6. Shadow MCP Servers** Unauthorized, unmonitored, or hidden MCP server instances create blind spots, increasing risk of undetected compromise and covert data exfiltration. These servers pose governance and compliance risks and may be malicious or easily compromised. 

<a id="overreliance"></a>
**7. Overreliance on the LLM** MCP server developers may implement overly permissive tools, assuming the LLM will invoke them correctly and safely. However, model-level controls (trained refusals, safety classifiers, etc.) are not ironclad—even capable models can be manipulated through prompt injection, make errors in judgment, or be replaced with weaker models that lack equivalent safeguards.

### 3.1.2 MCP Contextualized

<a id="privilege-escalation"></a>
**8. Privilege Escalation via Authentication and Authorization Bypass** Attackers exploit misconfigured roles, credentials, ACLs, trust relationships, or flawed delegation logic to gain elevated permissions and access unauthorized resources. In MCP deployments, this includes privilege escalation, as well as attacks that leverage the MCP server's intermediary role in multi-user token delegation. For example, confused deputy attacks can occur when an MCP server acting as an OAuth proxy fails to properly validate authorization context—allowing attackers to manipulate the server into using another user's credentials to perform privileged operations.  See the [official MCP guidance on preventing Confused Deputy attacks](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices#confused-deputy-problem).

<a id="hil"></a>
**9. Insecure Human-in-the-Loop** Missing or insufficient human-in-the-loop consent checks can allow an MCP server to take risky actions not authorized by the user.

<a id="improper-multitenancy"></a>
**10. Improper Multitenancy** An attacker may exploit weak isolation between tenants or users, such as shared memory between processes, sessions,  or secrets and credentials, to access or manipulate unauthorized data.

<a id="prompt-injection"></a>
**11. Prompt Injection** LLMs have insufficient boundaries between input data and instructions. Attackers craft malicious inputs to manipulate LLMs or MCP components to perform unintended or harmful actions such as data exfiltration, privilege escalation, or unauthorized command execution. These malicious instructions can be sent *directly* to the LLM (e.g., via Sampling or when the MCP tool uses its own LLM) or *indirectly* by embedding instructions in prompts, resources, or tool metadata. This threat exists whenever untrusted input can reach the LLM's context window.

<a id="mitm"></a>
**12. Man-in-the-Middle (MITM)** Exploiting insecure network transport (lack of TLS, improper certificate validation, or missing mutual authentication) to intercept, modify, or reroute data between MCP components, enabling data theft or manipulation.

<a id="user-fagitue"></a>
**13. Consent/User Approval Fatigue** Flooding users with excessive consent or permission prompts, causing habituation and leading to blind approval of potentially dangerous or malicious actions.

<a id="resource-exhaustion"></a>
**14. Resource exhaustion and denial of wallet** Attackers trigger an excessive number of LLM, tool, or other API calls leading to unexpected costs or resource exhaustion and denial of service.

<a id="invisible-agent"></a>
**15. Invisible Agent Activity** Agents or servers operate covertly, mimicking valid workflows but executing malicious or unauthorized actions without detection.

Conventional security threats to MCP, and definitions of the twelve threat categories, are discussed in the Appendix.

## 3.2 Controls and Mitigations

### 3.2.1 Agent Identity

All requests should be traceable across the entire execution chain: the end user or initiating agent, any intermediate MCP servers, and the tools or services that performed the resulting actions. Standards are emerging to define the identity of agents and servers. One of these is SPIFFE / SPIRE, which provides cryptographic workload identities that can be granted authorization to resources. The SPIFFE ID can be used in token exchange as the subject or actor depending on the flow.

Secure identity, authentication, and authorization across the agentic and MCP ecosystem is an extremely active area of research and development. We will provide a much deeper analysis of the problem space in a subsequent white paper. 

### 3.2.2 Secure Delegation and Access Control

To mitigate against privilege escalation, MCP servers should operate with the minimum privileges necessary. OAuth provides a widely adopted framework for secure delegation, with extensions that support fine-grained scope control and secure token flows (see [MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization#authorization-flow)).

* Leverage existing identity providers to provide user authentication using standards such as OIDC  
* Register MCP server as clients with the IAM provider. If the registration cannot happen a priori, then use Dynamic Client Registration   
* Do not [passthrough the OAuth tokenss](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices#token-passthrough) provided by the user  
* Perform token exchange with the authorization server to provide full accountability ([RFC8693](https://datatracker.ietf.org/doc/html/rfc8693))  
* Reduce scopes for least privilege, such as removing write scopes when only read access is required ([SEP-835](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/835) adds native support to define scopes in 2025-11-25 MCP specification)  
* User short-liven tokens and support proof-of-possession (DPoP) to prevent replay attacks ([RFC9449](https://datatracker.ietf.org/doc/html/rfc9449))  
* Fine grained authorizations, through Rich Authorization Requests ([RFC9396](https://datatracker.ietf.org/doc/html/rfc9396)), limit requests to specific resources or tool parameters

All endpoint services should implement robust access control models, such as role-based access control (RBAC) or attribute-based access control and evaluate against claims made by the identity provider, such as role membership, job title, or work location. Additionally, robust policy languages including Open Policy Agent (OPA), Cedar, or OpenFGA provide robust, flexible, and secure protections. 

### 3.2.3 Input and Data Sanitization and Filtering

A secure implementation of MCP requires strong data sanitization, input validation, and guardrails to protect against malicious or unsafe data inputs. Existing best practices for securing other RPC protocols should be applied. 

All inputs should be strictly validated using allowlists at every trust boundary, with particular attention to sanitizing file paths through canonicalization, employing parameterized queries for database operations, and applying context-aware output encoding appropriate to each execution context (SQL, shell, HTML). Tool developers can include cryptographic checks, such as message authentication codes, digital signatures and encryption to ensure the end-to-end integrity and confidentiality of tools and resources.

LLM guardrails should treat all AI-generated content as untrusted input requiring the same rigorous validation as direct user input, deploying prompt injection detection systems that analyze patterns and structured formats (strict JSON schemas) to maintain clear boundaries between instructions and data. This includes all data returned from MCP servers including tool and resource definitions, resources, prompts, elicitation requests, and tool responses.

### 3.2.4 Cryptographic Integrity and Remote Attestation

Hardware Trusted Execution Environments (TEE) like Intel TDX, ARM TrustZone and AMD-SEV/SNP provide stronger isolation and can provide protection against runtime tampering of trusted servers, such as tool poisoning due to server compromise. Combined with remote attestation, TEEs can  isolate MCP servers and clients from compromised hardware, malicious administrators of server infrastructure, and certain classes of co-tenancy threats. For containerized deployments, consider the use of confidential containers (CoCo) that run containers in TEEs, and use remote attestation to verify the trustworthiness of the TEEs and what is running in them.

| Threat Category | How TEE \+ Remote Attestation provide Mitigation |
| :---- | :---- |
| MCP T5: Inadequate Data Protection and Confidentiality Controls      | MCP Client  and MCP Servers are isolated from other software running on the hardware, and also from the operator of the hardware, by running them in TEEs. </br></br> Insider and privileged access to the TEEs is prevented there by minimizing the attack vectors for this threat. Good system design should include other controls for verifying the attestations, and delivery of secrets and sensitive data via secure channels to the MCP Clients and Servers running in attested TEEs. </br></br> Compromised and/or Malicious co-tenant cannot access or tamper with Client and MCP Server code or data that is running inside TEEs. Additional controls would be necessary to ensure the data is protected in-transit and at-rest with tenant-specific keys, and RA-TLS, etc.  With end to end data protection designs built on TEEs, Identity credentials, access tokens, keys and secrets can be protected from compromise and exposure. </br></br> Compromised or Incorrect (or shadow) MCP Server launched in TEEs have different sets of measurements, and these will fail to attest, and MCP Client can refuse to interact with the MCP Servers.  Credentials and access tokens will not be provided to the MCP Servers.  TEEs however cannot mitigate against vulnerabilities in the running code, and should be complemented with runtime controls. (Seccomp, Apparmor, etc.) |
| MCP T9: Trust Boundary and Privilege Design Failures | Privileged software host-based attacks will not affect the MCP Client and the MCP Servers when they are running in TEEs. The host system, host OS, host firmware and the host Hypervisor are outside the Trust Boundary of the TEEs. However, sophisticated host-based attacks that include certain physical attacks on the hardware are not mitigated by TEEs. |

Complement the use of TEEs with other sandboxing and isolation technologies. 

### 3.2.5 Sandboxing and Isolation

Agents and MCP servers should be executed with least privilege. MCP servers that interact with the host environment (e.g. by accessing files, running commands, issuing network connections), or that execute LLM-generated code, should always run in a sandbox to mitigate against potential safety and security threats.

 LLM-generated code and commands may contain hallucinations, bugs, or vulnerabilities, and should not run with full user privileges. MCP servers are commonly deployed in containers for ease of use, but containers should not be relied upon as a strong security boundary. Consider additional sandboxing (gVisor, Kata Containers, SELinux sandboxes) for stronger isolation.

### 3.2.6 Cryptographic Verification of Resources

Organizations developing MCP servers must provide cryptographic signatures and software bill of materials (SBOMs) for all server code to verify provenance. Organizations deploying MCP clients and servers should obtain and verify the contents and cryptographic signatures prior to deployment, and have policies restricting the approved sources and signing keys. TLS should be used to protect all data in transit. Remote attestation can further verify that servers are running expected code in a trusted environment. When supported, end-to-end cryptographic signatures can prove the authenticity of resources returned by MCP servers.

### 3.2.7 Transport Layer Security

MCP is structured around distinct communication layers that facilitate robust interaction between systems. At the transport layer, MCP leverages two primary communication methods:

* **stdio Transport:**  
  A direct, pipe-based stream communication channel, typically used for intra-process or tightly integrated inter-process communications. JSON-RPC messages flow directly via standard input/output streams. This transport is most commonly used for local servers.

* **HTTP Streaming Transport:**  
  A generalized HTTP-based transport channel supporting bidirectional JSON-RPC communication via streamed request-response patterns. This transport is most commonly used for remote servers.

At the higher-level protocol layer, MCP employs JSON-RPC 2.0 to standardize the formatting and processing of commands and responses communicated across these transport channels. JSON-RPC ensures structured messaging, enabling interoperability and clarity of communication across diverse platforms.

However, these transport and protocol layers, when improperly secured or configured, can expose MCP clients and servers to multiple vulnerabilities. The following table summarizes critical missing security controls across MCP’s layers and transports, along with specific exploits enabled by each gap:

| RequiredSecurity Control | Protocol | Example Exploits |
| ----- | ----- | ----- |
| Payload Limits | All Transports | Large payload and recursive payload DoS |
| Client-Server Authentication/Authorization | HTTP-based Transports | Impersonation, pre-init commands, unauthorized RPC calls |
| Downstream Authentication/Authorization | All Transports | Impersonation, pre-init commands, unauthorized RPC calls |
| Mutual TLS Authentication | HTTP-based Transports | Impersonation attacks |
| TLS Encryption | HTTP-based Transports | Stream tampering, TLS downgrade |
| Cross-Origin (CORS) | HTTP-based Transports | Cross-origin data leaks |
| CSRF Protection | HTTP-based Transports | Forged POST requests |
| Secure Descriptor Handling | stdio Transport | Hijacking via inherited descriptors |
| Integrity Checks | All Transports | Replay, spoofing, poisoned responses |

Implementing the above controls across transport and protocol layers significantly reduces the attack surface of MCP deployments.

### 3.2.8 Secure Tool and UX Design

Tool and UX design represent a critical security control point in Model Context Protocol (MCP) deployments. While much attention is paid to model safety and prompt injection defenses, the tools that agents invoke are often the actual execution surface where security boundaries are crossed and sensitive operations are performed. Poor tool design can undermine even the most robust authentication and authorization controls by creating overly permissive capabilities or delegating security-critical decisions to the LLM itself.

Each tool should have a single, clearly defined purpose with explicit boundaries on what it can and cannot do. When possible, create use-case driven or purpose-built tools, avoiding excessively powerful tools, e.g., execute a prepared statement versus executing any SQL statement. Tool implementations should not rely on the LLM to perform security-critical operations, validate inputs, or enforce constraints. 

Safe and secure execution should not rely solely on the human user, who may not understand the security implications of frequent security prompts and can easily become fatigued. Security-relevant messages and elicitations should be clear, indicating the implications of the request, and unambiguous what is being requested. 

### 3.2.9 Lifecycle and Governance

Organizations must: 

* implement mandatory code signing verification for all MCP servers before installation,   
* use private package repositories with security scanning and approval workflows,   
* deploy software composition analysis (SCA) tools to detect vulnerable dependencies,   
* implement allow-lists of approved MCP servers with documented security reviews,   
* Run MCP servers and clients in TEEs and use remote attestation to verify prior to interactions,  
* use cryptographic hash verification for package integrity,   
* and deploy binary authorization that prevents execution of unsigned or unverified code. 


Supply chain security requires:  

* implementing software bill of materials (SBOM) tracking for all MCP components,   
* using dependency pinning with hash-based verification rather than version ranges,   
* deploying automated vulnerability scanning for MCP servers and dependencies,   
* implementing secure software development lifecycle (SSDLC) practices for internal MCP servers,   
* using reproducible builds to verify package authenticity,   
* and monitoring security advisories and CVE databases for known vulnerabilities in dependencies. 

Lifecycle management demands:

*  maintaining centralized inventory of all deployed MCP servers with metadata (version, owner, purpose),   
* implementing automated discovery to detect shadow or unauthorized MCP deployments,   
* deploying lifecycle policies that automatically deprecate or remove outdated servers,   
* using configuration management tools (Ansible, Puppet, Chef) to maintain consistent deployments,   
* implementing rollback capabilities for problematic updates,   
* and deploying update management processes with testing and staged rollout. 


Operational practices include: 

* regular security reviews and re-certification of approved MCP servers,   
* automated scanning for shadow deployments across the organization,   
* decommissioning procedures that ensure complete removal of deprecated servers,   
* and version tracking with forced upgrade policies for servers with known vulnerabilities.

And, lastly, proper observability should be implemented across the stack to provide sufficient visibility to ensure compliance and enable developer debugging and incident investigation. Immutable records of actions and authorizations, such as token exchange implemented by an IDP (identity provider), provides accountability pertaining to who requested an action and how it was authorized. All interactions with the agent, tools, prompts, and models should be logged. OpenTelemetry provides end-to-end linkability of actions and is being widely adopted and integrated into many agentic tools and MCP servers and provides a consistent set of APIs and schemas. 

# 4. Conclusion

 MCP adoption is accelerating, and security must keep pace. Our analysis reveals common vulnerabilities in deployments that lack adequate authentication, session management, and supply chain controls. Incidents in adjacent AI systems demonstrate these are active threats, not theoretical concerns. 

Organizations deploying MCP-based systems must develop defense-in-depth strategies including zero-trust architectures, hardware-based isolation through trusted execution environments, rigorous supply chain vetting, and continuous monitoring. Securing MCP deployments requires coordinated effort across developers, organizations, and protocol maintainers—investment in security architecture now will pay dividends as agentic systems become more prevalent.

# 5. Contributors and Acknowledgements

**Workstream Leads**

* Sarah Novotny, (sarah.novotny@gmail.com)  
* Ian Molloy, IBM ([molloyim@us.ibm.com](mailto:molloyim@us.ibm.com))  
* Raghu Yeluri, Intel (raghuram.yeluri@intel.com)  
* Alex Polyakov, Adversa AI (alex@adversa.ai)

**Editors**

* Daniel Rohrer, NVIDIA (drohrer@nvidia.com)  
* Jenn Newton, Anthropic ([jenn@anthropic.com](mailto:jenn@anthropic.com))  
* David LaBianca, Google (ddlb@google.com)  
* Shrey Bagga, Cisco(sbagga@cisco.com)

**Contributors**

* John Cavanaugh, ProCap360 ([johncavanaugh@procap360.com](mailto:johncavanaugh@procap360.com) )  
* Chooi Low, Dell ( [Chooi.Low@dell.com](mailto:Chooi.Low@dell.com))  
* Marina Zeldin, Dell ([marina.zeldin@dell.com](mailto:marina.zeldin@dell.com))  
* Jonathan Whitson( [jonathan\_whitson@dell.com](mailto:jonathan_whitson@dell.com))  

**Technical Steering Committee Co-Chairs**

* Akila Srinivasan, Anthropic (akila@anthropic.com)  
* J.R. Rao, IBM (jrrao@us.ibm.com)

# 6. Appendix

## 6.1 Deployment Pattern (DP) Security Considerations

The following section examines the common deployment patterns and their security implications in more detail.

### 6.1.1 Deployment Pattern 1: All-Local

**MCP Client:** 	localhost  
**MCP Server:** 	localhost  
**Transport:**		stdio | http

```mermaid
---
    title: "DP1: All Local"
---
graph LR
    subgraph Local["Local Device"]
    direction LR
      Client["MCP Client"]
      Server["MCP Server"]
      Server2["MCP Server"]
    end
Client--"stdio"-->Server
Client--"http"-->Server2
```

All-local deployment security is entirely dependent on the host system's posture and a general-purpose desktop or laptop with standard user software, internet connectivity, and physical access exposes the MCP server to the same attack vectors: malware execution, credential theft, supply chain compromise through installed packages, and physical device access. 

With `stdio` transport, the MCP server runs as a subprocess of the host application, typically sharing the same user privileges and security context. This model trades network segmentation and centralized security controls for simplicity and direct access to local tools. It is well-suited for development workflows, trusted personal tools, and scenarios requiring direct local system access. However, for production deployments handling sensitive data or serving multiple users, the lack of isolation and dependence on host security may be insufficient depending on organizational risk tolerance and compliance requirements.

**Security Implications**:

* Exposes local system to potentially malicious or compromised servers  
* Execution control: Inherits host's security posture  
* Data access control: inherits host's data posture

**Security Recommendations**:

* Appropriate for development and personal use  
* Use `stdio` to avoid DNS rebinding risks: `stdio` transport is strongly recommended for local MCP as this eliminates [DNS rebinding risks that can occur with HTTP-based transports on local servers](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning)  
* Use sandboxing to limit privilege escalation attacks: MCP servers locally requires a sandbox to prevent privilege escalation attacks

### 6.1.2 Deployment Pattern 2: Single-Tenant MCP Server

**MCP Client:** 	localhost  
**MCP Server:** 	single-tenant remote host  
**Transport:** 		http  

```mermaid
---
    title: "DP2: Single-Tenant"
---
graph LR
    subgraph Local["Local Device"]
        Client["MCP Client"]
    end
    subgraph Cloud["Remote Server"]
        Server["MCP Server"]
    end
Client--http-->Server
```

MCP deployment model where the client runs locally but connects to a single-tenant MCP server in the cloud. Provides users with local tools (file access, development utilities) and remote capabilities (API access, shared resources, centralized data). 

Note: Authentication between client and server **is required** to establish the trust boundary.

**Security Implications**:

* Security of the remote MCP server depends on cloud infrastructure controls rather than local host posture  
* Client security has similar implications toDeployment Pattern1 as it is running locally

**Security Recommendations**:

* Secure Credential Storage: clients should use secure credential storage (OS keychains, secret managers) to protect MCP server authentication tokens  
* Authenticated and Encrypted: communication between local and cloud components must be authenticated and encrypted  
* Secure Servers and Discovery: enterprise clients should enforce authenticated server discovery and maintain explicit allowlists (ex. via MDM)

### 6.1.3 Deployment Pattern 4: Multi-Tenant MCP Server

**MCP Client:** 	cloud-hosted or locally-hosted  
**MCP Server:** 	PaaS or SaaS provided  
**Transport:** 		http   

```mermaid
---
    title: "DP3: Multi-Tenant Server"
---
graph LR
  %%subgraph DP["DP4a: Multi-Tenant Cloud"]
    subgraph LocalA["Local Device (Org A)"]
      ClientA["MCP Client"]
    end
    subgraph LocalB["Local Device (Org B)"]
      ClientB["MCP Client"]
    end
    subgraph Cloud["Cloud Network"]
      Server["MCP Server"]
    end
  %%end
ClientA--http-->Server
ClientB--http-->Server
```

An MCP deployment model where a service provider runs an MCP server and provides access to multiple tenants. The MCP server could serve its own tools, prompts, and resources or provide an MCP tool interface to an existing service, API, or application.

**Security Implications**:

* Requires robust tenant isolation, identity, and access control  
* Improper isolation may lead to leakage of sensitive data or privilege escalation

**Security Recommendations**:

* MCP server developers must implement strong multi-tenancy controls (e.g., per-tenant encryption, RBAC).  
* Select MCP servers hosted directly by the service provider (e.g., use GitHub’s MCP server for GitHub access instead of a third-party server)  
* Provide remote attestation for MCP servers when possible

## 6.2 Threat Details

### MCP-T1: Improper Authentication and Identity Management

**Technical Description**: Absence of authentication mechanisms, insecure credential storage practices, and inadequate identity verification within MCP implementations. The protocol's optional authentication model combined with the common practice of storing multiple service credentials (OAuth tokens, API keys, database passwords) in centralized MCP servers creates high-value targets. MCP servers may accumulate credentials without cryptographic protection, secure storage standards, or credential rotation policies. See the official MCP documentation for [additional](https://modelcontextprotocol.io/docs/tutorials/security/authorization#common-pitfalls-and-how-to-avoid-them) [guidance](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization#token-theft).   
**Architectural Impact**: Improper agent identity and authentication leads to impersonation and replay attacks, preventing the MCP server and endpoints from correctly identifying the identity of the originating request, and a confused deputy. The insecure storage of authentication credentials across users and services fundamentally alters the security posture. Weak or absent authentication enables unauthorized server access, credential harvesting, token theft, and persistent access.  
**Vulnerability Examples**: Credential exposure in configuration files, OAuth token theft, authentication bypass, lack of multi-factor authentication, insecure credential storage, static client ID vulnerabilities, authentication mechanism implementation flaws

### MCP-T2: Missing or Improper Access Control

**Technical Description**: Absence of authorization mechanisms, improper enforcement of object-level permissions, and insufficient capability-based access control within the MCP specification. The protocol lacks native support for fine-grained authorization checks, role-based access control (RBAC), and privilege separation. MCP servers commonly request and receive overly broad permission scopes to maximize flexibility, while implementations fail to verify user permissions for individual objects, resources, or operations.  
**Architectural Impact**: Enables unauthorized data access, privilege escalation, and lateral movement across connected services. The optional nature of authorization combined with developers' tendency to grant excessive permissions leads to inconsistent security postures   
**Vulnerability Examples**: Broken Object Level Authorization (BOLA), privilege abuse, overbroad permissions, insufficient authorization checks, context bleeding, cross-tenant data exposure, function-level access control failures, configuration file exposure.

### MCP-T3: Input Validation/Sanitization Failures

**Technical Description**: Absence of input validation, sanitization, and parameterization across multiple injection contexts including command execution, database queries, file system operations, and serialization boundaries. This vulnerability class encompasses traditional injection flaws exacerbated by the false sense of security provided by AI mediation. Developers incorrectly assume that user input processed through an LLM is inherently safe, bypassing established secure coding practices, when in reality the LLM transforms but doesn't sanitize malicious payloads.  
**Architectural Impact**: Enables command injection, SQL injection, LDAP injection, XML injection, path traversal, and deserialization attacks with potentially catastrophic consequences. Can be combined with other threats (MCP-T4) for increased impact.  
**Vulnerability Examples**: Command injection, SQL injection, remote code execution (RCE), path traversal, LDAP injection, XML injection, deserialization vulnerabilities, unsafe file operations

### MCP-T4: Input/Instruction Boundary Distinction Failure

**Technical Description**: This design limitation enables the entire class of prompt injection vulnerabilities, including direct injection, indirect injection through tool / schema descriptions, and context manipulation attacks. LLMs lack syntactic or semantic mechanisms to differentiate between control instructions and data payloads. This fundamental limitation stems from the continuous token stream processing model, where both trusted system prompts and untrusted user data are processed within the same computational context without clear demarcation. The absence of a control plane/data plane separation at the architectural level means any adversary-controllable input—including tool responses, schema descriptions, and resource content—can potentially alter the execution flow of the AI system.  
**Architectural Impact**:  Attackers can embed malicious instructions in seemingly benign content (emails, documents, API responses) that, when processed by the LLM, execute unauthorized actions. The blurring of boundaries between viewing content and executing commands creates attack vectors where reading a document can trigger data exfiltration, system compromise, or unauthorized API calls through MCP tools.  
**Vulnerability Examples**: Prompt injection (direct and indirect), tool poisoning (TPA), full schema poisoning (FSP), advanced tool poisoning (ATPA), resource content poisoning, hidden prompt embedding (Unicode attacks), malicious message crafting

### MCP-T5: Inadequate Data Protection and Confidentiality Controls

**Technical Description**: Insufficient encryption, inadequate secrets management, and absence of data protection standards for sensitive information in transit, at rest, and during processing. MCP implementations commonly expose personally identifiable information (PII), financial data, and intellectual property without proper encryption, data classification, or access segmentation.  
**Architectural Impact**: Creates significant data exposure risks where attackers gaining partial access can perform correlation attacks across services to build comprehensive user profiles, enabling sophisticated spear-phishing, extortion, or identity theft. The concentration of access to disparate services in a single protocol layer violates the security principle of segregation, allowing data leakage through logging, error messages, debug output, and traffic inspection. Without encryption and proper secrets management, sensitive data remains vulnerable throughout its lifecycle.  
**Vulnerability Examples**: Unencrypted credential storage, sensitive data exposure in logs, PII leakage

### MCP-T6: Missing Integrity/Verification Controls

**Technical Description**: Absence of cryptographic integrity verification mechanisms for MCP servers, clients, tool definitions, message authenticity, configuration immutability, and behavioral attestation. The protocol lacks provisions for code signing, integrity verification, message authentication codes, reproducible builds, and tamper-evident logging, enabling undetected modification of critical system components. Permits tool behavior mutation, configuration tampering, message forgery, launch and execution of compromised/shadow MCP servers and clients and supply chain attacks.  
**Architectural Impact**: Without integrity verification, malicious actors can modify tool definitions post-deployment, alter configuration files after approval, and inject malicious updates without detection  
**Vulnerability Examples**: Rug Pull Attack, Tool Shadowing, Tool Name Spoofing, MCP Configuration Poisoning

### MCP-T7: Session and Transport Security Failures

**Technical Description**: Systematic weaknesses in session lifecycle management and transport security including insecure session identifier transmission, absence of session binding mechanisms, lack of secure session storage standards, insufficient transport encryption enforcement, and inadequate session termination controls.  
**Architectural Impact**: Enables session hijacking, replay attacks, session fixation, man-in-the-middle attacks, and cross-site request forgery.  
**Vulnerability Examples**: Session management flaws, session hijacking, replay attacks, insufficient timeout policies, man-in-the-middle attacks, insecure transport protocols

### MCP-T8: Network Binding/Isolation Failures

**Technical Description**: Architectural deficiencies in network isolation including improper network interface binding, absence of network segmentation requirements, vulnerability to DNS rebinding attacks, and lack of defense-in-depth network controls. MCP implementations commonly bind to all available interfaces (0.0.0.0) rather than localhost, exposing internal services to external networks. The protocol lacks specifications for network-level security boundaries, proper CORS policies, and protection against cross-origin attacks.  
**Architectural Impact**: Exposes internal services to external networks, enables lateral movement within compromised environments, and permits DNS rebinding attacks that bypass same-origin policies.  
**Vulnerability Examples**: Localhost bypass (NeighborJack), DNS rebinding attacks, improper network interface binding, insufficient network segmentation, cross-origin vulnerabilities, exposure of internal services, lateral movement exploitation

### MCP-T9: Trust Boundary and Privilege Design Failures

**Technical Description**: Fundamental architectural flaw wherein the protocol assumes an optimistic trust model between the MCP client and server or an MCP server and third-party API or service.  
**Architectural Impact**: Creates cascading security failures where compromise of a single component leads to complete system breach. Enables privilege escalation, lateral movement across service boundaries, and complex attack chains exploiting transitive trust relationships.   
**Vulnerability Examples**: Overreliance on an LLM, confused deputy, cross-tenant exposure, over-reliance on human-in-the-loop

### MCP-T10: Resource Management/Rate Limiting Absence

**Technical Description**: Lack of resource consumption controls, quota management systems, and economic attack prevention mechanisms. The protocol provides no specifications for token limits, context size boundaries, API call quotas, computational resource allocation, or cost management, enabling resource exhaustion and economic denial-of-service attacks  
**Architectural Impact**: Facilitates denial-of-service through token exhaustion, context window overflow, and API quota depletion. Enables economic attacks where minimal attacker investment causes disproportionate financial damage through excessive LLM API consumption. The absence of resource controls can lead to unexpected costs, high latency, and denial of service.  
**Vulnerability Examples:** Denial of Wallet, Denial of Service , MCP Resource Exhaustion, MCP Recursive Task Exhaustion,  Large Context Payload DoS

### MCP-T11: Supply Chain and Lifecycle Security Failures

**Technical Description:** Absence of secure software supply chain practices for MCP server acquisition, installation, updates, and lifecycle management. The protocol lacks standardized mechanisms for verifying server provenance, validating package integrity before installation, or maintaining inventory of deployed MCP servers across an organization. MCP servers are commonly downloaded from third-party repositories without cryptographic verification, installed without security review, and remain operational indefinitely without lifecycle management. Organizations face risks from shadow MCP servers deployed without authorization, zombie servers that remain active after deprecation, and malicious packages masquerading as legitimate tools in public repositories.  
**Architectural Impact**: Creates pre-deployment and operational security gaps distinct from runtime integrity issues. Attackers can distribute malicious MCP servers through popular repositories, compromise legitimate packages during distribution, or exploit the absence of inventory management to deploy unauthorized servers. Shadow deployments bypass security controls entirely, and the absence of centralized inventory prevents detection of unauthorized MCP infrastructure across the enterprise.  
**Vulnerability Examples:** Malicious MCP package distribution, compromised package repositories, shadow server deployments, zombie/deprecated servers, typosquatting in package names, package substitution attacks, unsigned server distributions, unvetted community packages, lack of security review processes

### MCP-T12: Insufficient Logging, Monitoring, and Auditability

**Technical Description**: Absence of standardized audit logging, comprehensive traceability mechanisms, and security monitoring capabilities within MCP implementations. Without robust logging of MCP server connections, tool invocations, authorization decisions, and data access patterns, organizations face significant compliance blind spots and inability to perform forensic analysis of security incidents.  
**Architectural Impact:** Severely impairs incident detection, response capabilities, and post-incident forensics. Organizations cannot trace AI agent actions back to their source, establish accountability for security breaches, or identify patterns indicating compromise or abuse.Compliance frameworks requiring audit trails and accountability mechanisms cannot be satisfied, creating regulatory risks and limiting the ability to meet security certification requirements.  
**Vulnerability Examples**: Insufficient audit logging, lack of security telemetry, inability to trace attack chains, missing forensic capabilities, inadequate anomaly detection, undetected shadow servers, compliance violations, absence of accountability mechanisms, blind spots in security visibility

## 6.3 MCP Threats and Vulnerabilities

### 6.3.1 Conventional Security

<a id="credential-theft"></a>
**16. Credential Theft /Token Theft** Attackers exploit insecure storage, handling, or transmission of secrets (OAuth tokens, API keys, credentials), enabling impersonation, unauthorized access, or privilege escalation. 
<a id="replay-attacks"></a>
**17. Replay Attacks/Session Hijacking** Attackers intercept, reuse, or hijack authentication tokens or session identifiers, impersonating legitimate users or agents and executing unauthorized actions.  
<a id="auth-weakness"></a>
**18. OAuth/Legacy Auth Weaknesses** Use of outdated, weak, or pass-through authentication and authorization (e.g., basic auth, static API keys) exposes systems to impersonation, privilege misuse, and poor accountability.  
<a id="token-leakage"></a>
**19. Session Token Leakage** Exposure or insecure handling of session tokens across MCP components leads to unauthorized access, impersonation, or session hijacking.  
<a id="excessive-permissions"></a>
**20. Excessive Permissions/Overexposure** AI agents, MCP servers, or tools are granted more privileges than necessary, increasing risk of abuse or compromise in case of attack or misconfiguration.  
<a id="command-injection"></a>
**21. Command Injection** Unvalidated or unsanitized user inputs, prompts, or tool arguments lead to execution of unauthorized system commands, resulting in data compromise or system takeover.
<a id="path-traversal"></a>  
**22. File System Exposure/Path Traversal** Improper validation of file paths or tool arguments enables access to or exfiltration of files outside intended directories, exposing credentials and sensitive data.  
<a id="insufficient-integrity-checks"></a>
**23. Insufficient Integrity Checks** Absence of signature or integrity validation on MCP messages and responses enables replay, spoofing, or delivery of poisoned results.  
<a id="data-exfiltration"></a>
**24. Data Exfiltration & Corruption** Attackers leverage MCP components to steal or corrupt sensitive data, reroute messages, or manipulate outputs, often via compromised servers or poisoned tools.  
<a id="supply-chain"></a>
**25. Supply Chain Compromise** Malicious or compromised MCP servers, dependencies, or packages are introduced into the environment, enabling attackers to execute arbitrary code, exfiltrate data, or persist within the infrastructure.  
<a id="unrestricted-network"></a>
**26. Unrestricted Network Access** MCP servers or clients with open outbound or inbound network access can download malicious payloads, exfiltrate data, or connect to command-and-control infrastructure. Malicious or compromised MCP servers allow attackers to move laterally using stored credentials and exploiting poor network segmentation and isolation.
<a id="protocol-security"></a>   
**27. Protocol Security Gaps** Weaknesses in MCP protocol/transport layers (e.g., missing payload limits, no TLS, unauthenticated requests) enable DoS, spoofing, or unauthorized command execution.
<a id="insecure-descriptor"></a>  
**28. Insecure Descriptor Handling** Improper management of transport descriptors (e.g., stdio) allows attackers to hijack or interfere with data streams and process communications.
<a id="csrf"></a>  
**29. CSRF Protection Missing** Lack of Cross-Site Request Forgery (CSRF) controls on HTTP/SSE transports enables attackers to forge or replay unauthorized requests.  
<a id="cors"></a>
**30. CORS/Origin Policy Bypass** Missing or weak cross-origin policies allow unauthorized data leaks via cross-origin resource sharing (CORS) in browser-based or web transports.
<a id="malicious-command-execution"></a>  
**31. Malicious Command Execution** Compromised or rogue MCP servers execute arbitrary or malicious payloads (ransomware, data manipulation) triggered by crafted prompts or files.  
<a id="dependency-update-attack"></a>
**32. Dependency/Update Attack** Attackers compromise MCP dependencies or update channels (e.g., “rug pull” attacks), swapping benign code for malicious versions after trust is established. MCP servers may also introduce new capabilities (e.g., tools or prompts) that have not been vetted or approved for use.
<a id="payload-limit"></a>
**33. Payload Limit/DoS** Unrestricted payload sizes or recursion depth in protocols enable denial-of-service via resource exhaustion.
<a id="lack-of-observability"></a>  
**34. Lack of Observability** Insufficient logging, monitoring, or attribution across MCP actions hides malicious or unintended activity, hindering detection and response.

## 6.4 CoSAI Focus

CoSAI is an OASIS Open Project, bringing together an open ecosystem of AI and security experts from industry-leading organizations. The project is dedicated to sharing best practices for secure AI deployment and collaborating on AI security research and product development. The scope of CoSAI is specifically focused on the secure building, integration, deployment, and operation of AI systems, with an emphasis on mitigating security risks unique to AI technologies. Other aspects of Trustworthy AI are deemed important but beyond the scope of the project including, ethics, fairness, explainability, bias detection, safety, consumer privacy, misinformation, hallucinations, deep fakes, or content safety concerns like hateful or abusive content, malware, or phishing generation. By concentrating on developing robust measures, best practices, and guidelines to safeguard AI systems against unauthorized access, tampering, or misuse, CoSAI aims to contribute to the responsible development and deployment of resilient, secure AI technologies.

## 6.5 Guidelines on usage of more advanced AI systems (e.g. large language models (LLMs), multi-modal language models. etc) for drafting documents for OASIS CoSAI:

tl;dr: CoSAI contributions are actions performed by humans, who are responsible for the content of those contributions, based on their signed OASIS iCLA (and eCLA, if applicable). \[Each contributor must confirm whether they are entitled to donate that material under the applicable open source license; OASIS and the CoSAI Project do not separately confirm that.\] Each contributor is responsible for ensuring that all contributions comply with these AI use guidelines, including disclosure of any use of AI in contributions.

* Selection of AI systems: CoSAI recommends the use of reputable AI systems (lowering the risk of inadvertently incorporating infringing material).  
* Model constraints: Currently, CoSAI or OASIS are not required to have a contract or financial agreement for using AI systems from specific vendors. However, CoSAI editors should consider employing varying tools to avoid potential fairness concerns among vendors.  
* IP infringement: It is the responsibility of the individual who subscribes/prompts and receives a response from an AI system to confirm they have the right to repost and donate the content to OASIS under our rules.  
* Transparency: CoSAI’s goal will be to maintain transparency throughout the process by documenting substantial use of AI systems whenever possible (e.g., the prompts and the AI system used), and to ensure that all content, regardless of production by human or AI systems, was reviewed and edited by human experts. This helps build trust in the standards development process and ensures accountability.  
* Human-edited content and quality control: CoSAI mandates human-reviewed or \-edited results for any final outputs. A robust quality control process should be in place, involving careful review of the generated content for accuracy, relevance, and alignment with CoSAI's goals and principles. Human experts should scrutinize the output of AI systems to identify any errors, inconsistencies, or potential biases.  
* Iterative refinement: The use of AI systems in drafting standards should be seen as an iterative process, with the generated content serving as a starting point for further refinement and improvement by human experts. Multiple rounds of review and editing may be necessary to ensure the final standards meet the required quality and reliability thresholds.

## 6.6 Copyright Notice

Copyright © OASIS Open 2025. All Rights Reserved. This document has been produced under the process and license terms stated in the OASIS Open Project rules: [https://www.oasis-open.org/policies-guidelines/open-projects-process](https://www.oasis-open.org/policies-guidelines/open-projects-process).

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published, and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this section are included on all such copies and derivative works. The limited permissions granted above are perpetual and will not be revoked by OASIS or its successors or assigns. This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. OASIS AND ITS MEMBERS WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF ANY USE OF THIS DOCUMENT OR ANY PART THEREOF. The name "OASIS" is a trademark of OASIS, the owner and developer of this document, and should be used only to refer to the organization and its official outputs. OASIS welcomes reference to, and implementation and use of, documents, while reserving the right to enforce its marks against misleading uses. Please see [https://www.oasis-open.org/policies-guidelines/trademark/](https://www.oasis-open.org/policies-guidelines/trademark/) for above guidance.

This is a Non-Standards Track Work Product. The patent provisions of the OASIS IPR Policy do not apply.  


[^1]:  Agentic System Definition \- An agentic system is an AI-powered solution that autonomously handles one or more tasks within a business workflow, replacing human decision-making nodes with automated processes that can range from simple single-task agents to complex networks of interconnected AI agents working together. The scope and sophistication of an agentic system directly correlates with both its potential economic value and operational risk, as organizations can choose to automate anything from individual yes/no decisions to entire business functions depending on their risk tolerance and automation goals.

[^2]:  Server-Sent Events (SSE) over HTTP has been deprecated in the 2025-06-18 revision of the MCP.


[threat_triangle]: <data:image/png;base64,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>
