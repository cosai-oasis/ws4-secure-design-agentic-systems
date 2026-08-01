# Contributor Reputation Check

A GitHub Action that reports factual, publicly-observable signals about the
author of a new pull request or a new issue, so a maintainer can decide how
much scrutiny the contribution needs.

It is a **reporting** control, not an enforcement control. It never blocks,
closes, labels-as-spam, or auto-rejects anything. It publishes a risk level
and a label. A human makes the call.

## Why WS4 has this

Agentic-security repositories are a target for a specific abuse pattern: not
malicious code, but **social engineering of trust**. Someone opens a plausible
issue or a small PR whose real purpose is to attach their own product to the
credibility of a standards body, then cites that association elsewhere. WS4 is
exactly the kind of venue where "referenced in a CoSAI workstream" is worth
manufacturing.

Reviewing content alone does not catch this, because each individual issue
looks reasonable. The pattern is only visible in the author's cross-repository
behaviour.

## What it runs on

| Event | Runs? |
|-------|-------|
| Pull request opened | Yes |
| Issue opened | Yes |
| Comment on an issue or PR | **No.** See [Limits](#limits) |
| PR review or review comment | No |
| Discussion or discussion comment | No |
| Author has Maintain or Admin on this repo | Skipped |
| `dependabot[bot]`, `github-actions[bot]`, `copilot-swe-agent[bot]` | Skipped |

It also runs on demand via **Actions > Contributor Reputation Check > Run
workflow**, against any username, which is how you investigate an account
without waiting for them to open something.

## What it checks

Twelve signals over four groups, all computed from the public GitHub API. No
private data, no third-party data broker, no model inference about the person.

**Account shape.** Repository creation velocity, account age against
repository count, following:follower ratio, followers against public
repository count.

**Repository patterns.** Concentration of governance/security-themed repos,
bursts of repositories created in the last 90 days, bursts of "awesome"-list
forks inside 72 hours, batches of same-suffix repositories created inside 48
hours, and overlap with a defined feature-bucket set.

**Issue spray.** Issues filed across many distinct repositories inside a
7-day window, and whether those issues reference the author's own
repositories.

**Credibility.** Whether young, low-star repositories owned by the author are
being promoted into other organisations, and whether the same thin
repositories are promoted to overlapping sets of organisations.

Each signal is LOW, MEDIUM, or HIGH. Two or more HIGH aggregates to HIGH risk;
one HIGH, or three or more MEDIUM, aggregates to MEDIUM. A check that could
not complete, for example because of API rate limiting, returns UNKNOWN, which
is deliberately ranked above both LOW and MEDIUM so a failed probe cannot be
read as a clean result.

## What it publishes, and to whom

This is the part worth being precise about.

**Posted publicly on the issue or PR**, when risk is MEDIUM or above: a single
comment with the risk level per check group and an overall level, plus a
`needs-review:MEDIUM` / `needs-review:HIGH` / `needs-review:UNKNOWN` label. The
comment is idempotent, so a re-run edits it rather than stacking duplicates.

**Not published anywhere**: the per-signal detail. The underlying report names
which signals fired and with what numbers, and that detail is deliberately
neither posted as a comment nor written to the job summary nor uploaded as an
artifact. It is discarded when the job ends.

That is a deliberate choice. Publishing a scored dossier about a named person,
under the CoSAI banner, on a repository they just opened an issue on, is a
worse outcome than the spam it defends against. False positives are real, and
a public accusation is not reversible.

**How a maintainer gets the detail**: run the same tool locally against the
same username. It is MIT-licensed and reads only public API data.

```bash
gh auth login   # or export GITHUB_TOKEN
git clone https://github.com/microsoft/agent-governance-toolkit
python agent-governance-toolkit/scripts/contributor_check.py \
  --username <handle> \
  --repo cosai-oasis/ws4-secure-design-agentic-systems
```

Note that on a **public** repository, Actions run logs, job summaries, and
artifacts are readable by anyone, not only by maintainers. There is no
maintainer-only channel inside Actions on a public repo. That constraint is
why the detail is dropped rather than written somewhere "internal".

## What it deliberately does not do

- It does not decide anything. No auto-close, no auto-block, no spam label.
- It does not judge the contribution. A HIGH-risk author can be right, and a
  LOW-risk author can be wrong. Risk level says nothing about whether the
  issue or PR is any good.
- It does not use a model to form an opinion about a person. Every signal is a
  count or a ratio over public activity, with a published threshold.
- It does not bypass review. There is a maintainer allowlist upstream, and by
  design it can only soften a HIGH auto-flag to MEDIUM. It cannot mark anyone
  LOW, and it does not apply at all when a deliberate-abuse signal is present.

## Limits

**Comments are not covered.** Today the check fires on PR-open and issue-open
only. Someone who opens nothing but comments repeatedly is not screened. This
is technically addressable: `issue_comment` fires for comments on both issues
and PRs, from the default branch, in the base repository. Three things need
resolving before it ships, and none of them are solved here:

1. **Token scope.** Write access to the token on comments made against
   pull requests from forks needs confirming empirically before relying on it
   to post or label.
2. **Rate limit.** One profile check costs tens of GitHub API calls, some
   against the Search API, which is limited to 30 requests per minute. The
   `GITHUB_TOKEN` budget is 1,000 requests per hour per repository. Checking
   every comment would exhaust that on a normally busy thread.
3. **Noise.** Posting a risk comment in reply to every comment is unusable.

The plausible shape is first-time-commenter-only, with a per-account result
cached for some window, writing to a label rather than a new comment. That is
a separate change and a separate review.

**False positives have a known shape.** Protocol and specification
contributors legitimately file issues across many repositories, which triggers
cross-repo spread. The self-promotion signal is what separates them, and the
upstream check dampens volume signals for accounts with established organic
credibility. It still gets people wrong. Treat MEDIUM as "read it with
attention", not as an accusation.

**It is a point-in-time check.** It runs once, when the item is opened. It
does not re-evaluate later.

## Provenance

The detection scripts and the composite action are from
[microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit),
MIT licensed. This workflow pins them to an explicit commit SHA, because it
runs on `pull_request_target` with a write-capable token and must not track a
mutable ref. Bump the pin deliberately, after reviewing the diff.

Background reading: [Tutorial 53: Contributor Governance](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/tutorials/53-contributor-governance.md).
