# Enforced Stateful Knowledge Base for Agents

**Practical Guide (draft)** · ADLC SIG

> **Status:** Placeholder. Scope, outline and examples are still to be agreed. Proposed at the ADLC SIG meeting on 2026-11-11.

Contributors: David Pierce (@rabbidave)

---

## Goal

Agents keep more and more state between runs: memory, knowledge graphs, shared context. This guide will show how to build a portable, stateful knowledge base for agents where access is enforced, not assumed.

## Questions this guide should answer

- Who, or which agent, is allowed to read and write the knowledge base?
- How are permissions granted and checked at the time of each access (just-in-time)?
- How does the knowledge base move with the agent, and what has to be re-validated when it does?
- What happens to the stored state when the agent is updated or decommissioned?

## Related work

- The ADLC definitional paper, in particular the runtime, maintenance and decommissioning phases
- Identity and authorization work in other groups (for example ODIS)

## Outline

*TBD*

## Contributing

Comment on the PR that added this file or open an issue to join. See the [CoSAI Contributing policy](../../CONTRIBUTING.md).
