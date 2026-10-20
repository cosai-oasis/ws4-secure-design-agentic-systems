# WS4 Writing and Style Guide

This guide covers the three kinds of documents this workstream publishes: RFCs, white papers, and practical guides. Meeting agendas, blog posts, and SIG charters are out of scope, although blog posts should follow the white paper rules on prose and citations.

Each rule is marked as **Required** (a reviewer blocks the change) or **Recommended** (a reviewer may suggest the change but does not block on it).

---

## Part 1. Rules for every document

### 1.1 Language and spelling

- **Required.** Use US English spelling throughout: *defense*, *modeling*, *organization*, *behavior*. Code identifiers and proper names keep their own spelling.
- **Required.** Spell out each acronym the first time it appears in a document, for example "Model Context Protocol (MCP)". Do this again in every document, because readers will not have read the others.
- **Required.** Use the BCP 14 keywords (MUST, SHOULD, MAY and their negatives, per RFC 2119 and RFC 8174) only for normative requirements, and always in capitals. Write "must" in lowercase when you mean it in the ordinary sense.
- **Recommended.** Use terms from the shared glossary. If you need a term the glossary lacks, define it in your document and propose adding it to the glossary.

### 1.2 Structure and formatting

- **Required.** Each document starts with front matter that gives the title, status, version, date, and authors or editors.
- **Required.** Headings use sentence case and go no deeper than four levels.
- **Required.** Every image has alt text that says what the image shows. Commit the editable source for each diagram (SVG, Mermaid, or draw.io) next to any rendered PNG.
- **Recommended.** Use prose to make an argument and lists for items that really are parallel and separate. A section made only of bullet points usually means the reasoning has been left out.

### 1.3 Links

- **Required.** Every link resolves. CI checks this on each pull request and on a weekly schedule.
- **Required.** When you move or rename a file, update every link that points to it in the same pull request. Search the repository for the old path before you merge.
- **Required.** Describe the target in the link text. "See the [MCP Security white paper](...)" is acceptable; "see [here](...)" is not.
- **Recommended.** For sources that are likely to change or disappear, such as vendor blogs, news articles, and draft specifications, also record an archived copy (for example, a Wayback Machine snapshot) in the reference entry.

### 1.4 Use of AI tools

- **Required.** Follow the CoSAI guidelines on AI use that appear in the white paper template. A person is responsible for every sentence that is merged, and any substantial use of AI must be disclosed in the pull request.

---

## Part 2. RFCs

An RFC proposes a piece of work for the workstream. It is not the work. The RFC asks for agreement that a topic is worth doing, defines how big it is, and says what will be delivered. The deliverable itself (a white paper, a practical guide, or a specification) is written after the RFC is accepted.

### 2.1 Scope

- **Required.** One RFC proposes one deliverable. If a proposal leads to two outputs, such as a white paper and a reference implementation, submit two RFCs or explain why the outputs cannot be separated.
- **Required.** State what is out of scope as clearly as what is in scope.
- **Recommended.** Keep the body under about 1,500 words. If the proposal needs more, the extra material is probably the deliverable and should be written after the RFC is accepted. A sketch of the design belongs in the RFC; a full design does not.

### 2.2 Self-contained

A reader who has never attended a meeting and has never read the issue thread should be able to understand the RFC and decide whether to support it.

- **Required.** Do not rely on context outside the document. Avoid phrases such as "as discussed in the TSC", "per last week's call", or "Omar's thoughts". State the point and credit people in the Authors list.
- **Required.** Delete the template's prompt text ("Are there any reasons why we should not do this?") and replace it with your answers. Write "None identified" if that is the answer.
- **Allowed.** Because an RFC is a process document, it may link to the issue it came from and to related RFCs.

### 2.3 Required sections

1. **Summary.** Two or three sentences that state the gap and the proposed deliverable.
2. **Problem.** Explain what is missing from current guidance, with citations.
3. **Proposed deliverable.** State the type (white paper, practical guide, specification, or addendum), the intended audience, and an outline.
4. **Scope and non-scope.**
5. **Relationship to existing work.** Cover CoSAI documents, including those from other workstreams, as well as external standards. Explain why this work does not duplicate them.
6. **Exit criteria.** Define what "done" means, for example "a reviewed practical guide with runnable examples for X and Y".
7. **Leads, priority, and effort.**
8. **Alternatives and drawbacks.**
9. **Open questions.**
10. **References.**

### 2.4 Status

- **Required.** The front matter gives one status: `Proposed`, `Accepted`, `In progress`, `Completed`, or `Withdrawn`. When the status is `Completed`, the RFC links to the published deliverable.

---

## Part 3. White papers

White papers are the workstream's published voice. They are often read as PDFs, forwarded by email, or quoted in other organizations' documents, and their readers may never visit GitHub. They are written for a mixed audience: security architects and engineers, as well as risk, compliance, and executive readers.

### 3.1 Standalone

- **Required.** The published text contains no references to workstream process. That means no issue or pull request numbers, branches, meetings, Slack threads, mailing list posts, "drafting notes", "settled on (date)" annotations, or GitHub handles.
- **Required.** Credit contributors by name and affiliation in the Acknowledgements section, not by GitHub handle in the body.
- **Required.** Links to other CoSAI documents use absolute URLs so that they still work in the PDF. A paper that cites a CoSAI work as a reference cites a released, versioned copy (a tagged release or published PDF), not the `main` branch.
- **Recommended.** Keep drafting notes and open questions in the tracking issue, not in the paper. If they must live in the file during drafting, put them in HTML comments (`<!-- -->`) and remove them before the paper is submitted for approval.

### 3.2 Audience and structure

- **Required.** The paper opens with an abstract and an executive summary that a non-technical reader can follow without reading anything else. The executive summary states the problem, why it matters, and what the reader should do.
- **Required.** Include a Scope, Out-of-scope, and Target audience section.
- **Required.** Explain each technical concept in plain terms the first time it appears, then go into detail. Put reference material, schemas, and long control tables in appendices.
- **Recommended.** Each major section should end with a concrete takeaway, a recommendation the reader can act on, rather than a summary that repeats the section.
- **Recommended.** Use at least one worked example, a realistic scenario followed from start to finish, to make the abstract material concrete.

### 3.3 Prose that reads as written by people

Readers spot machine-generated text quickly, and once they do they stop trusting the content. Reviewers should flag the following patterns. None of them is wrong every time, but text full of them reads as unedited output.

**Patterns to avoid**

- **Vague intensifiers and filler words.** These include *robust*, *seamless*, *crucial*, *critical* (when not about severity), *leverage*, *landscape*, *holistic*, *ever-evolving*, *cutting-edge*, *paradigm*, *delve*, *navigate the complexities of*, *in today's world*, *it is important to note that*, *load-bearing*, and *game-changer*. Replace each with the specific claim it stands in for, or delete it.
- **Habitual contrasts.** Avoid repeated "not X, but Y" or "this isn't just X, it's Y". One in a paper can work; one per section cannot.
- **Reflexive triplets.** These are lists of three adjectives or three clauses added for rhythm rather than meaning.
- **Long chains of em dashes.** Use at most one pair in a paragraph. A comma, parentheses, or a new sentence is usually clearer. (As a rough benchmark, the more human-sounding papers in this repository use fewer than 3 per 1,000 words.)
- **A bolded lead-in on every bullet** ("**Scalability:** ...") throughout a section.
- **Symmetrical scaffolding.** These are sections that all begin with the same framing sentence and end with "In summary" or "In conclusion".
- **Stacked hedges** ("may potentially help to somewhat reduce").
- **Claims that could appear in any paper on any topic.** "Security is a critical concern for organizations adopting AI" tells the reader nothing.

**What to do instead**

- Make specific claims. Name the system, the version, the number, the attack, the standard.
- Vary sentence length. Keep sentences short when making a point and use longer ones when explaining how parts connect.
- Give each paragraph one claim and the evidence for it.
- Write as the workstream: "we recommend" is fine. Take positions and say how confident you are.
- Read the paper aloud. Rewrite any sentence a colleague would not say in a design review.

### 3.4 Citations

- **Required.** Cite every factual claim that does not come from the workstream's own analysis. That includes statistics, incidents, quotations, descriptions of a specification's behavior, regulatory requirements, and dates.
- **Required.** Use numbered inline citations ([1], [2]) that resolve to a References section at the end. Each entry gives the author or organization, title, publisher, publication date, URL, and the date you accessed it.
- **Required.** Prefer primary sources: specifications, standards, peer-reviewed papers, vendor security advisories, and official incident reports. Use news coverage and blogs only when no primary source exists, and say that you are doing so.
- **Required.** Cite a specific version of any specification that changes over time, for example "MCP specification, revision 2025-06-18". Undated claims about moving targets go stale without anyone noticing.
- **Required.** Identify work in progress as such. A draft standard, an open proposal, or an unmerged pull request in another project is cited as "proposed" or "draft" and is never described as shipped.
- **Recommended.** Before submitting, check that each reference supports the sentence that cites it, not just the general topic.

### 3.5 Versions, releases, and PDF parity

- **Required.** The Markdown file is the source. The PDF is generated from it, and both are updated in the same pull request.
- **Required.** Each published version has a version number and date in the front matter, plus a short changelog section or errata list.
- **Required.** When one paper names another (for example, a companion addendum), use that document's actual title and describe what it actually contains.

---

## Part 4. Practical guides

A practical guide is a tutorial. It explains a problem and a defense in plain English, then shows the defense working in code that a reader can run, check, and adapt. If a reader cannot reproduce the result, the guide has not done its job.

### 4.1 Structure

Each guide, or each major section of a long guide, follows this order:

1. **Problem.** State the threat in plain English, linked to the white paper section or CoSAI Risk Map entry that describes it.
2. **Approach.** Explain the defense and why it works, including its limits.
3. **Prerequisites.** List exact versions of languages, libraries, models, and container runtimes. Give hardware needs (GPU and RAM), any accounts or API keys, and the expected cost if the guide uses paid services.
4. **Steps.** Give numbered, copy-pasteable commands and code.
5. **Validate.** Show how the reader can confirm the defense works. At minimum, show one legitimate request that succeeds and one attack that is blocked, with the expected output.
6. **Clean up.** Explain how to tear down anything that was deployed.
7. **Limitations and next steps.**
8. **References.**

### 4.2 Runnable code

- **Required.** Every code block is either complete and runnable, or labeled as an excerpt with a link to the full file under `examples/`. Placeholder lines such as `# ...` are allowed only inside labeled excerpts.
- **Required.** Each example directory contains a dependency file with pinned versions (`requirements.txt` or `pyproject.toml`) and a short README that explains how to run it.
- **Required.** Secrets are read from environment variables and are never committed, not even as dummy values that look real.
- **Recommended.** Where the example needs a GPU, a hosted model, or cloud resources, provide an offline or mocked mode so that CI and readers without those resources can still run the logic.
- **Recommended.** Provide a container or devcontainer definition for anything with more than a few dependencies.

### 4.3 Tests

- **Required.** Each example ships with an automated test that asserts the security property, not just that the code runs. The test checks the positive case (allowed behavior works) and the negative case (the attack is blocked or detected).
- **Required.** Notebooks run cleanly from top to bottom on a fresh kernel ("Restart and Run All"). CI runs them with `nbmake` or an equivalent tool, using the mocked mode where needed.
- **Recommended.** Mark tests that need a GPU, network access, or paid APIs so that CI can skip them and readers can run them on purpose.
- **Recommended.** Set random seeds and report expected variance for stochastic results, such as adversarial suffix search.

### 4.4 Responsible content

- **Required.** Attack demonstrations target local, self-hosted components or purpose-built test fixtures, never third-party production services.
- **Required.** Do not publish a working exploit for an unpatched vulnerability in a named product.
- **Recommended.** Where a guide depends on one vendor's product, say so, explain why that product was chosen, and name alternatives where they exist. CoSAI is a cross-vendor coalition.

---

## Part 5. Reviewer checklist (summary)

| Check | RFC | White paper | Practical guide |
|---|:-:|:-:|:-:|
| Front matter (status, version, date, authors) | ✔ | ✔ | ✔ |
| Acronyms expanded on first use | ✔ | ✔ | ✔ |
| All links resolve; no links to moved paths | ✔ | ✔ | ✔ |
| Self-contained (no reliance on meeting or issue context) | ✔ | ✔ | ✔ |
| No issue/PR/branch/meeting/handle references | n/a | ✔ | ✔ (body) |
| One deliverable, scope and non-scope stated | ✔ | | |
| Template prompt text removed | ✔ | ✔ | ✔ |
| Executive summary readable by non-specialists | | ✔ | |
| Every factual claim cited; primary sources preferred | ✔ | ✔ | ✔ |
| Versioned specs cited by version | ✔ | ✔ | ✔ |
| No machine-sounding prose patterns (3.3) | ✔ | ✔ | ✔ |
| Markdown and PDF in sync | | ✔ | |
| Pinned dependencies and runnable code | | | ✔ |
| Positive and negative test per example | | | ✔ |
| Notebooks pass Restart and Run All | | | ✔ |
