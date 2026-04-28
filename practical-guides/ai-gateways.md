# Practical Guides for Secure AI Gateways Design and Implementation

## Overview

With the addition of AI Agents and MCP servers in architecture landscapes, the complexity and the security risk introduced is directly proportional with the amount of required connections between Agents and MCP Servers. 
Implementation of best practices, standardization, and enforcement of security controls while introducing the ability to control and monitor for visibility becomes cumbersome with a high fragmentation approach.

The purpose of this page is to introduce best practices and recommendations for designing and implementing Gateways in the context of the AI Landscape, in which specialized functionalities are required to managed the complexities introduced by the AI systems such as: identification, authentication and authorization of the agents, delegation and autonomy control, routing and protocol mediation, filtering and traffic control, human in the loop enforcement, context lifecycle policies, memory-safety boundaries, tool & function call control, behavior & policy enforcement, security controls & self-healing and observability.

## API Gateways vs AI Gateways

Traditionally, API Gateways have been used as a single entry point for managing and securing access to API consumers in distributed architectures. They provide functionalities such as traffic management, request routing, protocol translation, protection of the endpoints via authentication/authorization mechanisms, rate limiting, and observability.

Within the AI Landscape the gateways have to cover new functionalities given by new types of interactions, such as user to LLM, agent to tool, MCP requests, and the new attack surfaces introduced by the AI systems. The AI systems are introducing new capabilities such as autonomy, delegation, reasoning, dynamicity, and the ability to interact with tools and external systems which are not covered by traditional API Gateways.

These new capabilities introduce new attack surfaces, such as uncontrolled autonomy, unmonitored tool access, misuse of permissions, or manipulation of system instruction, that traditional security infrastructures are not designed to monitor or defend against. 

The key challenges introduced are:
- Threats living in language not only in the endpoints, which can lead to:
  - Context Injection and Manipulation
  - Memory Poisoning
  - Tool Poisoning Attacks
  - Servers Compromise and Credentials Harvesting
- Lack of predictability as AI systems now initiate their own autonomous actions which can lead to:
  - Non Deterministic Policy Evaluation
  - Behavioral Drift, Rogue Actions due to the nature of the AI Systems, the Load or due to Hallucinated function calls 
  - Abuse of Delegation Mechanisms 
  - Privilege Escalations 
  - Unauthorized Actions
  - Schema Violations
  - Sensitive Data Disclosure
- Some actions are too risky to be fully automated, requiring Built-in Approval Workflows for humans-in-the-loop
- MCP Servers are mandated to be discoverable, the gateways having to enable self registration mechanisms which can lead to:
  - Unverified, untrusted registrations 
  - Observability without exposing Sensitive Data
  - Cross session data leakage
  - Audit Invisibility


## AI Landscape Reference Architecture

*Add Diagram*

With the above reference architecture depicting the ecosystem of users, autonomous agents, enterprise systems, models and tooling the AI landscape is bringing to the table, it is imperative to list and highlight the new capabilities which have to be introduced to ensure consistency, trust, security, governance  and the  interoperability of the systems.

## Capabilities of AI Gateways

As highlighted in the above use cases, with the AI landscape, the existing capabilities have to be adapted and new capabilities have to be introduced for the Gateways to manage:

### Foundational Capabilities Inherited from Traditional API Gateways

- **Unified Access Point**: Centralized entry point for secure access to multiple LLM APIs, models, and AI services approved by the organization
- **Authentication and Authorization**: Integration with OAuth2, JWT, mTLS, and API keys for controlling access to AI models
- **Credential Management**: Centralized key lifecycle management (tracking, revocation, refresh) to eliminate API key sprawl and enhance security
- **Consumption Control**: Rate limiting and provider-specific/client-specific quotas to manage costs and prevent abuse
- **Observability**: Tracking of token usage, quotas, error rates, and access logs across LLM providers with correlation IDs
- **Enrichment**: Request/response transformation for usage reporting, context injection, and response filtering
- **Canonical LLM API Definition**: Abstraction layer that maps client requests to multiple provider-specific implementations

### AI-Specific Security & Governance Capabilities

- **Agent Identity & Delegation Chaining**: Binds requests to verifiable human, system, or agent identity with ephemeral, role-based access control and multi-level delegation chains
- **Delegation & Autonomy Control**: Limits how, when, and to what extent agents can delegate, spawn, or act autonomously
- **Prompt & Context Security**: Detects and neutralizes prompt injection, jailbreaks, and sensitive data leakage in prompts, context, and memory
- **Memory & Data Governance**: Controls AI data retention, lifecycle policies, redaction in embeddings, and memory-safety boundaries
- **Tool & Function Call Control**: Restricts AI tool access through explicit allowlisting and strict schema validation with policy-bound constraints
- **Behavior & Policy Enforcement**: Dynamic, risk-aware policy controls over agent reasoning, chain-of-thought safety, and detection of risky action patterns
- **Human in the Loop Enforcement**: Risk-scoring and approval workflows inserting mandatory human oversight for high-risk AI decisions
- **AI-Specific Threat Detection**: Input sanitization, token counting, prompt abuse detection, and malicious usage pattern detection
- **Non-Determinism Containment**: Constrains AI unpredictability through deterministic modes and stability monitoring
- **Security Controls & Self-Healing**: Continuous detection and automatic isolation/remediation of AI-specific threats (injection attacks, jailbreaks, unsafe calls)
- **Registration & Discovery**: Catalogs, versions, and classifies agents, tools, models, and MCP servers by trust level and capability with controlled registration mechanisms
- **Routing & Protocol Mediation**: Multimodal routing across User→LLM, Agent→Tool, and MCP requests while maintaining session awareness

## Implementation Considerations & References

*WIP*

### Plugin Based Extensibility

- Extensible plugin architecture for custom authentication, policy enforcement, and threat detection modules

- Tooling: kgateway.dev, Kong MCP GW, OpenRouter, LiteLLM,..

### Policy Attachment Model & Configuration Scope

Strict policy scoping prevents accidental AI policy application to invalid backends and enables fine-grained control over AI-specific behaviors to mitigate drifts and unintended consequences

Tooling: Kong MCP GW, OpenRouter, LiteLLM, kgateway.dev, Kuadrant MCP-Gateway, AgentGateway, Operant AI MCP Gateway, Microsoft MCP Gateway, Docker MCP Gateway, Lasso MCP Gateway, solo.io AgentMesh, Kagenti MCP-Gateway, Amazon Bedrock AgentCore, Google CAPSEM

### Data Plane Separation

 Out-of-process design allows independent scaling and development of AI-specific logic 

### Credential Management

Multiple auth patterns needed to support various deployment scenarios and security postures


## AI Gateways References

*WIP*

- EnkryptAI : Secure MCP Gateway
- AgentGateway
- IBM : Context Forge
- mcp.run
- Operant AI : MCP Gateway
- AgentGateway : AgentGateway
- Microsoft : MCP Gateway
- Docker : MCP Gateway
- Lasso : MCP Gateway
- solo.io : AgentMesh
- Kagenti : MCP-Gateway
- Amazon Bedrock AgentCore
- Kong MCP GW
- Google : CAPSEM
- OpenRouter, 
- LiteLLM,
- https://kgateway.dev/ 
- https://github.com/Kuadrant/mcp-gateway 
