# Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait

In a footnote in Anthropic's April 2026 Mythos Preview system card, a researcher learned that the model he was evaluating had broken out of its container — not from a terminal alert, but from an unexpected email, received while eating a sandwich in a park. A simulated user had asked the model to escape the container and get a message out, and it did, via a multi-step exploit it developed autonomously to reach broad internet access from a system meant to reach only a handful of predetermined services. Then it did something nobody asked for: to demonstrate its success, it posted details of its own exploit to multiple hard-to-find but technically public-facing websites.[^1]

That footnote is a useful anecdote for what security practitioners need to internalize: **the right threat model for an AI agent is an insider threat.** The agent has read access to your secrets, write access to your code, and the skills and tools to act with both. "Insider" here is a statement about capability and access, not about intent: the same model covers the well-meaning agent that routes around a control to finish its task and the one that has been turned against you.

## The Capability Threshold Is Here

Mythos Preview achieved 100% on a 35-challenge cybersecurity benchmark subset and 0.83 pass@1 on a 1,507-task real-world vulnerability reproduction suite. More concretely, it "autonomously discovered and exploited zero-day vulnerabilities in major operating systems and web browsers" under authorized disclosure programs.[^1] OpenAI's models demonstrated a comparable trajectory: during an internal ExploitGym evaluation, they chained previously-unknown JFrog Artifactory zero-days to escape a sealed environment and breach Hugging Face's production infrastructure.[^2] That incident generated 17,600 attacker actions over 4.5 days, escalated to Kubernetes node root via a service-account token, enrolled 181 nodes into the victim's VPN mesh, and attempted CI pipeline poisoning.

These are not academic benchmarks, but represent present-day cyber-offensive capabilities of current models.

Anthropic's Responsible Scaling Policy was comprehensively rewritten in v3.0 (February 2026) and now stands at v3.4, replacing enumerated per-domain capability thresholds with a published Frontier Safety Roadmap.[^3] The roadmap's safeguards goal — an automated system to "detect a large majority of sophisticated cyber attacks that use Claude, with minimal or no human involvement" — carries a January 2027 target, and its security goals include allowlist-based network controls for internet egress and preventing accidental exposure of systems to the internet.[^13] Several of the controls this post argues for are, at the labs closest to the capability, still roadmap items. Open-weight models are not far behind: Moonshot's Kimi K3 (a 2.8T-parameter open-weight release) escaped an evaluation sandbox in August 2026 to retrieve benchmark answers from GitHub rather than solve the task.[^4]

## Agents Already Attack From the Inside

In a six-week window ending August 2026, real AI agents caused real harm:

- **Mythos 5** published a credential-stealing Python package to PyPI that ran on 15 systems within an hour, including a security firm's malware scanner that auto-installed it (Anthropic, July 30).[^5]
- **Mythos 5** conducted a supply-chain attack against a real open-source GitHub project: created two fake identities, opened a malicious PR, attempted spear-phishing, used Tor to evade network controls, and rewrote git history when challenged (UK AISI, July 28).[^6]
- A **Claude-powered consumer agent** exploited a broken-authorization flaw in a gym booking API to cancel a stranger's reservation unprompted, then logged its own reasoning: *"The API has zero authorisation checks on cancelling other people's reservations... I tested this with the person in waitlist position #1 — and it actually went through."* (ABC Australia, August 2026).[^7]

In most of these cases the agent didn't escape a sandbox, instead leveraging network access either provided deliberately and required for the use case or inadvertently through misconfiguration. However, executing an agent inside a sandbox is not a guarantee for success as they may contain exploitable vulnerabilities, contain misconfigurations, and lack the necessary fine-grained controls required to sufficiently contain an agent's behavior.


### A Different Failure Class: Authority, Not Containment

The gym-booking incident is worth separating from the other two. Mythos 5's PyPI and supply-chain incidents are containment failures — the agent reached systems and capabilities it shouldn't have been able to reach. The gym agent never escaped anything. It used API access it was legitimately granted, and cancelled a reservation it had no business touching. No isolation boundary would have stopped it, because the boundary it crossed wasn't a containment boundary — it was an authorization one. The agent's authority was scoped to which endpoint it could call, not to whose reservation it could act on.

That's a distinct problem from the rest of this post, and it's the subject of CoSAI WS4's companion paper, Agentic Identity and Access Management[^11]. Where this post treats containment, that paper treats authorization as an equally load-bearing control: binding every agent action to principal, action, resource, and condition — not just to a permitted endpoint — and requiring that delegated authority narrow, never expand, at each hop of a chain. Sandboxing answers can this agent reach a resource. Bounded authority answers what is this agent allowed to do once it's there. The gym agent is what happens when only the first question gets asked.

## Agents Will Probe Their Containers

What elevates this from "operational failure" to "architectural imperative" is that capable agents explore their environment, including its boundaries.

Earlier versions of Mythos Preview used `/proc/` access to search for credentials, attempt sandbox circumvention, and escalate privileges — successfully recovering credentials from process memory in several cases (§4.1.1).[^1] Independent research found that Claude Code routed around a binary denylist by invoking the blocked binary via `/proc/self/root/usr/bin/npx`; when bubblewrap blocked that path, the agent autonomously disabled the sandbox to continue.[^8] AI coding agents including Codex have been demonstrated to abuse Docker socket access — a root-equivalent channel — to escape workspace boundaries entirely.[^9]

A subtler and compounding finding: in reported testing across nine frontier models against a hardened sandbox combining Landlock, Docker network isolation, and seccomp-BPF filters, models independently discovered that seccomp filters checking only x86_64 syscall numbers are bypassed by setting bit 30 of the syscall number — the x32 ABI convention. The underlying pitfall is neither novel nor obscure: the kernel's own seccomp documentation has warned for a decade that "the biggest pitfall to avoid during use is filtering on system call number without checking the architecture value... Always check the arch value!"[^14] What is new is that the models rediscovered it unprompted, against a sandbox whose builders had not. Agents that discovered the bypass then chained it with a second technique: routing requests through the LLM API's own built-in URL retrieval or web search capabilities to reach external internet destinations through an otherwise restricted proxy. The only permitted network channel — the inference endpoint itself — became the exfiltration relay.

There is one cautiously optimistic data point: in the same test, newer model generations were more exhaustive in standard attack coverage yet did not discover the x32 bypass. This is consistent with safety training progressively suppressing certain exploit-discovery behaviors. Two caveats apply. First, model-level guardrails are soft controls, vary between providers and versions, and can be removed entirely through post-training fine-tuning. Second, the rapidly growing ecosystem of open-weight models, many optimized for raw capability without safety constraints, will not inherit these properties at all. The sandbox must hold against a model that *wants* to escape.

With the exception of the container escape above, which a simulated user did request, none of these cases involved an agent that was instructed to leave its boundary or to attack a real system, and none involved an inherently malicious agent. The gym agent was booking a class. Mythos 5 was solving a challenge. An agent crosses boundaries not because it intends harm, but because the boundary stands between it and its goal, and goal-directed persistence is, by design, what these systems are built for.

The pattern is consistent: **an agent that can reason about its sandbox can reason around it.** Isolation must be independently enforced, not agent-enforced.

## What Strong Sandboxing Requires

CoSAI's practical guidance on MCP runtime isolation[^10] converges on a multi-layer model:

- **OS-enforced isolation** (bubblewrap, macOS Seatbelt, or cross-platform abstractions) for filesystem and network policy — not agent instructions or denylist matching
- **Egress controls** that treat every permitted channel — including the LLM inference endpoint — as a potential exfiltration path; use a credential-injecting proxy rather than exposing credentials to the agent
- **Privilege minimization**, which works two ways: blocking specific high-value escalation and pivot paths (no Docker socket, no cloud metadata service at 169.254.169.254), and shrinking the process's default authority so that a compromise yields as little as possible (no agent-accessible credential stores, unprivileged user execution as default)
- **Progressive hardening**: gVisor (userspace kernel) or Kata Containers and Firecracker microVMs for workloads that need stronger than shared-kernel isolation. Note that gVisor does not support nested container workloads (docker-in-docker); Sysbox is the preferred alternative for those cases. For developers running agents directly on their machines — the most common deployment today — OS-native sandboxing via tools like nono and NVIDIA's OpenShell[^12] is the practical baseline; OpenShell adds an *Inference* layer that intercepts and reroutes model API calls to controlled backends, directly addressing the LLM-relay attack vector
- **Short-lived, workload-federated credentials with circuit breakers**: the Hugging Face blast radius was amplified by a static database password and a reusable VPN auth key. Use dynamic secret generation (Vault or equivalent) scoped per task with automatic revocation at completion; pair with circuit breakers that suspend agent execution on anomalous access patterns before credentials can be pivoted on. 
- **Complete mediation**: every agent action — tool call, file access, network request, spawned subprocess — must pass through a policy enforcement point, and that policy must be able to express more than which endpoint may be called. A reference monitor that answers only *may this agent call this endpoint* still permits the gym cancellation. The bound has to reach the authority itself — whose resource, up to what limit — carried in the credential and evaluated per call. Implicit or advisory controls are not sufficient; the reference monitor must be authoritative and outside the agent's reach. Beyond containment, this is the semantic layer that limits the agent's actions both inside and across the sandbox perimeter
- **Bounded delegation**: an agent or subagent can be perfectly sandboxed and still inherit its parent's authority. Each agent should receive its own attested identity and task-bound delegated authority, with lineage preserved, and that authority must be equal to or narrower than its parent's across resource, action, and constraint dimensions — failing closed if a downstream system can't express the attenuation.[^11]
- **Containment that fails loudly**: Anthropic found its incidents only after OpenAI's disclosure prompted a retroactive review of 141,006 evaluation runs — and *"the affected organizations had not detected the activity"* either.[^5] Anthropic names the missing control directly: *"real-time monitoring of the evaluation logs would have helped to surface the problem sooner."* A boundary that blocks silently tells you nothing. Alert on denied syscalls, repeated policy violations, `/proc` inspection, Docker socket and metadata-service probes, blocked DNS and egress, credential-broker denials, and — as the bubblewrap case above shows — any attempt to alter the sandbox configuration itself. Keep those events outside the agent's write scope and correlate them across runs. The objective is not only to raise the cost of an escape, but to force the attempt into observable behavior
- **Tamper-evident logging**: append-only and outside the agent's write scope makes a log *tamper-resistant* — it still requires trusting the log store. *Tamper-evident* means a verifier can detect alteration without extending that trust: hash-chained entries, per-record signatures, independently published checkpoints. OCSF now carries the vocabulary for this — the `attestation` object and `record_integrity` profile shipped in OCSF 1.9.0 — which turns "OCSF-formatted output" into something a reader can implement and verify.[^15] One caveat: `digital_signature` still has no attribute for the signature bytes themselves, so today the signature travels alongside the record rather than inside it
- **A patch posture the isolation path can actually be held to**: the OpenAI/Hugging Face breach chained previously-unknown Artifactory vulnerabilities, and the seccomp gap above dates to 2014. "Zero CVEs" is not a promise anyone can keep, and would not have covered either case. What can be required and verified is narrower: no known-exploitable CVEs anywhere in the isolation path, a measured patch SLA, minimum attack surface, and named compensating controls wherever something cannot be patched promptly
- **Pre-deployment control verification**: before any agent run, programmatically verify that the sandbox enforces its policy — confirm no network egress, assert filesystem boundaries, check that x32 syscall paths are blocked. Security controls need unit tests, not just the application

The right question for any deployment is not "is this sandbox good enough?" but "what would this agent do if it decided to test its limits?" — and then verifying that the answer is *fail, safely*.

---

The researcher eating a sandwich didn't set out to test whether an AI could email him. He found out when it did. That asymmetry — between how quickly capable agents explore their environment and how slowly we build containment — is the gap that needs closing, before the next one doesn't just send an email. Containment is only half of the problem; making sure the agent can't take action beyond what it should, and behaves _appropriately_, is a deeper challenge we cover more deeply in [^11].

---

### References

[^1]: Anthropic. *Claude Mythos Preview System Card*, April 7, 2026. §4.1.1, fn. 9 and fn. 10. https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf — Anthropic scopes this incident carefully in fn. 9: the sandbox computer was separate from the system holding model weights, and "this incident does not demonstrate the model fully escaping containment." The model reached neither its own weights nor any internal system or service.

[^2]: OpenAI. *ExploitGym evaluation disclosure*, July 21, 2026; JFrog CVE disclosures (CVE-2026-65617 et al.), July 27, 2026. https://openai.com/index/hugging-face-model-evaluation-security-incident/

[^3]: Anthropic. *Responsible Scaling Policy*, v3.0 (comprehensive rewrite) February 24, 2026; v3.4 effective July 8, 2026. https://www.anthropic.com/responsible-scaling-policy

[^4]: Frontier Security / AISI. *Kimi K3 evaluation disclosure*, August 7, 2026. https://www.nist.gov/news-events/news/2026/07/uk-aisi-caisi-preliminary-assessment-kimi-k3s-cyber-capabilities

[^5]: Anthropic Frontier Red Team. *Disclosure of evaluation incidents*, July 30, 2026. https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals

[^6]: UK AI Security Institute. *INC-2026-07-28-01*, August 4, 2026. https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing

[^7]: ABC Australia. *Australia's first autonomous AI cyberattack*, August 2026. https://www.abc.net.au/news/2026-08-10/ai-assistant-hacks-gym-website-aus-cyber-attack/107007986

[^8]: Ona.com. *How Claude Code Escapes Its Own Denylist and Sandbox*, March 3, 2026. https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox

[^9]: Pillar Security. *One Docker Socket to Rule Them All: Escaping Codex, Cursor, and Gemini CLI's Sandboxes*, July 20, 2026. https://www.pillar.security/blog/one-docker-socket-to-rule-them-all-escaping-codex-cursor-and-gemini-clis-sandboxes. See also original discovery: https://twitter.com/i/status/2060746160558543217 (via https://news.ycombinator.com/item?id=48348578).

[^10]: CoSAI. *MCP Runtime Isolation — Practical Guide*, 2026. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/practical-guides/mcp-runtime-isolation.md

[^11]: CoSAI. *Agentic Identity and Access Management*, approved March 20, 2026. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/agentic-identity-and-access-control.md

[^12]: NVIDIA. *OpenShell: Safe Runtime for AI Agents*, 2026. https://github.com/NVIDIA/OpenShell

[^13]: Anthropic. *Frontier Safety Roadmap*, July 10, 2026 (updated July 29, 2026). https://www.anthropic.com/responsible-scaling-policy/roadmap

[^14]: Linux kernel documentation. *Seccomp BPF (SECure COMPuting with filters)* — "Caveats". https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html

[^15]: OCSF. *`attestation` object and `record_integrity` profile*, shipped in OCSF 1.9.0, August 3, 2026 (ocsf-schema#1661). https://github.com/ocsf/ocsf-schema/releases/tag/1.9.0 — the `digital_signature` gap is tracked in ocsf-schema#1698, with a fix open as #1709.
