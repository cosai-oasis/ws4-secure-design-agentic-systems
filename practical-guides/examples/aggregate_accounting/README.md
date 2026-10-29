# Aggregate accounting: the cases for section 4

This example runs the nineteen cases of the `aggregate-accounting/v1` corpus against the accounting rules in [section 4 of the containment paper](../../../whitepapers/agent-containment.md). It answers the review request on [PR 262](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/262#issuecomment-6432678801), where [aeoess](https://github.com/aeoess) noted that section 8.2 does not test the accounting rules and proposed four deterministic cases, with all other authorization conditions satisfied. Those four are named under the table below. The remaining cases cover the neighbouring rules in sections 4.3 and 7.1: the contract identifier, the identity of each decision, the retained effect counts and the boundary at the latency bound.

The shape under test is a limit that holds for each agent while the budget the agents share does not. Each request can be inside its own limit and the set of them outside the budget, which a check on one agent cannot see.

## Run it

```sh
pip install --require-hashes -r requirements.txt
agent-evidence-vectors --corpus vectors-aggregate-accounting --report report.json
```

The command prints `aggregate-accounting/v1: reference reader answered 19 of 19 cases, 0 disagreements` and writes `report.json`, whose `totals` read `conform: 19`, `fail: 0` and `vectors: 19`. Pass `--verifier` with the command line of your own accounting authority to run its answers against the same cases instead of the reference reader.

## The cases

Each denied case is built so the check it names is the first to fail and every earlier check passes. The allowed cases are controls: a verifier that refuses everything fails them, and so does one that refuses a request that fits.

| Case | What it tests |
| --- | --- |
| `allow-concurrent-both-fit` | two concurrent requests for 4 units each against 10 left; both are admitted |
| `allow-race-one-admitted` | two racing requests for 6 units each against 10 left; one is admitted and one refused |
| `allow-exact-fit-both-admitted` | two requests that together use the budget exactly; both are admitted |
| `allow-unknown-outcome-stays-charged` | a reservation with an unknown outcome stays charged past its expiry |
| `allow-released-reservation-returns-units` | a released reservation returns its units |
| `allow-past-latency-bound-refused` | a request past the latency bound is refused |
| `allow-past-latency-bound-held` | a request past the latency bound is held for confirmation |
| `allow-latency-at-bound-admitted` | a request answered exactly at the bound is admitted |
| `allow-two-subtrees-one-principal` | two subtrees under one principal draw on one budget |
| `contract-id-missing` | a record that carries no contract identifier |
| `contract-id-unknown` | a record that carries an unknown contract identifier |
| `identity-missing-subtree` | a decision that names no subtree |
| `identity-missing-action` | a decision that names no action |
| `latency-bound-admitted` | a request admitted after an answer slower than the bound |
| `unknown-outcome-released-after-expiry` | an unknown-outcome reservation released at expiry |
| `race-both-admitted` | two racing requests for 6 units each, both admitted against 10 left |
| `per-agent-limits-hold-aggregate-fails` | every agent inside its own limit while the shared budget is exceeded |
| `fitting-request-refused` | a request that fits the remaining budget is refused |
| `effect-counts-disagree` | the retained effect counts disagree with the decisions |

The four cases from the review are `allow-concurrent-both-fit`, `allow-race-one-admitted`, `allow-unknown-outcome-stays-charged` and `allow-past-latency-bound-refused` (with `allow-past-latency-bound-held` for the hold). The faults that each of them guards against are `fitting-request-refused`, `race-both-admitted`, `unknown-outcome-released-after-expiry` and `latency-bound-admitted`.

Every result names the principal, subtree, budget and action in the decision it records, and the corpus retains the effect counts, so a reader can recompute them. The corpus, its checks in order and the record layout are documented in the [corpus README](https://github.com/probityai/agent-evidence-vectors/tree/v0.29.0/vectors-aggregate-accounting).

## Keeping it current

`requirements.txt` pins `agent-evidence-vectors` to one release with its file hashes, and Dependabot opens a pull request for each new release. The workflow in `.github/workflows/aggregate-accounting-example.yml` runs every case and checks that this table names exactly the cases the corpus ran, so the table cannot drift from the data.
