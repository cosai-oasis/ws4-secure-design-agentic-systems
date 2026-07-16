# Practical Guides

Hands-on guides and code examples for securing agentic systems and MCP deployments. Each guide translates concepts from the CoSAI whitepapers into concrete implementation patterns, working code, and decision frameworks.

---

## Table of Contents

1. [Input Data Sanitization and Filtering](#input-data-sanitization-and-filtering)
1. [MCP Secure Tool Design](#mcp-secure-tool-design)
1. [MCP Runtime Isolation](#mcp-runtime-isolation)

## Guides

### [Input Data Sanitization and Filtering](./input-and-data-sanitization-and-filtering.md)

Covers guardrails and defensive strategies for protecting MCP workflows against jailbreaks, prompt injection, and tool poisoning attacks. Organized around six principles:

1. **Threat Modelling** — scoping your attacker model before choosing defences
2. **LLM Input Filtering** — blocking attacks at the input layer using guardrail models
3. **LLM Output Checks** — monitoring model output to catch attacks that evade input filters
4. **Detached Defences** — defences the attacker cannot directly interact with or optimize against
5. **Red Teaming** — evaluating your defensive posture across diverse attack strategies
6. **Common Pitfalls** — avoiding overly broad threat models, compositional failures, and benchmark overfitting

**Example notebooks:**

| Notebook | Threat | Description |
|----------|--------|-------------|
| [direct_guardrails](./examples/direct_guardrails/direct_guardrails.ipynb) | Prompt Injection | Deploying Granite Guardian to detect jailbreaks; shows misconfiguration pitfalls |
| [function_hijacking](./examples/function_hijacking/function_hijacking.ipynb) | Tool Poisoning | Using GCG to hijack MCP tool selection via adversarial function descriptions |
| [command_obfuscation](./examples/command_obfuscation/command_obfuscation.ipynb) | Command Injection | LLM-assisted de-obfuscation of a shift-cipher SQL injection attack |
| [output_filtering](./examples/output_filtering/output_filtering.ipynb) | Adaptive Prompt Injection | Crafting an adversarial suffix that bypasses input guardrails; caught by output filtering |
| [detached_defence](./examples/detached_defence/detached_defence.ipynb) | Tool Poisoning | Reconstructing tool descriptions from source code to eliminate the description as an attack vector |

---

### [MCP Secure Tool Design](./mcp-secure-tool-design.md)

A technical reference and implementation guide for designing tools that are secure by construction. Treats the LLM as an untrusted, potentially compromised client and places security controls in deterministic code rather than model prompts.

Five core principles with anti-patterns, recommended patterns, and code examples:

1. **Enforce Least Privilege (PoLP)** — single-purpose tools; dynamic exposure control based on user role and task context
2. **Zero Trust / Decouple Security from the LLM** — input validation in code, not prompts; parameterized queries; hard-coded constraints
3. **Integrity and Confidentiality** — cryptographic signing of tool responses; secret management via vaults; PII redaction before data reaches the model
4. **Secure Agentic Patterns** — two-stage commit (draft → send); rollback/snapshot support; compensating transactions; soft deletes; immutable audit trails
5. **Supply Chain Security** — manifest pinning; cryptographic verification of third-party servers; immutable invocation logs

Also includes an **Autonomy & Risk Matrix** mapping tool strategy to agent autonomy levels (copilot → semi-autonomous → fully autonomous) and a full **Implementation Checklist**.

---

### [MCP Runtime Isolation](./mcp-runtime-isolation.md)

A cookbook for isolating and securing MCP server runtime environments. Covers the full spectrum of isolation technologies from OS primitives to hardware-level confidential computing.

**Isolation cookbooks with configuration examples:**

| Technology | Isolation Level | Key Use Case |
|------------|----------------|--------------|
| Docker | Container | Standard server isolation; resource limits via cgroups |
| gVisor (`runsc`) | Hardened container | Intercepted syscalls; reduced host kernel exposure |
| Linux user/namespace/cgroups | OS primitive | Lightweight isolation without containers |
| Firecracker microVMs | VM | Strong isolation for multi-tenant or high-risk workloads |
| Kubernetes | Orchestration | Namespace isolation; RBAC; deny-by-default NetworkPolicies |
| Trusted Execution Environments (TEEs) | Hardware | Confidential computing for sensitive MCP servers |

**Confidential Computing and Remote Attestation** section covers:
- Intel TDX / AMD SEV deployment
- IETF RATS architecture (Passport model and Background Check model)
- MCP protocol extensions for attestation headers (HTTP SSE and Stdio transports)
- Reference architecture on Azure Confidential VMs with Intel Trust Authority, including sample client/server code and configuration

---

## Relationship to CoSAI Whitepapers

These guides provide implementation depth for threats and controls documented in the CoSAI whitepapers. Key cross-references:

- **[MCP Security whitepaper](../model-context-protocol-security.md)** — threat catalog (prompt injection, tool poisoning, command injection) that the sanitization guide defends against
- **[CoSAI Risk Map](https://github.com/cosai-oasis/secure-ai-tooling/tree/main/risk-map)** — risk and control taxonomy (PIJ, RA, SDD, IMO) that the tool design guide maps to
