#!/usr/bin/env python3
"""
Mechanical checks for WS4 white papers and RFCs, following STYLE_GUIDE.md.

This is the first pass of the cosai-ws4-doc-review skill. It finds what a
regular expression can find (process references, template text, broken links,
missing sections, filler vocabulary, uncited statistics) so the reviewer can
spend their attention on what it cannot: whether the argument holds, whether a
source supports its sentence, whether the executive summary works for a
non-specialist.

Every finding carries the STYLE_GUIDE.md section it comes from and a severity:

    blocking      breaks a Required rule
    pre-approval  breaks a Required rule for published text, in a draft that
                  is not yet published (white papers only)
    should-fix    breaks a Recommended rule, or a §3.3 prose pattern
    nit           style and consistency

Findings marked "heuristic" (shown as "?" in text output) are pattern matches
that a person or agent must confirm before reporting them.

Usage:
    # Type (whitepaper or rfc) is inferred from the path
    python3 lint_docs.py whitepapers/agent-containment.md RFCs/RFC-50.md

    # An RFC issue body saved to a file, or piped on stdin
    gh issue view 50 --json body -q .body | python3 lint_docs.py --type rfc -

    # Also fetch every external URL (slow; needs network)
    python3 lint_docs.py --check-urls whitepapers/model-context-protocol-security.md

    # Machine-readable output for the skill
    python3 lint_docs.py --format json whitepapers/*.md

Exit status is 1 if any non-heuristic blocking finding is reported, else 0.
Standard library only; Python 3.10+.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

SEVERITIES = ["blocking", "pre-approval", "should-fix", "nit"]

# Findings per rule per file before the rest are folded into one summary line.
DEFAULT_CAP = 6

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

# §3.3, the words the guide names.
FILLER_GUIDE = (
    r"robust(?:ly|ness)?|seamless(?:ly)?|crucial(?:ly)?|leverag(?:e|es|ed|ing)|"
    r"landscapes?|holistic(?:ally)?|ever-evolving|cutting-edge|paradigms?|"
    r"delv(?:e|es|ed|ing)|load-bearing|game-changers?|game-changing|"
    r"navigat(?:e|ing) the complexities|in today's (?:world|landscape|environment)|"
    r"it is important to note(?: that)?"
)
# Same family, not named in the guide. Reported as nits.
FILLER_EXTRA = (
    r"pivotal|tapestry|realm|empower(?:s|ed|ing)?|unlock(?:s|ed|ing)? the|"
    r"it is worth noting(?: that)?|it's worth noting(?: that)?|plays? a (?:key|vital|pivotal) role|"
    r"in the ever-changing|state-of-the-art|best-in-class|world-class|"
    r"a testament to|first and foremost|at the end of the day|moving forward"
)
FILLER_GUIDE_RE = re.compile(rf"\b(?:{FILLER_GUIDE})\b", re.I)
FILLER_EXTRA_RE = re.compile(rf"\b(?:{FILLER_EXTRA})\b", re.I)

CONTRAST_RE = re.compile(
    r"\b(?:is|are|was|were)n['’]t (?:just|only|merely|simply)\b|"
    r"\b(?:is|are) not (?:just|only|merely|simply)\b|"
    r"\bnot (?:just|merely|simply) (?:a|an|the|about)\b|"
    r"\bit['’]s not about\b|"
    r"\bnot (?:a|an) \w+(?: \w+)?, but (?:a|an)\b",
    re.I,
)
SCAFFOLD_RE = re.compile(r"^(?:in summary|in conclusion|to summarize|to sum up|overall,|ultimately,)", re.I)
HEDGES = {"may", "might", "could", "potentially", "possibly", "perhaps", "somewhat",
          "arguably", "conceivably", "presumably", "seemingly", "relatively", "fairly"}

UK_SPELLING_RE = re.compile(
    r"\b(?:"
    r"(?:author|organ|recogn|real|util|optim|minim|maxim|priorit|standard|character|summar|"
    r"emphas|categor|normal|serial|initial|central|special|visual|final|sanit|custom|"
    r"operational|harmon|synchron|monet|weapon|capital|apolog|critic|memor|modern|neutral|"
    r"tokenis|virtual|contextual|formal|personal|industrial|regular|vectoris)is"
    r"(?:e|es|ed|ing|ation|ations|er|ers)"
    r"|anal[yi]s(?:e|es|ed|ing)|paralys(?:e|ed|ing)|catalys(?:e|ed|ing)"
    r"|behaviour(?:s|al)?|colour(?:s|ed)?|favour(?:s|ed|ite|able)?|honour(?:s|ed)?|labour|neighbour(?:s|ing)?|endeavour(?:s)?|rumour(?:s)?"
    r"|centre(?:s|d)?|fibre(?:s)?|theatre(?:s)?"
    r"|defence(?:s)?|offence(?:s)?|pretence|licence(?:s|d)?"
    r"|catalogue(?:s|d)?|analogue"
    r"|modell(?:ing|ed|er|ers)|labell(?:ing|ed)|travell(?:ing|ed|er)|signall(?:ing|ed)|fuell(?:ing|ed)|channell(?:ing|ed)"
    r"|programme(?:s)?|artefact(?:s)?|judgement(?:s)?|whilst|amongst|enrol(?:s|ment)?|fulfil(?:s|ment)?"
    r")\b",
    re.I,
)

BCP14_RE = re.compile(r"\b(?:MUST(?: NOT)?|SHALL(?: NOT)?|SHOULD(?: NOT)?|REQUIRED|RECOMMENDED|OPTIONAL|NOT RECOMMENDED)\b|\bMAY\b")
BCP14_BOILERPLATE_RE = re.compile(r"RFC\s?2119|RFC\s?8174|BCP\s?14", re.I)

ACRONYM_RE = re.compile(r"(?<![\w/.-])([A-Z][A-Z0-9]{1,7})(s?)(?![\w/-])")
ACRONYM_SKIP = {
    # BCP 14 and other all-caps words that are not acronyms
    "MUST", "SHALL", "SHOULD", "MAY", "NOT", "REQUIRED", "RECOMMENDED", "OPTIONAL",
    "AND", "OR", "TODO", "TBD", "FIXME", "XXX", "NOTE", "WARNING", "TIP", "IMPORTANT",
    # Roman numerals
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
    # Terms readers of these papers will not need expanded
    "US", "UK", "EU", "OK", "ID", "PDF", "URL", "URI", "HTTP", "HTTPS", "JSON", "YAML",
    "XML", "HTML", "CSS", "API", "CPU", "GPU", "RAM", "SQL", "CLI", "SDK", "FAQ", "UTC",
    "AM", "PM", "ET", "PT", "PST", "EST", "DNS", "IP", "TCP", "UDP", "SSH",
    "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "EDIT",
}
# Acronyms used as a document identifier ("RFC 8693", "FIPS 203", "CVE-2025-1234") need no expansion there.
ACRONYM_AS_ID_RE = re.compile(r"\s?[- ]?\d")

# §3.1 process references in white papers: (rule id, pattern, description).
PROCESS_PATTERNS = [
    ("issue-number", re.compile(r"(?<![\w&/\\(\[#])#\d{2,5}\b"), "issue or PR number"),
    ("issue-number", re.compile(r"\b(?:issue|PR|pull request|discussion)s?\s+#?\d+\b", re.I), "issue or PR number"),
    ("github-url", re.compile(r"/(?:issues|pull|discussions)/\d+|/commit/[0-9a-f]{7,}"), "link to an issue, PR, discussion, or commit"),
    ("github-handle", re.compile(r"(?<![\w.@/`])@[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})\b(?![.\w-]*\.[a-z]{2,})"), "GitHub handle"),
    ("branch", re.compile(r"\b(?:main|master|develop|v\d[\w.]*|feat/[\w-]+|feature/[\w-]+)\s+branch\b|\bbranch(?:es)?\s+[`'\"]?(?:main|master|v\d|feat/|feature/)", re.I), "branch name"),
    ("meeting", re.compile(
        r"\b(?:slack|mailing list|(?:this|the|in the|per the) thread|on the call|(?:last|weekly|our|the tsc) call|"
        r"(?:last|this|next) (?:week's )?meeting|meeting (?:notes|minutes)|as (?:we )?discussed|we discussed|"
        r"agreed (?:on|in) the (?:call|meeting))\b", re.I), "reference to a meeting, call, Slack, or mailing list"),
    ("drafting-note", re.compile(r"\b(?:drafting note|editor['’]?s note|note to (?:self|editors|reviewers)|settled (?:\(|on \d|with the))", re.I), "drafting note"),
    ("repo-reference", re.compile(r"\bthis (?:repo|repository)\b|\b(?:open|file|raise) an issue\b|\bsubmit a (?:PR|pull request)\b", re.I), "reference to the repository or its workflow"),
]
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|XXX)\b|\[citation needed\]|lorem ipsum", re.I)

# Prompt text from whitepaper-template.md and rfc-template.md.
TEMPLATE_PROMPTS = [
    "Example Corp", "Chair.Name@example.com", "Editor.Name@example.com", "WS Lead Chair Name",
    "Editor Name (", "Level 2 Section Title", "Level 3 Section Title", "[Workstream name]",
    "\\[Workstream name\\]", 'remove "s" from', "hyperlink to remember",
    "list file names or directory name", "Summary of the technical purpose of the document",
    "This document is one component of a Work Product",
    "How to use this template", "[RFC Title]", "* @handle", "Short, sweet, and to the point",
    "Are there any reasons why we should not do this?", "is it too opinionated?",
    "is it too complex to implement?", "does the ecosystem exist to support this yet?",
    "What other designs have been considered?", "What is the impact of not doing this?",
    "Is there an existing framework or paper that discusses this?",
    "Was this discussed in a talk that was recorded?",
    "What help from the group do you need to make this successful?",
]
TEMPLATE_OPTION_SETS = [
    ("Priority", ["P0: This is critical", "P1: This is important", "P2: This is nice to have"]),
    ("Level of Effort", ["Small: This will take", "Medium: This will take", "Large: This will take"]),
]

VAGUE_LINK_TEXT = {"here", "click here", "this link", "link", "this", "this page", "read more", "more", "page", "website"}

MOVING_SPECS_RE = re.compile(r"\b(?:MCP|Model Context Protocol|A2A|Agent2Agent|OAuth 2\.1|AGNTCY|ACP)\b")
SPEC_WORD_RE = re.compile(r"\b(?:specification|spec)\b", re.I)
VERSION_HINT_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b(?:revision|version|release|draft)\b|\bv\d", re.I)

STAT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)? percent\b|\b\d{1,3}(?:,\d{3})+\b|\$\s?\d|"
    r"\b\d+(?:\.\d+)?\s?(?:million|billion|trillion)\b|"
    r"\baccording to (?:a|an|the|recent)? ?(?:\w+ )?(?:study|survey|report|research|analysis|data|researchers)\b|"
    r"\b(?:a|one) (?:recent )?(?:study|survey|report) (?:found|shows|showed)\b|\b(?:reported|disclosed) (?:that|in)\b",
    re.I,
)
CITATION_MARK_RE = re.compile(r"\[\d{1,3}(?:\s*[-–,]\s*\d{1,3})*\]|\[\^[\w-]+\]|\]\(https?://")

RFC_STATUSES = ["proposed", "in review", "accepted", "approved", "in progress", "completed", "withdrawn"]

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    section: str
    severity: str
    message: str
    excerpt: str = ""
    heuristic: bool = False


@dataclass
class Line:
    no: int
    raw: str
    clean: str = ""   # raw minus HTML comments and inline code
    prose: str = ""   # clean minus link targets, URLs, and markup
    code: bool = False
    fm: bool = False
    comment: bool = False  # line lies wholly inside an HTML comment
    heading: int = 0
    table: bool = False
    toc: bool = False
    refs: bool = False
    list_item: bool = False


@dataclass
class Doc:
    label: str
    path: Path | None
    kind: str
    text: str
    lines: list[Line] = field(default_factory=list)
    fm: dict[str, str] = field(default_factory=dict)
    headings: list[tuple[int, int, str]] = field(default_factory=list)  # (line, level, clean text)
    anchors: set[str] = field(default_factory=set)
    comment_lines: list[int] = field(default_factory=list)
    stage: str = "draft"
    findings: list[Finding] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def add(self, line, rule, section, severity, message, excerpt="", heuristic=False):
        excerpt = excerpt.strip()
        if len(excerpt) > 160:
            excerpt = excerpt[:157] + "..."
        self.findings.append(Finding(self.label, line, rule, section, severity, message, excerpt, heuristic))

    def body(self):
        """Lines that carry readable text."""
        return [ln for ln in self.lines if not (ln.code or ln.fm or ln.comment)]

    def prose_lines(self):
        """Body text a reader reads as prose: no headings, tables, TOC, or references."""
        return [ln for ln in self.body() if not (ln.heading or ln.table or ln.toc or ln.refs) and ln.prose.strip()]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

LINK_RE = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\[\]]*\])*)\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]^][^\]]*)\]:\s*(\S+)")
BARE_URL_RE = re.compile(r"(?<![(<\[])https?://[^\s<>)\]\"'`|]+")
REFS_HEADING_RE = re.compile(r"^(?:references|bibliography|works cited|sources|reference material)\b", re.I)
TOC_HEADING_RE = re.compile(r"^(?:table of contents|contents)$", re.I)


def clean_heading(text: str) -> str:
    text = re.sub(r"\s*\{#[^}]*\}\s*$", "", text)
    text = re.sub(r"\s#+\s*$", "", text)
    text = LINK_RE.sub(lambda m: m.group(2), text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\\", "").replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?<!\w)[*_](.+?)[*_](?!\w)", r"\1", text)
    return text.strip()


def github_slug(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def strip_number(text: str) -> str:
    """'3.2 Scope' -> 'scope'; 'Appendix A. Evidence' -> 'evidence'."""
    t = text.lower().strip()
    t = re.sub(r"^appendix\s+[a-z0-9]+[.:)]?\s*", "", t)
    t = re.sub(r"^[\d.]+\s*", "", t)
    return t.strip(" .:-—")


def to_prose(s: str) -> str:
    s = LINK_RE.sub(lambda m: "" if m.group(1) else m.group(2), s)
    s = re.sub(r"<https?://[^>]+>", " ", s)
    s = BARE_URL_RE.sub(" ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\\", "")
    return s


def parse(label: str, path: Path | None, text: str, kind: str) -> Doc:
    doc = Doc(label=label, path=path, kind=kind, text=text)
    raw_lines = text.splitlines()

    fm_end = -1
    if raw_lines and raw_lines[0].strip() == "---":
        for j in range(1, min(len(raw_lines), 80)):
            if raw_lines[j].strip() in ("---", "..."):
                fm_end = j
                break
    for j in range(1, fm_end):
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw_lines[j])
        if m:
            doc.fm[m.group(1).lower()] = m.group(2).strip().strip("\"'")

    in_code = False
    fence = ""
    in_comment = False
    in_toc = False
    refs_level = 0
    slug_counts: dict[str, int] = {}

    for idx, raw in enumerate(raw_lines):
        ln = Line(no=idx + 1, raw=raw)
        doc.lines.append(ln)

        if idx <= fm_end:
            ln.fm = True
            ln.clean = raw
            continue

        fm_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw)
        if in_code:
            ln.code = True
            if fm_match and fm_match.group(1)[0] == fence[0] and len(fm_match.group(1)) >= len(fence):
                in_code = False
            continue
        if fm_match and not in_comment:
            in_code = True
            fence = fm_match.group(1)
            ln.code = True
            continue

        # Strip HTML comments, which may span lines.
        out = []
        rest = raw
        had_text = False
        while rest:
            if in_comment:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    rest = rest[end + 3:]
                    in_comment = False
            else:
                start = rest.find("<!--")
                if start < 0:
                    out.append(rest)
                    had_text = had_text or bool(rest.strip())
                    rest = ""
                else:
                    out.append(rest[:start])
                    had_text = had_text or bool(rest[:start].strip())
                    doc.comment_lines.append(ln.no)
                    rest = rest[start + 4:]
                    in_comment = True
        if not had_text and (in_comment or "<!--" in raw or "-->" in raw):
            ln.comment = True
        clean = "".join(out)
        clean = re.sub(r"`[^`]*`", " ", clean)
        ln.clean = clean
        ln.prose = to_prose(clean)

        hm = re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", clean)
        if hm:
            level = len(hm.group(1))
            htext = clean_heading(hm.group(2))
            ln.heading = level
            doc.headings.append((ln.no, level, htext))
            explicit = re.search(r"\{#([^}]+)\}\s*$", hm.group(2))
            base = explicit.group(1) if explicit else github_slug(htext)
            n = slug_counts.get(base, 0)
            doc.anchors.add(base if n == 0 else f"{base}-{n}")
            slug_counts[base] = n + 1
            in_toc = bool(TOC_HEADING_RE.match(strip_number(htext)))
            if refs_level and level <= refs_level:
                refs_level = 0
            if REFS_HEADING_RE.match(strip_number(htext)):
                refs_level = level
            continue

        for a in re.findall(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']", raw) + re.findall(r"\sid=[\"']([^\"']+)[\"']", raw):
            doc.anchors.add(a)

        stripped = clean.strip()
        ln.table = stripped.startswith("|")
        ln.list_item = bool(re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", clean))
        ln.toc = in_toc or bool(re.match(r"^\s*(?:[-*+]|\d+[.)])\s*\[[^\]]+\]\(#[^)]*\)\s*$", clean))
        ln.refs = bool(refs_level)

    # Stage: approved documents are held to the published-text rules.
    status = doc.fm.get("status", "")
    approved = bool(re.match(r"^\s*approved\b", status, re.I))
    if re.search(r"\bApproved by the CoSAI Project Governing Board\b", text):
        approved = True
    if re.search(r"\bnot (?:yet )?approved\b", status, re.I):
        approved = False
    doc.stage = "approved" if approved else "draft"
    return doc


def iter_links(doc: Doc):
    """Yield (line, is_image, text, target) for inline links, reference definitions, and bare URLs."""
    for ln in doc.body():
        for m in LINK_RE.finditer(ln.clean):
            target = m.group(3).strip("<>")
            yield ln.no, bool(m.group(1)), m.group(2), target
        m = REF_DEF_RE.match(ln.clean)
        if m:
            yield ln.no, False, m.group(1), m.group(2).strip("<>")
        no_links = LINK_RE.sub(" ", ln.clean)
        for u in BARE_URL_RE.findall(no_links):
            yield ln.no, False, "", u.rstrip(".,;:")
        for m in re.finditer(r"<img\b[^>]*>", ln.clean, re.I):
            src = re.search(r"src=[\"']([^\"']+)", m.group(0))
            alt = re.search(r"alt=[\"']([^\"']*)", m.group(0))
            yield ln.no, True, alt.group(1) if alt else "", src.group(1) if src else ""


def sentences(text: str):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])", text) if s.strip()]


def paragraphs(doc: Doc):
    """Group prose lines into paragraphs; each list item starts a new one."""
    paras: list[tuple[int, str]] = []
    cur_start, cur = 0, []
    prev_no = -1
    for ln in doc.prose_lines():
        if cur and (ln.no != prev_no + 1 or ln.list_item):
            paras.append((cur_start, " ".join(cur)))
            cur = []
        if not cur:
            cur_start = ln.no
        cur.append(ln.prose.strip())
        prev_no = ln.no
    if cur:
        paras.append((cur_start, " ".join(cur)))
    return paras


def word_count(doc: Doc) -> int:
    return sum(len(re.findall(r"\b[\w'’-]+\b", ln.prose)) for ln in doc.body() if not (ln.toc or ln.refs))


def has_heading(doc: Doc, pattern: str, max_level: int = 6) -> bool:
    rx = re.compile(pattern, re.I)
    return any(level <= max_level and rx.search(strip_number(t)) for _, level, t in doc.headings)


def has_field(doc: Doc, names: list[str]) -> bool:
    if any(n in doc.fm for n in names):
        return True
    rx = re.compile(r"^\W*(?:" + "|".join(names) + r")s?\W*\s*:", re.I)
    return any(rx.match(ln.clean.lstrip("#* ")) for ln in doc.lines[:200] if not ln.code)


def compact(nums: list[int], limit: int = 15) -> str:
    shown = ", ".join(str(n) for n in nums[:limit])
    return shown + (f", and {len(nums) - limit} more" if len(nums) > limit else "")


# ---------------------------------------------------------------------------
# Checks for every document (Part 1)
# ---------------------------------------------------------------------------


def check_common(doc: Doc, repo_root: Path | None, allow_acronyms: set[str]):
    body = doc.body()

    # §1.1 US spelling
    for ln in doc.prose_lines():
        for m in UK_SPELLING_RE.finditer(ln.prose):
            doc.add(ln.no, "us-spelling", "1.1", "blocking",
                    f"UK spelling \"{m.group(0)}\"; use US English unless this is a proper name.", ln.raw, heuristic=True)

    # §1.1 acronyms expanded on first use
    expanded: dict[str, int] = {}
    first_use: dict[str, tuple[int, str]] = {}
    for ln in body:
        if ln.toc or ln.refs:
            continue
        for m in re.finditer(r"\(([A-Z][A-Za-z0-9]{1,7}?)s?[),;]", ln.prose):
            expanded.setdefault(m.group(1), ln.no)
        for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,7})s? \((?:[A-Z][a-z]|[a-z])", ln.prose):
            expanded.setdefault(m.group(1), ln.no)
        if ln.heading or ln.table:
            continue
        for m in ACRONYM_RE.finditer(ln.prose):
            acr = m.group(1)
            if not re.search(r"[A-Z].*[A-Z]", acr) or acr in ACRONYM_SKIP or acr in allow_acronyms:
                continue
            if re.fullmatch(r"[A-Z]\d+|\d+[A-Z]+", acr) or ACRONYM_AS_ID_RE.match(ln.prose, m.end()):
                continue
            first_use.setdefault(acr, (ln.no, ln.raw))
    missing = sorted(
        ((no, acr) for acr, (no, _) in first_use.items() if acr not in expanded or expanded[acr] > no),
        key=lambda x: x[0],
    )
    if missing:
        listed = "; ".join(f"{acr} (line {no})" for no, acr in missing[:25])
        more = f"; and {len(missing) - 25} more" if len(missing) > 25 else ""
        doc.add(missing[0][0], "acronym-first-use", "1.1", "blocking",
                f"{len(missing)} acronyms appear before (or without) their expansion: {listed}{more}.",
                heuristic=True)

    # §1.1 BCP 14 keywords
    bcp_lines = [ln.no for ln in doc.prose_lines() if BCP14_RE.search(ln.prose)]
    if bcp_lines and not BCP14_BOILERPLATE_RE.search(doc.text):
        doc.add(bcp_lines[0], "bcp14-boilerplate", "1.1", "blocking",
                f"Capitalized requirement keywords (MUST, SHOULD, MAY...) on lines {compact(bcp_lines)} "
                "but no BCP 14 statement citing RFC 2119 and RFC 8174.", heuristic=True)

    # §1.2 headings: depth and sentence case
    title_case = []
    for no, level, text in doc.headings:
        if level > 4:
            doc.add(no, "heading-depth", "1.2", "blocking", f"Heading level {level}; the guide allows four.", text)
        words = [w for w in re.findall(r"[A-Za-z][\w'’-]*", strip_number(text))][1:]
        candidates = [w for w in words if len(w) > 3 and not w.isupper() and not re.search(r"[A-Z].*[A-Z]", w)]
        caps = [w for w in candidates if w[0].isupper()]
        if len(caps) >= 2 and len(caps) >= 0.6 * len(candidates):
            title_case.append(no)
    if title_case:
        doc.add(title_case[0], "heading-case", "1.2", "blocking",
                f"{len(title_case)} headings look like title case rather than sentence case (lines {compact(title_case)}). "
                "Proper nouns keep their capitals.", heuristic=True)

    # §1.2 front matter
    if doc.kind == "whitepaper":
        wanted = {"title": ["title"], "status": ["status"], "version": ["version"],
                  "date": ["date", "last_updated"], "authors or editors": ["author", "authors", "editor", "editors"]}
        missing_fm = [k for k, names in wanted.items() if not has_field(doc, names)]
        if "title" in missing_fm and doc.headings and doc.headings[0][1] == 1:
            missing_fm.remove("title")
        if missing_fm:
            doc.add(1, "front-matter", "1.2", "blocking", f"Front matter lacks: {', '.join(missing_fm)}.")

    # §1.2 images: alt text and editable diagram source
    for no, is_img, alt, target in iter_links(doc):
        if not is_img:
            continue
        if not alt.strip():
            doc.add(no, "image-alt", "1.2", "blocking", "Image has no alt text.", target)
        if doc.path and target and not re.match(r"https?:", target) and re.search(r"\.(png|jpe?g|gif|webp)$", target, re.I):
            img = (doc.path.parent / urllib.parse.unquote(target)).resolve()
            stems = [img.with_suffix(s) for s in (".svg", ".mmd", ".mermaid", ".drawio", ".excalidraw")]
            stems.append(img.parent / (img.stem + ".drawio.svg"))
            if img.exists() and not any(p.exists() for p in stems):
                doc.add(no, "diagram-source", "1.2", "blocking",
                        "Raster image with no editable source (SVG, Mermaid, draw.io) beside it. Ignore if it is a screenshot.",
                        target, heuristic=True)

    # §1.3 links: targets resolve, anchors exist, link text describes the target
    for no, is_img, text, target in iter_links(doc):
        if not is_img and text and clean_heading(text).lower().strip(" .") in VAGUE_LINK_TEXT:
            doc.add(no, "link-text", "1.3", "blocking", f"Link text \"{text}\" does not describe its target.", target)
        if not target or re.match(r"(?:https?|mailto|ftp|tel):", target, re.I):
            continue
        path_part, _, anchor = target.partition("#")
        if not path_part:
            if anchor and anchor not in doc.anchors and urllib.parse.unquote(anchor) not in doc.anchors:
                doc.add(no, "broken-anchor", "1.3", "blocking", f"No heading in this document produces the anchor #{anchor}.", target)
            continue
        if doc.path is None:
            continue
        dest = (doc.path.parent / urllib.parse.unquote(path_part)).resolve()
        if not dest.exists():
            doc.add(no, "broken-link", "1.3", "blocking", f"Relative link target does not exist: {path_part}", target)
        elif anchor and dest.suffix == ".md":
            other = parse(str(dest), dest, dest.read_text(encoding="utf-8", errors="replace"), "other")
            if anchor not in other.anchors:
                doc.add(no, "broken-anchor", "1.3", "blocking", f"{path_part} has no heading for #{anchor}.", target)

    # §1.4 / template prompt text left in (Required for all three types, Part 5 checklist)
    for ln in doc.lines:
        if ln.code:
            continue
        for p in TEMPLATE_PROMPTS:
            if p in ln.raw:
                doc.add(ln.no, "template-text", "2.2/Part 5", "blocking", "Template prompt text left in.", ln.raw)
                break
    for name, options in TEMPLATE_OPTION_SETS:
        hits = [ln.no for ln in doc.lines for o in options if o in ln.raw]
        if len(hits) == len(options):
            doc.add(hits[0], "template-text", "2.2/Part 5", "blocking",
                    f"All three template options for {name} are still listed; keep the one that applies.")


# ---------------------------------------------------------------------------
# Prose patterns (§3.3), applied to white papers and RFCs
# ---------------------------------------------------------------------------


def check_prose(doc: Doc):
    paras = paragraphs(doc)
    words = word_count(doc)
    doc.metrics["words"] = words

    for ln in doc.prose_lines():
        words_hit = [m.group(0) for m in FILLER_GUIDE_RE.finditer(ln.prose)]
        if words_hit:
            doc.add(ln.no, "filler-word", "3.3", "should-fix",
                    f"{', '.join(repr(w) for w in words_hit)}: replace with the specific claim, or delete.", ln.raw)
        extra = [m.group(0) for m in FILLER_EXTRA_RE.finditer(ln.prose)]
        if extra:
            doc.add(ln.no, "filler-word-extra", "3.3", "nit", f"{', '.join(repr(w) for w in extra)} reads as filler.", ln.raw)

    contrasts = [(no, m.group(0)) for no, p in paras for m in CONTRAST_RE.finditer(p)]
    doc.metrics["contrast_constructions"] = len(contrasts)
    sections = max(1, sum(1 for _, level, _ in doc.headings if level <= 2))
    if len(contrasts) >= 3 and len(contrasts) > sections / 3:
        doc.add(contrasts[0][0], "habitual-contrast", "3.3", "should-fix",
                f"{len(contrasts)} \"not X, but Y\" style constructions (lines {compact([c[0] for c in contrasts])}). "
                "One in a paper can work; this many reads as a habit.", contrasts[0][1])

    dash_total = 0
    for no, p in paras:
        n = p.count("—") + len(re.findall(r"\s--\s", p))
        dash_total += n
        if n > 2:
            doc.add(no, "em-dash", "3.3", "should-fix", f"{n} em dashes in one paragraph; the guide allows one pair.", p[:120])
    doc.metrics["em_dashes_per_1000_words"] = round(dash_total * 1000 / words, 1) if words else 0

    # Bold lead-in on every bullet in a run of four or more
    run: list[int] = []
    bold_runs = []
    prev = -2
    for ln in doc.body():
        if ln.list_item and not (ln.toc or ln.refs):
            bold = bool(re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]+\*\*\s*[:.—-]|^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]+[:.]\*\*", ln.clean))
            if bold and (ln.no <= prev + 2 or not run):
                run.append(ln.no)
                prev = ln.no
                continue
        elif ln.no <= prev + 1 or not ln.raw.strip():
            continue
        if len(run) >= 4:
            bold_runs.append(run)
        run, prev = [], -2
    if len(run) >= 4:
        bold_runs.append(run)
    for r in bold_runs:
        doc.add(r[0], "bold-lead-in", "3.3", "should-fix",
                f"{len(r)} consecutive bullets each open with a bold label. Consider prose or plain bullets.")

    # Symmetrical scaffolding: summary closers and identical section openers
    for no, p in paras:
        if SCAFFOLD_RE.match(p):
            doc.add(no, "scaffold-closer", "3.3", "should-fix", "Paragraph opens with a summary formula.", p[:100])
    openers: dict[str, list[int]] = {}
    heading_lines = {no for no, level, _ in doc.headings if level <= 3}
    seen_paras = set()
    for hno in sorted(heading_lines):
        for no, p in paras:
            if no > hno:
                if no not in seen_paras:
                    seen_paras.add(no)
                    key = " ".join(p.lower().split()[:3])
                    openers.setdefault(key, []).append(no)
                break
    for key, nos in openers.items():
        if len(nos) >= 3 and key:
            doc.add(nos[0], "same-opener", "3.3", "should-fix",
                    f"{len(nos)} sections open with the same words \"{key}...\" (lines {compact(nos)}).")

    # Stacked hedges
    for no, p in paras:
        for s in sentences(p):
            toks = re.findall(r"[a-z]+", s.lower())
            for i in range(len(toks)):
                window = [t for t in toks[i:i + 6] if t in HEDGES]
                if len(window) >= 2 and toks[i] in HEDGES:
                    doc.add(no, "stacked-hedge", "3.3", "should-fix", "Stacked hedges: " + " / ".join(window) + ".", s)
                    break

    # Sentence length spread, reported as a metric only
    lengths = [len(s.split()) for _, p in paras for s in sentences(p) if len(s.split()) > 2]
    if len(lengths) > 10:
        doc.metrics["sentence_words_mean"] = round(statistics.mean(lengths), 1)
        doc.metrics["sentence_words_stdev"] = round(statistics.pstdev(lengths), 1)


# ---------------------------------------------------------------------------
# Citations (§3.4)
# ---------------------------------------------------------------------------


def parse_references(doc: Doc):
    entries: list[dict] = []
    cur = None
    for ln in doc.lines:
        if ln.code or ln.comment:
            continue
        fn = re.match(r"^\s*\[\^([\w-]+)\]:\s*(.*)", ln.clean)
        if fn:
            # A footnote is a reference only if it points at a source; explanatory notes are not.
            cur = None
            if re.search(r"https?://|\bdoi\b|10\.\d{4,}/", fn.group(2), re.I):
                cur = {"line": ln.no, "key": "^" + fn.group(1), "text": fn.group(2)}
                entries.append(cur)
            continue
        if not ln.refs or ln.heading:
            if not ln.refs:
                cur = None
            continue
        m = re.match(r"^\s*(?:(\d+)[.)]\s+|\[(\d+)\]\s*|[-*+]\s+(?:\[(\d+)\]\s*)?)(.*)", ln.clean)
        if m:
            key = m.group(1) or m.group(2) or m.group(3)
            cur = {"line": ln.no, "key": key, "text": m.group(4)}
            entries.append(cur)
        elif cur and ln.clean.strip():
            cur["text"] += " " + ln.clean.strip()
        elif not ln.clean.strip():
            pass
    return entries


def expand_cites(s: str) -> list[str]:
    out = []
    for part in re.split(r"\s*,\s*", s):
        r = re.split(r"\s*[-–]\s*", part)
        if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and int(r[1]) - int(r[0]) < 50:
            out += [str(i) for i in range(int(r[0]), int(r[1]) + 1)]
        elif part.isdigit():
            out.append(part)
    return out


def check_citations(doc: Doc, numbered_required: bool):
    entries = parse_references(doc)
    has_refs = any(ln.refs for ln in doc.lines)
    doc.metrics["references"] = len(entries)

    cited: dict[str, int] = {}
    for ln in doc.body():
        if ln.refs or ln.toc:
            continue
        for m in re.finditer(r"\[(\d{1,3}(?:\s*[-–,]\s*\d{1,3})*)\](?!:)", ln.clean):
            for k in expand_cites(m.group(1)):
                cited.setdefault(k, ln.no)
        for m in re.finditer(r"\[\^([\w-]+)\](?!:)", ln.clean):
            cited.setdefault("^" + m.group(1), ln.no)
    doc.metrics["inline_citations"] = len(cited)

    # A missing References section is reported by the structure checks.
    if numbered_required and (entries or has_refs):
        if not cited:
            doc.add(entries[0]["line"] if entries else 1, "no-inline-citations", "3.4", "blocking",
                    "References are listed but nothing in the text cites them with [n] markers.")
        keyed = {e["key"] for e in entries if e["key"]}
        if entries and not keyed:
            doc.add(entries[0]["line"], "unnumbered-references", "3.4", "blocking",
                    "Reference entries are not numbered, so [n] citations cannot resolve to them.")
        undefined = sorted((no, k) for k, no in cited.items() if keyed and k not in keyed)
        for no, k in undefined:
            doc.add(no, "undefined-citation", "3.4", "blocking", f"Citation [{k.lstrip('^')}] has no matching reference entry.")
        unused = [e for e in entries if e["key"] and e["key"] not in cited]
        if unused:
            doc.add(unused[0]["line"], "uncited-reference", "3.4", "should-fix",
                    f"{len(unused)} reference entries are never cited in the text (lines {compact([e['line'] for e in unused])}).")

    # Entry completeness: author/org, title, publisher, date, URL, access date
    if entries:
        no_url = [e["line"] for e in entries if not re.search(r"https?://|\bdoi\b|10\.\d{4,}/|\b(?:RFC|FIPS|ISO|IEC|SP)\s?[\d-]", e["text"], re.I)]
        no_date = [e["line"] for e in entries if not re.search(r"\b(?:19|20)\d{2}\b", e["text"])]
        no_access = [e["line"] for e in entries if not re.search(r"\b(?:accessed|retrieved|viewed)\b", e["text"], re.I)]
        sev = "blocking" if doc.kind == "whitepaper" else "should-fix"
        for rule, lines, what in (("reference-url", no_url, "a URL or standard identifier"),
                                  ("reference-date", no_date, "a publication date"),
                                  ("reference-accessed", no_access, "an access date")):
            if lines:
                doc.add(lines[0], rule, "3.4", sev, f"{len(lines)} of {len(entries)} references lack {what} (lines {compact(lines)}).")
        news = [e["line"] for e in entries if re.search(r"medium\.com|substack|linkedin\.com|news\.|techcrunch|theverge|wired\.com|zdnet|venturebeat|/blog/", e["text"], re.I)]
        if news:
            doc.add(news[0], "secondary-source", "3.4", "should-fix",
                    f"{len(news)} references look like blogs or news (lines {compact(news)}). Use a primary source where one exists, "
                    "and say so where none does.", heuristic=True)

    # A paper that states its baseline once ("updated for the MCP 2026-07-28 release") may
    # name the specification without a version afterwards; downgrade those to nits.
    baseline = set()
    for m in re.finditer(r"\b(MCP|A2A|ACP)\b[^.\n]{0,40}?\b\d{4}-\d{2}-\d{2}\b|\b\d{4}-\d{2}-\d{2}\b[^.\n]{0,30}?\b(MCP|A2A|ACP)\b", doc.text):
        baseline.add(m.group(1) or m.group(2))
    doc.metrics["spec_baseline"] = sorted(baseline)

    # Uncited factual claims and unversioned specifications, per sentence
    for no, p in paragraphs(doc):
        para_cited = bool(CITATION_MARK_RE.search(p)) or bool(re.search(r"\]\(https?://", doc.lines[no - 1].clean))
        for s in sentences(p):
            if STAT_RE.search(s) and not para_cited:
                doc.add(no, "uncited-claim", "3.4", "blocking",
                        "Statistic or reported fact with no citation in its paragraph.", s, heuristic=True)
                break
        for s in sentences(p):
            spec = MOVING_SPECS_RE.search(s)
            if spec and SPEC_WORD_RE.search(s) and not VERSION_HINT_RE.search(s) and not CITATION_MARK_RE.search(s):
                name = "MCP" if spec.group(0) == "Model Context Protocol" else spec.group(0)
                if name in baseline:
                    doc.add(no, "unversioned-spec", "3.4", "nit",
                            f"Names the {name} specification without a version; the paper states a baseline elsewhere. "
                            "Confirm this claim holds for that revision.", s, heuristic=True)
                else:
                    doc.add(no, "unversioned-spec", "3.4", "blocking",
                            "Names a specification that changes over time without a version or revision date.", s, heuristic=True)


# ---------------------------------------------------------------------------
# White papers (Part 3)
# ---------------------------------------------------------------------------


def git(repo_root: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def check_whitepaper(doc: Doc, repo_root: Path | None):
    published = doc.stage == "approved"
    standalone_sev = "blocking" if published else "pre-approval"

    # §3.1 standalone: no process references
    for ln in doc.lines:
        if ln.code or ln.comment:
            continue
        reported = set()
        for rule, rx, what in PROCESS_PATTERNS:
            m = rx.search(ln.clean)
            if m and rule not in reported:
                reported.add(rule)
                doc.add(ln.no, rule, "3.1", standalone_sev, f"Process reference ({what}): \"{m.group(0).strip()}\".", ln.raw,
                        heuristic=rule in ("meeting", "repo-reference", "github-handle"))
        if not ln.fm:
            m = PLACEHOLDER_RE.search(ln.clean)
            if m:
                doc.add(ln.no, "placeholder", "3.1", standalone_sev, f"Placeholder \"{m.group(0)}\" left in the text.", ln.raw)
    if doc.comment_lines:
        doc.add(doc.comment_lines[0], "html-comment", "3.1", standalone_sev,
                f"{len(doc.comment_lines)} HTML comments (lines {compact(doc.comment_lines)}). "
                "Allowed while drafting; remove before the paper goes for approval.")

    # §3.1 links: absolute URLs, and versioned CoSAI documents
    tags = git(repo_root, "tag", "--list") if repo_root else ""
    for no, is_img, _text, target in iter_links(doc):
        if is_img or not target:
            continue
        if not re.match(r"(?:https?|mailto):|#", target):
            doc.add(no, "relative-link", "3.1", "blocking",
                    "Relative link will break in the PDF; use an absolute URL.", target)
        if re.search(r"github\.com/cosai-oasis/[^/\s]+/(?:blob|tree)/main\b|raw\.githubusercontent\.com/cosai-oasis/[^/\s]+/main\b", target):
            if tags:
                doc.add(no, "unversioned-cosai-link", "3.1", "blocking",
                        "Links to the main branch; cite a tagged release or published PDF.", target)
            else:
                doc.add(no, "unversioned-cosai-link", "3.1", "should-fix",
                        "Links to the main branch. The guide asks for a tagged release, but this repository has no tags yet.", target)

    # §3.2 structure
    addendum = bool(re.match(r"addendum", (doc.path.name if doc.path else doc.label), re.I)) or \
        bool(doc.headings and re.match(r"addendum", doc.headings[0][2], re.I))
    doc.metrics["addendum"] = addendum
    required = [
        ("Abstract", r"^abstract\b", "3.2"),
        ("Executive summary", r"executive summary|^summary$", "3.2"),
        ("Scope", r"^(?:in[- ])?scope\b|\bscope$|scope and", "3.2"),
        ("Out of scope", r"out[- ]of[- ]scope|anti[- ]scope|non[- ]scope|non[- ]goals", "3.2"),
        ("Target audience", r"audience", "3.2"),
        ("References", r"^references\b|^bibliography", "3.4"),
        ("Acknowledgements", r"acknowledg|contributors", "3.1"),
    ]
    for name, rx, sec in required:
        if not has_heading(doc, rx):
            if addendum and name != "References":
                doc.add(1, "missing-section", sec, "should-fix",
                        f"No {name} section. The guide does not say whether addenda are exempt.")
            else:
                doc.add(1, "missing-section", sec, "blocking", f"No {name} section.")
    if not has_heading(doc, r"takeaway|recommendation|conclusion|next steps|what to do"):
        doc.add(1, "missing-section", "3.2", "should-fix", "No Takeaways, Recommendations, or Conclusion section.")
    if not has_heading(doc, r"example|scenario|case study|walkthrough|worked"):
        doc.add(1, "worked-example", "3.2", "nit", "No section headed as a worked example or scenario (Recommended).", heuristic=True)
    if not (has_heading(doc, r"guidelines on usage|ai usage|use of ai") and has_heading(doc, r"copyright")):
        doc.add(1, "cosai-appendix", "AGENTS.md", "should-fix",
                "Missing the standard CoSAI appendix from whitepaper-template.md (AI usage guidelines, copyright).")

    # Conflicting status statements
    statuses = [doc.fm.get("status", "")] + [
        ln.clean for ln in doc.lines if re.match(r"^\W*status\W*:", ln.clean.lstrip("#* "), re.I) and not ln.fm
    ]
    says_draft = any(re.search(r"\bdraft\b", s, re.I) for s in statuses)
    if published and says_draft:
        line = next((ln.no for ln in doc.lines if re.match(r"^\W*status\W*:.*draft", ln.clean.lstrip("#* "), re.I)), 1)
        doc.add(line, "conflicting-status", "1.2", "should-fix", "The paper is marked approved but also says Draft.",
                doc.lines[line - 1].raw)

    # §3.5 versions and changelog
    if not has_heading(doc, r"change ?log|revision history|version history|errata|changes in|what changed"):
        note = " (front matter has a revision_note, which is not a changelog)" if "revision_note" in doc.fm else ""
        doc.add(1, "changelog", "3.5", "blocking" if published else "pre-approval",
                "No changelog or errata section" + note + ".")

    # §3.5 PDF parity
    if doc.path and repo_root:
        pdf = doc.path.with_suffix(".pdf")
        if pdf.exists():
            rel_md, rel_pdf = str(doc.path.relative_to(repo_root)), str(pdf.relative_to(repo_root))
            md_t = git(repo_root, "log", "-1", "--format=%ct", "--", rel_md)
            pdf_t = git(repo_root, "log", "-1", "--format=%ct", "--", rel_pdf)
            if md_t and pdf_t and int(md_t) > int(pdf_t) + 3600:
                md_d = git(repo_root, "log", "-1", "--format=%cs", "--", rel_md)
                pdf_d = git(repo_root, "log", "-1", "--format=%cs", "--", rel_pdf)
                doc.add(1, "pdf-stale", "3.5", "should-fix",
                        f"Markdown last committed {md_d}, PDF {pdf_d}. Check the PDF matches.", heuristic=True)
            dirty = git(repo_root, "status", "--porcelain", "--", rel_md, rel_pdf)
            if any(l.endswith(rel_md) for l in dirty.splitlines()) and not any(l.endswith(rel_pdf) for l in dirty.splitlines()):
                doc.add(1, "pdf-regenerate", "3.5", "nit", "Markdown has uncommitted changes; regenerate the PDF in the same PR.")
        elif published:
            doc.add(1, "pdf-missing", "3.5", "should-fix", "Approved paper with no PDF beside it.")


# ---------------------------------------------------------------------------
# RFCs (Part 2)
# ---------------------------------------------------------------------------

# (name, heading pattern, present in rfc-template.md)
RFC_SECTIONS = [
    ("Summary", r"^summary|^abstract", True),
    ("Problem", r"problem|motivation|\bgap\b|background", False),
    ("Proposed deliverable", r"deliverable|^proposal|^proposed|design overview", False),
    ("Scope", r"\bscope\b|^goals", False),
    ("Non-scope", r"non[- ]?scope|out[- ]of[- ]scope|non[- ]goals|anti[- ]scope", False),
    ("Relationship to existing work", r"related work|existing work|prior art|relationship", True),
    ("Exit criteria", r"exit (?:criteria|gate|conditions)|definition of done|success criteria|acceptance criteria", False),
    ("Priority", r"priority", True),
    ("Level of effort", r"effort", True),
    ("Alternatives", r"alternatives", True),
    ("Drawbacks", r"drawbacks|risks|downsides", True),
    ("Open questions", r"open questions|unresolved questions", True),
    ("References", r"references|reference material|bibliography", True),
]

CONTEXT_RE = re.compile(
    r"\b(?:as (?:we )?discussed|we discussed|per (?:the )?(?:last|tsc|call|meeting|thread|discussion)|"
    r"last (?:week|call|meeting)|on the call|in the (?:tsc|call|meeting|thread)|(?:this|the) thread|"
    r"see (?:the )?slack|on slack|as agreed|we agreed)\b",
    re.I,
)
PERSON_SECTION_RE = re.compile(r"\b[A-Z][a-z]+['’]s (?:thoughts|notes|proposal|comments|views?|ideas|take)\b")


def check_rfc(doc: Doc):
    # §2.2 self-contained
    for ln in doc.body():
        m = CONTEXT_RE.search(ln.clean) or PERSON_SECTION_RE.search(ln.clean)
        if m:
            doc.add(ln.no, "outside-context", "2.2", "blocking",
                    f"Relies on context outside the document: \"{m.group(0)}\". State the point; credit people in Authors.",
                    ln.raw, heuristic=not ln.heading)
        m = PLACEHOLDER_RE.search(ln.clean)
        if m:
            doc.add(ln.no, "placeholder", "2.2", "should-fix", f"Placeholder \"{m.group(0)}\".", ln.raw)

    # §2.3 sections
    authors = has_field(doc, ["author", "authors", "lead", "leads", "editor", "editors"]) or has_heading(doc, r"authors?|leads?")
    if not authors:
        doc.add(1, "missing-section", "2.3", "blocking", "No Authors or Leads.")
    for name, rx, in_template in RFC_SECTIONS:
        if has_heading(doc, rx) or (name in ("Priority", "Level of effort") and has_field(doc, [name.split()[-1].lower()])):
            continue
        if in_template:
            doc.add(1, "missing-section", "2.3", "blocking", f"No {name} section.")
        else:
            doc.add(1, "missing-section", "2.3", "should-fix",
                    f"No {name} section. (STYLE_GUIDE.md requires it, but rfc-template.md does not ask for it yet.)")

    # §2.1 length
    words = word_count(doc)
    doc.metrics["words"] = words
    if words > 1500:
        doc.add(1, "rfc-length", "2.1", "should-fix",
                f"About {words} words; the guide suggests under 1,500. Extra material is probably the deliverable.")

    # §2.4 status
    status = doc.fm.get("status", "")
    if not status:
        for ln in doc.lines[:80]:
            m = re.match(r"^\W*status\W*:\W*(.*)$", ln.clean.lstrip("#* "), re.I)
            if m:
                status = m.group(1)
                break
    doc.metrics["status"] = status
    if not status:
        doc.add(1, "rfc-status", "2.4", "blocking",
                "No status. Use one of Proposed, Accepted, In progress, Completed, Withdrawn (or the label on the issue).")
    else:
        low = status.lower()
        if not any(s in low for s in RFC_STATUSES):
            doc.add(1, "rfc-status", "2.4", "blocking", f"Status \"{status}\" is not one of the defined values.")
        elif any(s in low for s in ("in review", "approved")):
            doc.add(1, "rfc-status-vocab", "2.4", "nit",
                    f"Status \"{status}\" uses the CONTRIBUTING.md terms; STYLE_GUIDE.md uses Proposed/Accepted.")
        if "completed" in low and not re.search(r"whitepapers/|practical-guides/|\.pdf\b", doc.text):
            doc.add(1, "rfc-completed-link", "2.4", "blocking", "Status is Completed but there is no link to the deliverable.")


# ---------------------------------------------------------------------------
# External URLs (§1.3), opt-in
# ---------------------------------------------------------------------------


def fetch_status(url: str) -> tuple[str, int | None, str]:
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "Mozilla/5.0 (cosai-ws4-doc-review link check)", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return url, r.status, ""
    except urllib.error.HTTPError as e:
        return url, e.code, ""
    except Exception as e:  # noqa: BLE001 - report any network failure
        return url, None, type(e).__name__ + ": " + str(e)[:80]


def check_urls(docs: list[Doc]):
    where: dict[str, list[tuple[Doc, int]]] = {}
    for doc in docs:
        for no, _, _, target in iter_links(doc):
            if re.match(r"https?://", target):
                where.setdefault(target.split("#")[0], []).append((doc, no))
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(fetch_status, where))
    for url, code, err in results:
        for doc, no in where[url][:1]:
            if code in (404, 410):
                doc.add(no, "dead-url", "1.3", "blocking", f"HTTP {code}.", url)
            elif code in (401, 403, 429, 999) or (code is None and "timed out" in err):
                doc.add(no, "unverified-url", "1.3", "nit", f"Could not verify ({code or err}); the site may block scripts.", url)
            elif code is None:
                doc.add(no, "dead-url", "1.3", "should-fix", f"Request failed: {err}", url)
            elif code >= 400:
                doc.add(no, "dead-url", "1.3", "should-fix", f"HTTP {code}.", url)
        for doc in {id(d): d for d, _ in where[url]}.values():
            doc.metrics["urls_checked"] = doc.metrics.get("urls_checked", 0) + 1


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def infer_kind(path: str) -> str:
    p = path.replace("\\", "/").lower()
    name = p.rsplit("/", 1)[-1]
    if "/rfcs/" in f"/{p}" or name.startswith("rfc"):
        return "rfc"
    if "/whitepapers/" in f"/{p}" or "whitepaper" in name or name.startswith("addendum"):
        return "whitepaper"
    return "unknown"


def find_repo_root(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return None


def cap_findings(doc: Doc, cap: int):
    if cap <= 0:
        return
    by_rule: dict[tuple[str, str], list[Finding]] = {}
    for f in doc.findings:
        by_rule.setdefault((f.rule, f.severity), []).append(f)
    kept = []
    for (rule, sev), fs in by_rule.items():
        kept += fs[:cap]
        if len(fs) > cap:
            rest = fs[cap:]
            kept.append(Finding(doc.label, rest[0].line, rule, rest[0].section, sev,
                                f"...and {len(rest)} more \"{rule}\" findings on lines {compact([f.line for f in rest], 30)}.",
                                heuristic=rest[0].heuristic))
    doc.findings = kept


def lint(label: str, text: str, kind: str, path: Path | None, allow: set[str], stage: str = "auto") -> Doc:
    repo_root = find_repo_root(path.parent) if path else None
    doc = parse(label, path, text, kind)
    if stage != "auto":
        doc.stage = stage
    check_common(doc, repo_root, allow)
    check_prose(doc)
    if kind == "whitepaper":
        check_whitepaper(doc, repo_root)
        check_citations(doc, numbered_required=True)
    elif kind == "rfc":
        check_rfc(doc)
        check_citations(doc, numbered_required=False)
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="Markdown files, or - for stdin")
    ap.add_argument("--type", choices=["auto", "whitepaper", "rfc"], default="auto")
    ap.add_argument("--stage", choices=["auto", "draft", "approved"], default="auto",
                    help="Override the detected stage (white papers). 'approved' applies published-text rules to a draft.")
    ap.add_argument("--check-urls", action="store_true", help="Fetch every external URL (needs network)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--cap", type=int, default=DEFAULT_CAP, help="Findings per rule before folding the rest (0 = no cap)")
    ap.add_argument("--allow-acronyms", default="", help="Comma-separated acronyms to skip in the first-use check")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="nit")
    args = ap.parse_args(argv)

    allow = {a.strip() for a in args.allow_acronyms.split(",") if a.strip()}
    docs = []
    for f in args.files:
        if f == "-":
            label, text, path = "<stdin>", sys.stdin.read(), None
        else:
            path = Path(f).resolve()
            if not path.is_file():
                print(f"{f}: no such file.", file=sys.stderr)
                return 2
            label, text = f, path.read_text(encoding="utf-8", errors="replace")
        kind = args.type if args.type != "auto" else infer_kind(f)
        if kind == "unknown":
            print(f"{f}: cannot tell whether this is a white paper or an RFC; pass --type.", file=sys.stderr)
            return 2
        docs.append(lint(label, text, kind, path, allow, args.stage))

    if args.check_urls:
        check_urls(docs)

    floor = SEVERITIES.index(args.min_severity)
    for doc in docs:
        doc.findings = [f for f in doc.findings if SEVERITIES.index(f.severity) <= floor]
        doc.findings.sort(key=lambda f: (SEVERITIES.index(f.severity), f.line, f.rule))
        cap_findings(doc, args.cap)
        doc.findings.sort(key=lambda f: (SEVERITIES.index(f.severity), f.line, f.rule))

    if args.format == "json":
        print(json.dumps([{
            "file": d.label, "type": d.kind, "stage": d.stage, "metrics": d.metrics,
            "counts": {s: sum(1 for f in d.findings if f.severity == s) for s in SEVERITIES},
            "findings": [asdict(f) for f in d.findings],
        } for d in docs], indent=2))
    else:
        for d in docs:
            counts = ", ".join(f"{sum(1 for f in d.findings if f.severity == s)} {s}" for s in SEVERITIES)
            print(f"== {d.label} ({d.kind}, {d.stage}): {counts}")
            print("   metrics: " + ", ".join(f"{k}={v}" for k, v in d.metrics.items()))
            for f in d.findings:
                mark = "?" if f.heuristic else " "
                print(f"{mark} {f.file}:{f.line} [{f.severity}] §{f.section} {f.rule}: {f.message}")
                if f.excerpt:
                    print(f"      > {f.excerpt}")
            print()

    blocking = any(f.severity == "blocking" and not f.heuristic for d in docs for f in d.findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
