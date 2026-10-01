#!/usr/bin/env python3
"""Build and check a lead-review body so every round has the same shape.

  review_body.py next [PREV]              print the skeleton for the next round
  review_body.py walk CHECKLIST           print the checklist walk skeleton (a file or a folder)
  review_body.py verify-prompt BODY --diff DIFF --rules DOC [DOC ...]
                                          print the prompt for a fresh-context verifier
  review_body.py check BODY --repo OWNER/REPO --base SHA --verify VERDICTS
                   (--walk WALK --checklist CHECKLIST | --no-checklist) [--prev PREV]
                                          exit 1 and list errors if BODY breaks the format
  review_body.py --self-test

`next` with no PREV prints a Round 1 skeleton with one section per severity.
Delete the sections you do not need and fill every {{...}} placeholder.
With PREV (the body of the last posted round) it copies the table and every
OPEN section, and bumps the round. `check` rejects a body that still has a
placeholder. Standard library only, so it runs under any harness with python3.
"""
import argparse
import hashlib
import os
import re
import sys
from collections import namedtuple

MAX_WORDS = 20  # house ASD-STE100 limit per sentence
MAX_TITLE_WORDS = 12
# LEGACY_SEP: rounds posted before the ASCII switch used a middle dot; parse them, never write them.
SEP = r" (?:\||\u00b7) "
HEADER_RE = re.compile(r"^## Round (\d+)" + SEP + r"(Request Changes|Approve)$")
TABLE_HEAD = ("| ID | Finding | Severity | Status |", "|----|---------|----------|--------|")
ROW_RE = re.compile(r"^\| (F\d+) \| (.+) \| (BLOCKER|NIT|QUESTION) \| (OPEN|RESOLVED|DECLINED|ANSWERED) \|$")
SECTION_RE = re.compile(r"^### (F\d+)" + SEP + r"(.+)" + SEP + r"(BLOCKER|NIT|QUESTION)$")
FIELD_RE = re.compile(r"^\*\*(Gate|CI|Where|Problem|Question|Bug if|Rule|Fix|Done when):\*\* (.+)$")
WHERE_RE = re.compile(r"^(`[^`\s]+:\d+(-\d+)?`(, `[^`\s]+:\d+(-\d+)?`)*|commit `[0-9a-f]{7,40}`|PR description(: .+)?)$")
OPTION_RE = re.compile(r"\b(or|either|alternatively|at minimum)\b", re.IGNORECASE)
PROOF_OPEN = "<details><summary>Proof</summary>"
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BLOB_RE = re.compile(r"^https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
ITEM_RE = re.compile(r"^\s*- \[[ xX]\] (.+)$")
WALK_RE = re.compile(r"^(\S+):L(\d+) \| (PASS|N/A|(FAIL|ASK) (F\d+)) \| ")
VERDICT_RE = re.compile(r"^(F\d+): (OK|RULE|SPLIT|FOLLOWS|OVERRIDE)(?: (.+))?$")
ANCHOR_RE = re.compile(r"#L(\d+)(?:-L(\d+))?")
MAX_SENTENCES = {"Gate": 2, "CI": 2, "Problem": 2, "Question": 2, "Bug if": 1, "Fix": 1, "Done when": 1}

# Field order and required fields per severity. "diff" is a ```diff block.
ORDER = {
    "BLOCKER": ["Where", "Problem", "Rule", "Fix", "diff", "Done when", "Proof"],
    "NIT": ["Where", "Problem", "Fix", "diff", "Done when"],
    "QUESTION": ["Where", "Question", "Bug if", "Proof"],
}
REQUIRED = {
    "BLOCKER": ["Where", "Problem", "Fix", "diff", "Done when"],
    "NIT": ["Where", "Problem", "Fix", "diff", "Done when"],
    "QUESTION": ["Where", "Question", "Bug if"],
}
# The statuses each severity can reach. Every status except OPEN is final.
STATUSES = {"BLOCKER": {"OPEN", "RESOLVED"}, "NIT": {"OPEN", "RESOLVED", "DECLINED"}, "QUESTION": {"OPEN", "ANSWERED"}}

Row = namedtuple("Row", "id title sev status")


def num(fid):
    return int(fid[1:])


def plain(text):
    text = re.sub(r"`[^`]*`", "CODE", text)
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)


def check_field(label, name, value, errs):
    option = OPTION_RE.search(plain(value)) if name == "Fix" else None
    if option:
        errs.append(f"{label}: offers options ({option[0]!r}). Pick one fix.")
    if name == "Where" and not WHERE_RE.match(value):
        errs.append(f"{label}: use `path:line` items separated by commas, commit `<sha>`, or PR description: <part>.")
    if name not in MAX_SENTENCES:
        return
    parts = [p for p in re.split(r"(?<=[.!?])\s+", plain(value).strip()) if p]
    if len(parts) > MAX_SENTENCES[name]:
        errs.append(f"{label}: {len(parts)} sentences, limit {MAX_SENTENCES[name]}. Move detail into Proof or cut it.")
    for p in parts:
        if len(p.split()) > MAX_WORDS:
            errs.append(f"{label}: sentence over {MAX_WORDS} words: {p[:50]!r}... Split or shorten it.")


def split_body(body, errs=None):
    """Split into the part before the first finding and one list per finding.

    The `---` separator before each finding heading is removed. With `errs`,
    a missing separator, or one with no blank line above it, is an error.
    """
    top, sections, cur, fence = [], [], None, False
    for ln in body.replace("\r\n", "\n").split("\n"):
        if ln.startswith("```"):
            fence = not fence
        if not fence and ln.startswith("### "):
            prior = cur if cur is not None else top
            while prior and not prior[-1].strip():
                prior.pop()
            if prior and prior[-1] == "---":
                prior.pop()
                if prior and prior[-1].strip() and errs is not None:
                    errs.append(f"'---' above {ln[:12]!r} needs a blank line above it, or Markdown turns the line above into a heading")
            elif errs is not None:
                errs.append(f"put a '---' line, with a blank line above it, before {ln[:12]!r}")
            cur = [ln]
            sections.append(cur)
            continue
        (cur if cur is not None else top).append(ln)
    return top, sections


def parse_top(top, errs):
    lines = [l for l in top if l.strip()]
    info = {"round": None, "verdict": None, "rows": []}
    if not lines:
        errs.append("body is empty")
        return info
    m = HEADER_RE.match(lines[0])
    if m:
        info["round"], info["verdict"] = int(m[1]), m[2]
    else:
        errs.append(f"line 1 must be '## Round <N> | Request Changes' or '## Round <N> | Approve', got {lines[0]!r}")
    t = next((k for k in range(len(lines) - 1) if tuple(lines[k:k + 2]) == TABLE_HEAD), None)
    if t is None:
        errs.append("missing the status table header, exactly: " + " / ".join(TABLE_HEAD))
        t = len(lines)
    pre = lines[1:t]
    for k, name in enumerate(("Gate", "CI")):
        fm = FIELD_RE.match(pre[k]) if k < len(pre) else None
        if fm and fm[1] == name:
            check_field(name, name, fm[2], errs)
        else:
            errs.append(f"line {k + 2} of the body must be '**{name}:** ...'; the header is followed by Gate, then CI")
    for extra in pre[2:]:
        errs.append(f"text outside the skeleton: {extra[:60]!r}. Give it a finding ID or cut it.")
    i = t + 2
    while i < len(lines) and lines[i].startswith("|"):
        rm = ROW_RE.match(lines[i])
        if rm:
            row = Row(*rm.groups())
            info["rows"].append(row)
            if row.status not in STATUSES[row.sev]:
                errs.append(f"{row.id}: a {row.sev} cannot be {row.status}; allowed: {', '.join(sorted(STATUSES[row.sev]))}")
            if "|" in row.title:
                errs.append(f"{row.id}: a title cannot contain '|'; it breaks the table")
            if len(plain(row.title).split()) > MAX_TITLE_WORDS:
                errs.append(f"{row.id}: title over {MAX_TITLE_WORDS} words. One finding, one short title.")
        else:
            errs.append(f"bad table row {lines[i]!r}; use '| F<N> | <title> | BLOCKER|NIT|QUESTION | <status> |'")
        i += 1
    for extra in lines[i:]:
        errs.append(f"text outside the skeleton: {extra[:60]!r}. Give it a finding ID or cut it.")
    ids = [r.id for r in info["rows"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate finding IDs in the table")
    if [num(x) for x in ids] != sorted(num(x) for x in ids):
        errs.append("table rows must be in ID order")
    return info


def check_section(sec, rows, errs, rules):
    m = SECTION_RE.match(sec[0])
    if not m:
        errs.append(f"bad heading {sec[0]!r}; use '### F<N> | <title> | BLOCKER|NIT|QUESTION'")
        return None
    fid, title, sev = m.groups()
    row = rows.get(fid)
    if row is None:
        errs.append(f"{fid}: section has no table row")
    else:
        if (row.title, row.sev) != (title, sev):
            errs.append(f"{fid}: heading title and severity must match the table row exactly")
        if row.status != "OPEN":
            errs.append(f"{fid}: only OPEN findings get a section; drop it")
    order = ORDER[sev]
    seen, last, i = [], -1, 1
    while i < len(sec):
        ln = sec[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("```"):
            item, j = "diff", i + 1
            while j < len(sec) and not sec[j].startswith("```"):
                j += 1
            if ln[3:].strip() != "diff":
                errs.append(f"{fid}: a code block outside Proof must be a ```diff block")
            if j == len(sec):
                errs.append(f"{fid}: code block is not closed")
            i = j + 1
        elif ln.strip() == PROOF_OPEN:
            item, j = "Proof", i + 1
            while j < len(sec) and sec[j].strip() != "</details>":
                j += 1
            if j == len(sec):
                errs.append(f"{fid}: Proof has no closing </details>")
            i = j + 1
        else:
            fm = FIELD_RE.match(ln)
            if not fm or fm[1] in ("Gate", "CI"):
                errs.append(f"{fid}: text outside a field: {ln[:60]!r}. Put evidence in Proof, give a new ask its own ID, or cut it.")
                i += 1
                continue
            item = fm[1]
            check_field(f"{fid} {item}", item, fm[2], errs)
            if item == "Rule":
                rules[fid] = fm[2]
            i += 1
        if item not in order:
            if sev == "NIT" and item in ("Rule", "Proof"):
                errs.append(f"{fid}: has {item}, so it is not arguable. Mark it BLOCKER.")
            else:
                errs.append(f"{fid}: a {sev} has no {item}; its fields are " + ", ".join(order))
            continue
        pos = order.index(item)
        if pos < last or (pos == last and item != "diff"):
            errs.append(f"{fid}: '{item}' is out of order or repeated; order is " + ", ".join(order))
        last = max(last, pos)
        seen.append(item)
    for r in REQUIRED[sev]:
        if r not in seen:
            errs.append(f"{fid}: missing {r}")
    if sev == "BLOCKER" and "Rule" not in seen and "Proof" not in seen:
        errs.append(f"{fid}: a BLOCKER needs Rule or Proof. With neither, it is arguable: mark it NIT.")
    return fid


def check_prose(body, errs, repo=None, shas=None):
    fence = False
    for n, ln in enumerate(body.replace("\r\n", "\n").split("\n"), 1):
        if "{{" in ln:
            errs.append(f"line {n}: unfilled placeholder {{{{...}}}}")
        if ln.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        text = re.sub(r"`[^`]*`", "", ln)
        if "\u00b7" in text:
            errs.append(f"line {n}: middle dot; the separator is ' | '")
        elif "\u2014" in text or "\u2013" in text:
            errs.append(f"line {n}: em or en dash; use a period or a comma")
        elif EMOJI_RE.search(text):
            errs.append(f"line {n}: emoji")
        elif any(ord(c) > 127 for c in text):
            errs.append(f"line {n}: non-ASCII {next(c for c in text if ord(c) > 127)!r} outside code; ASCII only")
        if re.search(r"(^|\s)--(\s|$)", text):
            errs.append(f"line {n}: '--' in prose")
        for url in LINK_RE.findall(text):
            if not url.startswith("https://"):
                errs.append(f"line {n}: link {url!r} must be an absolute https URL")
                continue
            blob = BLOB_RE.match(url)
            if blob is None:
                continue
            if repo and blob[1] != repo:
                errs.append(f"line {n}: link points to {blob[1]}, not {repo}. Link only this repo's files.")
            if not SHA_RE.match(blob[2]):
                errs.append(f"line {n}: pin {url!r} to the 40-character base commit SHA, not a branch")
            elif shas and blob[2] not in shas:
                errs.append(f"line {n}: link uses {blob[2][:12]}, which is neither the base SHA nor in the previous round")


def body_hash(body):
    # Layout does not change what the verifier judged: skip `---` lines and repeated blank lines.
    kept, fence = [], False
    for ln in body.replace("\r\n", "\n").strip().split("\n"):
        if ln.startswith("```"):
            fence = not fence
        if not fence and (ln == "---" or (not ln.strip() and kept and not kept[-1].strip())):
            continue
        kept.append(ln)
    return hashlib.sha256("\n".join(kept).encode()).hexdigest()[:12]


def load_docs(path):
    """Read a checklist or rule doc as [(key, text)].

    A single file (the shape of every older project) keys by its name. A folder
    (docs/<name>/_index.md plus NN-section.md) keys each file as <folder>/<file>.
    A rule link cites an item when its URL contains the key.
    """
    if os.path.isdir(path):
        base = os.path.basename(os.path.normpath(path))
        return [(f"{base}/{f}", read(os.path.join(path, f))) for f in sorted(os.listdir(guard(path))) if f.endswith(".md")]
    return [(os.path.basename(path), read(path))]


def checklist_items(docs):
    items = {}
    for key, text in docs:
        for n, ln in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
            m = ITEM_RE.match(ln)
            if m:
                items[(key, n)] = m[1]
    return items


def walk_skeleton(docs):
    return "".join(f"{key}:L{n} | {{{{PASS|FAIL F<n>|ASK F<n>|N/A}}}} | {item}\n"
                   for (key, n), item in checklist_items(docs).items())


def cites(rule, key, n):
    for url in LINK_RE.findall(rule):
        if key in url:
            for a in ANCHOR_RE.finditer(url):
                if int(a[1]) <= n <= int(a[2] or a[1]):
                    return True
    return False


def check_walk(walk, docs, rows, rules, errs):
    items = checklist_items(docs)
    if not items:
        errs.append(f"walk: {', '.join(k for k, _ in docs)} has no '- [ ]' items, so nothing was walked")
    verdicts = {}
    for ln in (l for l in walk.replace("\r\n", "\n").split("\n") if l.strip()):
        m = WALK_RE.match(ln)
        if not m:
            errs.append(f"walk: bad line {ln[:60]!r}; use '<file>:L<n> | PASS|N/A|FAIL F<n>|ASK F<n> | <item>'")
            continue
        item = (m[1], int(m[2]))
        if item not in items:
            errs.append(f"walk: {m[1]}:L{m[2]} is not a checklist item")
        elif item in verdicts:
            errs.append(f"walk: {m[1]}:L{m[2]} appears twice")
        else:
            verdicts[item] = (m[4], m[5]) if m[4] else None
    for key, n in items:
        if (key, n) not in verdicts:
            errs.append(f"walk: checklist item {key}:L{n} has no verdict")
    for (key, n), verdict in verdicts.items():
        if verdict is None:
            continue
        kind, fid = verdict
        row = rows.get(fid)
        if kind == "ASK":
            if row is None or row.sev != "QUESTION" or row.status != "OPEN":
                errs.append(f"walk: {key}:L{n} asks as {fid}, so {fid} must be an OPEN QUESTION")
        elif row is None or row.sev != "BLOCKER" or row.status != "OPEN":
            errs.append(f"walk: {key}:L{n} fails as {fid}, so {fid} must be an OPEN BLOCKER")
        elif not cites(rules.get(fid, ""), key, n):
            errs.append(f"walk: {key}:L{n} fails as {fid}, so {fid}'s Rule must link {key}#L{n}")
    for fid, rule in rules.items():
        for key, n in items:
            if cites(rule, key, n) and verdicts.get((key, n)) != ("FAIL", fid):
                errs.append(f"{fid}: its Rule cites {key} L{n}, so the walk must say '{key}:L{n} | FAIL {fid}'")


def check_verify(verify, body, rows, errs):
    lines = [l.strip() for l in verify.replace("\r\n", "\n").split("\n") if l.strip()]
    if not lines or lines[0] != f"Body: {body_hash(body)}":
        errs.append("verify: first line must be 'Body: " + body_hash(body) + "'. The body changed, or the verifier skipped it. Rerun the verifier.")
    open_ids = {r.id for r in rows.values() if r.status == "OPEN"}
    judged, flagged, overridden = set(), {}, {}
    for ln in lines[1:]:
        m = VERDICT_RE.match(ln)
        if not m:
            errs.append(f"verify: bad line {ln[:60]!r}; use 'F<n>: OK', 'F<n>: RULE|SPLIT|FOLLOWS <detail>' or 'F<n>: OVERRIDE <reason>'")
        elif m[1] not in open_ids:
            errs.append(f"verify: {m[1]} is not an OPEN finding")
        elif m[2] == "OVERRIDE":
            if not m[3]:
                errs.append(f"verify: {m[1]} OVERRIDE needs a reason")
            overridden[m[1]] = m[3] or ""
        else:
            judged.add(m[1])
            if m[2] != "OK":
                flagged.setdefault(m[1], []).append(f"{m[2]} {m[3] or ''}".strip())
    for fid, verdicts in flagged.items():
        if fid not in overridden:
            errs.append(f"{fid}: verifier says {'; '.join(verdicts)}. Fix the body and rerun the verifier, or override with the user's approval.")
    for fid in overridden:
        if fid not in flagged:
            errs.append(f"verify: {fid} OVERRIDE has no verifier flag to override")
    for fid in sorted(open_ids - judged, key=num):
        errs.append(f"verify: {fid} has no verdict")


def overrides(verify):
    return [ln.strip() for ln in verify.split("\n") if re.match(r"^F\d+: OVERRIDE ", ln.strip())]


def cited_paths(body):
    """The file paths the findings' Where lines name."""
    paths = set()
    for m in re.finditer(r"^\*\*Where:\*\* (.+)$", body, re.M):
        paths.update(re.findall(r"`([^`\s]+?):\d+(?:-\d+)?`", m.group(1)))
    return paths


def trim_diff(diff, paths):
    """Keep only the per-file sections of a unified diff whose path a finding cites."""
    sections = re.split(r"(?m)^(?=diff --git )", diff)
    kept = [sec for sec in sections if any(f" b/{p}\n" in sec.split("\n", 1)[0] + "\n" for p in paths)]
    others = sorted({re.match(r"diff --git a/(\S+)", sec).group(1) for sec in sections
                     if sec.startswith("diff --git") and sec not in kept})
    note = "Other files the diff changes (no finding cites them): " + ", ".join(others) + "\n\n" if others else ""
    return note + "".join(kept)


def verify_prompt(body, diff, docs, full_diff=False):
    here = os.path.dirname(os.path.abspath(__file__))
    template = open(os.path.join(here, "..", "verify.md"), encoding="utf-8").read()
    out = [template.replace("$HASH", body_hash(body)), "\n===== REVIEW BODY =====\n", body]
    for path, text in docs:
        out += [f"\n===== RULE DOC: {path} =====\n", text]
    out += ["\n===== DIFF =====\n", diff if full_diff else trim_diff(diff, cited_paths(body))]
    return "\n".join(out)


def check(body, prev=None, repo=None, base=None, walk=None, checklist=None, verify=None):
    errs = []
    top, sections = split_body(body, errs)
    info = parse_top(top, errs)
    rows = {r.id: r for r in info["rows"]}
    rules = {}
    detailed = {check_section(s, rows, errs, rules) for s in sections}
    if checklist is not None:
        check_walk(walk or "", checklist, rows, rules, errs)
    if verify is not None:
        check_verify(verify, body, rows, errs)
    for r in info["rows"]:
        if r.status == "OPEN" and r.id not in detailed:
            errs.append(f"{r.id}: OPEN finding has no section")
    still_open = [r.id for r in info["rows"] if r.status == "OPEN"]
    want = "Request Changes" if still_open else "Approve"
    if info["verdict"] and info["verdict"] != want:
        errs.append(f"verdict must be '{want}': " + (f"{', '.join(still_open)} still OPEN" if still_open else "nothing is OPEN"))
    shas = {base} | set(re.findall(r"/blob/([0-9a-f]{40})/", prev or "")) if base else None
    check_prose(body, errs, repo, shas)
    if prev is not None:
        perrs = []
        p = parse_top(split_body(prev)[0], perrs)
        if perrs:
            errs.append("previous round does not parse: " + perrs[0])
        if p["round"] and info["round"] != p["round"] + 1:
            errs.append(f"round must be {p['round'] + 1}")
        for r in p["rows"]:
            c = rows.get(r.id)
            if c is None:
                errs.append(f"{r.id}: dropped; every ID stays in the table for good")
            elif (c.title, c.sev) != (r.title, r.sev):
                errs.append(f"{r.id}: title and severity are frozen; copy them from the previous round")
            elif r.status != "OPEN" and c.status != r.status:
                errs.append(f"{r.id}: {r.status} is final; file anything new under a new ID")
        top_id = max((num(r.id) for r in p["rows"]), default=0)
        for c in info["rows"]:
            if c.id not in {r.id for r in p["rows"]} and num(c.id) <= top_id:
                errs.append(f"{c.id}: a new finding takes an ID above F{top_id}")
    return errs


SKELETON_SECTIONS = """---

### F1 | {{title, 12 words at most}} | BLOCKER

**Where:** {{`path:line`}}
**Problem:** {{what is wrong and what it breaks, two sentences at most}}
**Rule:** {{[doc section](https://github.com/OWNER/REPO/blob/BASE_SHA/path?plain=1#Ln) "rule quoted verbatim"; delete this line if Proof is given}}
**Fix:** {{one sentence, one approach}}

```diff
- {{code from the PR}}
+ {{replacement}}
```

**Done when:** {{one sentence the author can check}}

<details><summary>Proof</summary>

{{reproduction output or file:line trace; delete this block if Rule is given}}

</details>

---

### F2 | {{title}} | NIT

**Where:** {{`path:line`}}
**Problem:** {{what you prefer and why, two sentences at most}}
**Fix:** {{one sentence, one approach}}

```diff
- {{code from the PR}}
+ {{replacement}}
```

**Done when:** {{one sentence the author can check}}

---

### F3 | {{title}} | QUESTION

**Where:** {{`path:line`}}
**Question:** {{what only the author knows, two sentences at most}}
**Bug if:** {{the answer that turns this into a BLOCKER}}
"""


def next_round(prev=None):
    head = ["", "**Gate:** {{command and result}}", "**CI:** {{result}}", "", *TABLE_HEAD]
    if prev is None:
        rows = ["| F1 | {{title}} | BLOCKER | OPEN |", "| F2 | {{title}} | NIT | OPEN |", "| F3 | {{title}} | QUESTION | OPEN |"]
        return "\n".join(["## Round 1 | {{Request Changes|Approve}}", *head, *rows, "", SKELETON_SECTIONS])
    errs = []
    top, sections = split_body(prev)
    info = parse_top(top, errs)
    if errs:
        sys.exit("previous round does not parse:\n  " + "\n  ".join(errs))
    close = {"BLOCKER": "RESOLVED if Done when holds", "NIT": "RESOLVED if Done when holds, DECLINED if the author gave a reason",
             "QUESTION": "ANSWERED if the author answered"}
    out = [f"## Round {info['round'] + 1} | {{{{Request Changes|Approve}}}}", *head]
    out += [f"| {r.id} | {r.title} | {r.sev} | {{{{OPEN, or {close[r.sev]}}}}} |"
            if r.status == "OPEN" else f"| {r.id} | {r.title} | {r.sev} | {r.status} |" for r in info["rows"]]
    out.append("")
    open_ids = {r.id for r in info["rows"] if r.status == "OPEN"}
    for s in sections:
        m = SECTION_RE.match(s[0])
        if m and m[1] in open_ids:
            out += ["---", "", *s]
    return "\n".join(out).rstrip() + "\n"


GOOD = """## Round 1 | Request Changes

**Gate:** `make check` passes.
**CI:** Passes.

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F1 | Guard rejects owners | BLOCKER | OPEN |
| F2 | Dead check | NIT | OPEN |
| F3 | Retry count source | QUESTION | OPEN |

---

### F1 | Guard rejects owners | BLOCKER

**Where:** `a.ts:3`, `b.ts:10-12`
**Problem:** The guard throws for the owning project.
**Rule:** [STD 1](https://github.com/o/r/blob/0123456789abcdef0123456789abcdef01234567/STD.md?plain=1#L1) "Owners pass."
**Fix:** Compare the project id.

```diff
- if (x) throw e;
+ if (!x) throw e;
```

**Done when:** A test passes the owning project through the guard.

<details><summary>Proof</summary>

```text
GET /p/a -> 404
```

</details>

---

### F2 | Dead check | NIT

**Where:** `b.ts:9`
**Problem:** The null check never fires.
**Fix:** Delete the check.

```diff
- if (r === null) throw e;
```

**Done when:** The line is gone and `tsc` passes.

---

### F3 | Retry count source | QUESTION

**Where:** `c.ts:4`
**Question:** Does the vendor cap retries at 3?
**Bug if:** The vendor allows fewer than 5 retries.
"""


def self_test():
    assert check(GOOD) == [], check(GOOD)
    assert check(GOOD.replace("---\n\n### F2", "### F2")), "missing separator not caught"
    assert check(GOOD.replace("tsc` passes.\n\n---", "tsc` passes.\n---")), "separator with no blank line above not caught"
    assert body_hash(GOOD) == body_hash(GOOD.replace("---\n\n", "")), "separators must not change the hash"
    no_proof = GOOD.replace("<details><summary>Proof</summary>\n\n```text\nGET /p/a -> 404\n```\n\n</details>\n", "")
    assert check(no_proof) == [], "BLOCKER with Rule only must pass"
    sha = "0123456789abcdef0123456789abcdef01234567"
    assert check(GOOD, repo="o/r", base=sha) == [], check(GOOD, repo="o/r", base=sha)
    assert check(GOOD, repo="acme/app", base=sha), "link to another repo not caught"
    assert check(GOOD, repo="o/r", base="f" * 40), "link off the base SHA not caught"
    assert check(GOOD.replace("Round 1", "Round 2"), prev=GOOD, repo="o/r", base="f" * 40) == [], "SHA from prev must pass"
    bad = {
        "missing Done when": GOOD.replace("**Done when:** The line is gone and `tsc` passes.\n", ""),
        "stray prose": GOOD.replace("**Fix:** Delete the check.", "**Fix:** Delete the check.\nAlso consider a refactor."),
        "em dash": GOOD.replace("never fires.", "never fires \u2014 ever."),
        "dot in prose": GOOD.replace("never fires.", "never fires \u00b7 ever."),
        "legacy dot header": GOOD.replace("Round 1 | Request", "Round 1 \u00b7 Request"),
        "arrow": GOOD.replace("never fires.", "never fires \u2192 ever."),
        "pipe in title": GOOD.replace("Dead check", "Dead | check"),
        "branch link": GOOD.replace("0123456789abcdef0123456789abcdef01234567", "main"),
        "verdict with open NIT": GOOD.replace("Request Changes", "Approve"),
        "BLOCKER with neither": no_proof.replace(no_proof[no_proof.index("**Rule:**"):no_proof.index("**Fix:** Compare")], ""),
        "NIT with Rule": GOOD.replace("**Fix:** Delete the check.", '**Rule:** [S](https://x.y/z) "q"\n**Fix:** Delete the check.'),
        "two fixes": GOOD.replace("Compare the project id.", "Compare the project id. Then move the guard."),
        "options in Fix": GOOD.replace("Compare the project id.", "Compare the id or the slug."),
        "long sentence": GOOD.replace("never fires.", "never fires because " + "very " * 20 + "late."),
        "long title": GOOD.replace("Dead check", "Dead check " + "word " * 12),
        "bad Where": GOOD.replace("**Where:** `b.ts:9`", "**Where:** somewhere in b.ts"),
        "placeholder": GOOD.replace("Passes.", "{{result}}"),
        "placeholder in diff": GOOD.replace("+ if (!x) throw e;", "+ {{replacement}}"),
        "QUESTION without Bug if": GOOD.replace("**Bug if:** The vendor allows fewer than 5 retries.\n", ""),
        "QUESTION with Fix": GOOD.replace("**Bug if:** The vendor", "**Fix:** Ask.\n**Bug if:** The vendor"),
        "DECLINED BLOCKER": GOOD.replace("| BLOCKER | OPEN |", "| BLOCKER | DECLINED |"),
        "ANSWERED NIT": GOOD.replace("| NIT | OPEN |", "| NIT | ANSWERED |"),
    }
    for name, body in bad.items():
        assert check(body), f"self-test: '{name}' was not caught"
    r2 = (GOOD.replace("Round 1", "Round 2").replace("| NIT | OPEN |", "| NIT | DECLINED |")
          .replace("| QUESTION | OPEN |", "| QUESTION | ANSWERED |"))
    r2 = r2[:r2.index("---\n\n### F2")]
    assert check(r2, prev=GOOD) == [], check(r2, prev=GOOD)
    assert check(r2.replace("| F2 | Dead check | NIT | DECLINED |\n", ""), prev=GOOD), "dropped ID not caught"
    assert check(r2.replace("Dead check | NIT", "Dead code | NIT"), prev=GOOD), "renamed title not caught"
    r3 = r2.replace("Round 2", "Round 3").replace("| NIT | DECLINED |", "| NIT | RESOLVED |")
    assert check(r3, prev=r2), "a final status change was not caught"
    r2_low = r2.replace("| F1 |", "| F0 | Scope | NIT | OPEN |\n| F1 |", 1)
    assert any("above F3" in e for e in check(r2_low, prev=GOOD)), "new ID below the previous top not caught"
    legacy = "\n".join(l.replace(" | ", " \u00b7 ") if l.startswith(("## Round", "### F")) else l
                        for l in GOOD.split("\n"))
    assert "\u00b7" in legacy and check(r2, prev=legacy) == [], check(r2, prev=legacy)
    assert next_round(legacy).startswith("## Round 2 | "), "legacy prev must yield an ASCII round"
    nxt = next_round(GOOD)
    assert nxt.startswith("## Round 2 | ") and "| F1 | Guard rejects owners | BLOCKER |" in nxt and "### F3 |" in nxt
    skeleton = next_round()
    assert "{{" in skeleton and all(f"### F{n} |" in skeleton for n in (1, 2, 3))
    items = "- [ ] Owners pass.\n- [ ] No dead code.\n"
    one_file = [("STD.md", items)]
    walk = "STD.md:L1 | FAIL F1 | Owners pass.\nSTD.md:L2 | PASS | No dead code.\n"
    assert check(GOOD, walk=walk, checklist=one_file) == [], check(GOOD, walk=walk, checklist=one_file)
    walk_bad = {
        "unfilled verdict": walk_skeleton(one_file),
        "missing item": "STD.md:L1 | FAIL F1 | Owners pass.\n",
        "FAIL on a NIT": "STD.md:L1 | FAIL F1 | Owners pass.\nSTD.md:L2 | FAIL F2 | No dead code.\n",
        "FAIL without matching Rule": "STD.md:L1 | PASS | Owners pass.\nSTD.md:L2 | FAIL F1 | No dead code.\n",
        "Rule cites a PASS item": "STD.md:L1 | PASS | Owners pass.\nSTD.md:L2 | PASS | No dead code.\n",
        "ASK on a BLOCKER": "STD.md:L1 | FAIL F1 | Owners pass.\nSTD.md:L2 | ASK F1 | No dead code.\n",
        "no file in the key": "L1 | FAIL F1 | Owners pass.\nL2 | PASS | No dead code.\n",
    }
    for name, w in walk_bad.items():
        assert check(GOOD, walk=w, checklist=one_file), f"self-test: walk '{name}' was not caught"
    walk_ask = "STD.md:L1 | FAIL F1 | Owners pass.\nSTD.md:L2 | ASK F3 | No dead code.\n"
    assert check(GOOD, walk=walk_ask, checklist=one_file) == [], "ASK on a QUESTION must pass"
    folder = [("std/_index.md", "# Checklist\n"), ("std/01-owners.md", "# Owners\n\n- [ ] Owners pass.\n"),
              ("std/02-code.md", "- [ ] No dead code.\n")]
    good_folder = GOOD.replace("/STD.md?plain=1#L1", "/docs/std/01-owners.md?plain=1#L3")
    walk_folder = "std/01-owners.md:L3 | FAIL F1 | Owners pass.\nstd/02-code.md:L1 | PASS | No dead code.\n"
    assert check(good_folder, walk=walk_folder, checklist=folder) == [], check(good_folder, walk=walk_folder, checklist=folder)
    assert walk_skeleton(folder).startswith("std/01-owners.md:L3 | "), walk_skeleton(folder)
    assert check(good_folder, walk=walk_folder.replace("01-owners.md:L3", "02-code.md:L3"), checklist=folder), "wrong file not caught"
    assert check(GOOD, walk=walk_folder, checklist=folder), "Rule linking another file not caught"
    ok = f"Body: {body_hash(GOOD)}\nF1: OK\nF2: OK\nF3: OK\n"
    assert check(GOOD, verify=ok) == [], check(GOOD, verify=ok)
    verify_bad = {
        "missing ID": ok.replace("F3: OK\n", ""),
        "non-OK verdict": ok.replace("F2: OK", "F2: RULE STD.md#L2"),
        "unknown ID": ok + "F9: OK\n",
        "stale body": ok.replace(body_hash(GOOD), "0" * 12),
        "override without reason": ok.replace("F2: OK", "F2: RULE STD.md#L2\nF2: OVERRIDE"),
        "override with no flag": ok + "F1: OVERRIDE not needed\n",
    }
    for name, v in verify_bad.items():
        assert check(GOOD, verify=v), f"self-test: verify '{name}' was not caught"
    overridden = ok.replace("F2: OK", "F2: RULE STD.md#L2\nF2: OVERRIDE the diff follows L2")
    assert check(GOOD, verify=overridden) == [], check(GOOD, verify=overridden)
    assert overrides(overridden) == ["F2: OVERRIDE the diff follows L2"]
    diff = ("diff --git a/a.ts b/a.ts\n--- a/a.ts\n+++ b/a.ts\n@@ -1 +1 @@\n-x\n+y\n"
            "diff --git a/z.ts b/z.ts\n--- a/z.ts\n+++ b/z.ts\n@@ -1 +1 @@\n-p\n+q\n")
    assert cited_paths(GOOD) == {"a.ts", "b.ts", "c.ts"}, cited_paths(GOOD)
    trimmed = trim_diff(diff, cited_paths(GOOD))
    assert "diff --git a/a.ts" in trimmed and "+q" not in trimmed and "z.ts" in trimmed, trimmed
    two = diff + "diff --git a/a.ts b/a.ts\n--- a/a.ts\n+++ b/a.ts\n@@ -1 +1 @@\n-y\n+w\n"
    assert "+y" in trim_diff(two, {"a.ts"}) and "+w" in trim_diff(two, {"a.ts"}), "an audit's second patch to a file was dropped"
    # The unattended-mode guard: fails closed, and refuses .. and symlinks that leave the roots.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        inside = os.path.join(d, "in")
        os.makedirs(inside)
        ok_file = os.path.join(inside, "a.md")
        with open(ok_file, "w") as fh:
            fh.write("x")
        os.symlink(os.path.realpath(__file__), os.path.join(inside, "link.md"))
        saved = {k: os.environ.get(k) for k in ("LEAD_REVIEW_UNATTENDED", "LEAD_REVIEW_ROOTS")}

        def refused(path):
            try:
                guard(path)
            except SystemExit:
                return True
            return False
        try:
            os.environ["LEAD_REVIEW_UNATTENDED"] = "1"
            os.environ.pop("LEAD_REVIEW_ROOTS", None)
            assert refused(ok_file), "unattended mode with no roots must refuse every file"
            os.environ["LEAD_REVIEW_ROOTS"] = inside
            assert not refused(ok_file), "a file under the roots must pass"
            assert refused(os.path.join(inside, "..", "..", "..", "etc", "hosts")), "a .. escape must be refused"
            assert refused(os.path.join(inside, "link.md")), "a symlink out of the roots must be refused"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    print("self-test OK")



def guard(path):
    """Unattended mode (a review bot holding credentials) reads only files whose real path lies under
    LEAD_REVIEW_ROOTS, a colon-separated list. Without it, it reads nothing: the guard fails closed.
    The real path counts, so `..` segments and symlinks that leave the roots are refused."""
    if os.environ.get("LEAD_REVIEW_UNATTENDED") != "1":
        return path
    roots = [os.path.realpath(r) for r in os.environ.get("LEAD_REVIEW_ROOTS", "").split(":") if r]
    real = os.path.realpath(path)
    if not any(real == r or real.startswith(r + os.sep) for r in roots):
        sys.exit(f"unattended mode: {path!r} is outside LEAD_REVIEW_ROOTS; refused")
    return path

def read(path):
    with open(guard(path), encoding="utf-8") as f:
        return f.read()


def main(argv):
    if argv[:1] in (["self-test"], ["--self-test"]):
        return self_test()
    if argv[:1] == ["next"] and len(argv) <= 2:
        sys.stdout.write(next_round(read(argv[1]) if len(argv) == 2 else None))
        return
    if argv[:1] == ["walk"] and len(argv) == 2:
        sys.stdout.write(walk_skeleton(load_docs(argv[1])))
        return
    if argv[:1] == ["verify-prompt"]:
        ap = argparse.ArgumentParser(prog="review_body.py verify-prompt")
        ap.add_argument("body")
        ap.add_argument("--diff", required=True)
        ap.add_argument("--rules", required=True, nargs="+", help="files or folders: checklist, standard, CLAUDE.md, cited specs")
        ap.add_argument("--full-diff", action="store_true", help="embed the whole diff, not only the files findings cite")
        a = ap.parse_args(argv[1:])
        docs = [(os.path.join(os.path.dirname(os.path.normpath(p)), k), t) for p in a.rules for k, t in load_docs(p)]
        prompt = verify_prompt(read(a.body), read(a.diff), docs, a.full_diff)
        sys.stdout.write(prompt)
        print(f"verify prompt: {len(prompt.encode()) // 1024} KB", file=sys.stderr)
        return
    if argv[:1] == ["check"]:
        ap = argparse.ArgumentParser(prog="review_body.py check")
        ap.add_argument("body")
        ap.add_argument("--repo", required=True, help="OWNER/REPO of the PR")
        ap.add_argument("--base", required=True, help="the PR's baseRefOid")
        ap.add_argument("--verify", required=True, help="the verifier's output")
        ap.add_argument("--walk")
        ap.add_argument("--checklist", help="the review checklist: one file, or a folder of section files")
        ap.add_argument("--no-checklist", action="store_true", help="only when the repo has no review checklist")
        ap.add_argument("--prev")
        a = ap.parse_args(argv[1:])
        if not a.no_checklist and not (a.walk and a.checklist):
            ap.error("pass --walk and --checklist, or --no-checklist when the repo has no review checklist")
        checklist = None if a.no_checklist else load_docs(a.checklist)
        errs = check(read(a.body), read(a.prev) if a.prev else None, a.repo, a.base,
                     read(a.walk) if a.walk else None, checklist, read(a.verify))
        if errs:
            print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
            sys.exit(1)
        for line in overrides(read(a.verify)):
            print(f"WARNING: {line.rstrip('.')}. The user must approve this override before you post.")
        print("OK: review body matches the format.")
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
