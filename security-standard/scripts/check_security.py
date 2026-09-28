#!/usr/bin/env python3
"""Check a security standard folder: every row has a status and proof you can open.

  check_security.py DIR [--spec PATH] [--root PATH]
  check_security.py --self-test

DIR is docs/security-standards/. --spec is the technical specs (a folder or a
file); with it, every SEC-NN ID must exist there. --root is the repo root that
cited paths are relative to (default: the current directory). See
../references/layout.md for the tables. Standard library only.
"""
import glob
import os
import re
import sys

RISK_FILES = ("01-owasp-api-top-10.md", "02-owasp-web-top-10.md", "03-asvs.md", "04-before-exposure.md")
FILES = ("_index.md", *RISK_FILES, "05-not-done.md", "06-claims.md")
STATUSES = ("Done", "Partial", "Not done", "Not applicable")
# The same card-or-issue shape as pr_hygiene.py's WORK_REF, minus SEC IDs.
WORK_REF = re.compile(r"#\d+|\b(?!AC-|US-|SEC-)[A-Z][A-Z0-9]*-(?:S\d+-)?\d+\b")
SEC_ID = re.compile(r"\bSEC-\d+\b")
NA_RE = re.compile(r"^Not applicable: \S", re.M)


def table(text, head_re):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(head_re, l.strip())), None)
    if start is None:
        return None
    out = []
    for n, line in enumerate(lines[start + 2:], start + 3):
        if not line.startswith("|"):
            break
        out.append((n, [c.strip() for c in line.strip().strip("|").split("|")]))
    return out


def paths(where):
    """Backticked tokens that look like repo paths, with any :line or #anchor cut off."""
    out = []
    for tok in re.findall(r"`([^`\s]+)`", where):
        tok = re.sub(r"(:L?\d+(-\d+)?|#.*)$", "", tok)
        if "/" in tok or re.search(r"\.[a-z]{1,5}$", tok) or tok in ("Dockerfile", "Makefile"):
            out.append(tok)
    return out


def check_risk_file(name, text, root, sec_ids):
    errs = []
    rows = table(text, r"^\| # \| Risk \| Control \| Status \| Where \|$")
    if rows is None:
        if not NA_RE.search(text):
            errs.append(f"{name}: no '| # | Risk | Control | Status | Where |' table and no 'Not applicable: <reason>' line")
        return errs
    seen = set()
    for n, cells in rows:
        at = f"{name}:{n}"
        if len(cells) != 5:
            errs.append(f"{at}: {len(cells)} cells, need 5")
            continue
        rid, _, control, status, where = cells
        if rid in seen:
            errs.append(f"{at}: row {rid} appears twice")
        seen.add(rid)
        if status not in STATUSES:
            errs.append(f"{at}: status {status!r} is not one of: {', '.join(STATUSES)}")
            continue
        if sec_ids is not None:
            for sec in SEC_ID.findall(control):
                if sec not in sec_ids:
                    errs.append(f"{at}: {sec} is not in the technical spec")
        cited = paths(where)
        missing = [p for p in cited if not os.path.exists(os.path.join(root, p))]
        for p in missing:
            errs.append(f"{at}: path `{p}` does not exist")
        if status == "Done" and len(cited) == len(missing):
            errs.append(f"{at}: a Done row cites at least one file that exists, in backticks")
        if status in ("Partial", "Not done") and not WORK_REF.search(where):
            errs.append(f"{at}: a {status} row names the card or issue that closes it")
        if status == "Not applicable" and len(where.split()) < 4:
            errs.append(f"{at}: a Not applicable row gives its reason in one sentence")
    return errs


def check(folder, root=".", spec=None):
    errs, texts = [], {}
    for name in FILES:
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            errs.append(f"missing {name}; a section that does not apply keeps its file with 'Not applicable: <reason>'")
            continue
        with open(p, encoding="utf-8") as f:
            texts[name] = f.read()
        for n, line in enumerate(texts[name].splitlines(), 1):
            bad = sorted({c for c in line if ord(c) > 127})
            if bad:
                errs.append(f"{name}:{n}: non-ASCII {' '.join(map(repr, bad))}; ASCII only")
    sec_ids = None
    if spec:
        files = sorted(glob.glob(os.path.join(spec, "*.md"))) if os.path.isdir(spec) else [spec]
        sec_ids = set()
        for f in files:
            with open(f, encoding="utf-8") as fh:
                sec_ids |= set(SEC_ID.findall(fh.read()))
    for name in RISK_FILES:
        if name in texts:
            errs += check_risk_file(name, texts[name], root, sec_ids)
    if "05-not-done.md" in texts and not NA_RE.search(texts["05-not-done.md"]):
        rows = table(texts["05-not-done.md"], r"^\| # \| Not done \| Why \|$")
        if rows is None:
            errs.append("05-not-done.md: no '| # | Not done | Why |' table and no 'Not applicable: <reason>' line")
        for n, cells in rows or []:
            if len(cells) != 3 or len(cells[2].split()) < 4:
                errs.append(f"05-not-done.md:{n}: each row gives its reason in one sentence")
    if "06-claims.md" in texts:
        for head in ("## Can claim", "## Cannot claim"):
            if head not in texts["06-claims.md"].splitlines():
                errs.append(f"06-claims.md: missing the section {head!r}")
    return errs


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "src/http"))
        open(os.path.join(root, "src/http/auth.ts"), "w").close()
        spec = os.path.join(root, "07-security.md")
        with open(spec, "w") as f:
            f.write("SEC-01 and SEC-03\n")
        folder = os.path.join(root, "docs/security-standards")
        os.makedirs(folder)

        def write(files):
            for name, text in files.items():
                with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                    f.write(text)

        head = "| # | Risk | Control | Status | Where |\n| --- | --- | --- | --- | --- |\n"
        good = {
            "_index.md": "# Security standards\n",
            "01-owasp-api-top-10.md": "# API\n\n" + head
            + "| API1 | Broken object level authorization | SEC-03 | Done | `src/http/auth.ts:12` checks scope. |\n"
            + "| API4 | Unrestricted resource consumption | SEC-01 | Partial | `src/http/auth.ts` caps bodies. Uploads are BE-S4-02. |\n"
            + "| API6 | Sensitive business flows | - | Not done | #88 |\n"
            + "| API9 | Improper inventory management | - | Not applicable | The API has one version and one prefix. |\n",
            "02-owasp-web-top-10.md": "# Web\n\nNot applicable: the product has no browser client.\n",
            "03-asvs.md": "# ASVS\n\nNot applicable: the project follows the two Top 10 lists only.\n",
            "04-before-exposure.md": "# Before exposure\n\n" + head
            + "| 1 | TLS in front | - | Not done | DEPLOY-3 |\n",
            "05-not-done.md": "# Not done\n\n| # | Not done | Why |\n| --- | --- | --- |\n"
            + "| 1 | No MFA of its own | The proxy carries MFA for public instances. |\n",
            "06-claims.md": "# Claims\n\n## Can claim\n\n- x\n\n## Cannot claim\n\n- y\n",
        }
        write(good)
        assert check(folder, root, spec) == [], check(folder, root, spec)
        api = good["01-owasp-api-top-10.md"]
        bad = {
            "made-up path": api.replace("`src/http/auth.ts:12`", "`src/http/guard.ts`"),
            "Done without a path": api.replace("`src/http/auth.ts:12` checks scope.", "The guard checks scope."),
            "Not done without a card": api.replace("| Not done | #88 |", "| Not done | Later. |"),
            "SEC ID as the card": api.replace("| Not done | #88 |", "| Not done | SEC-01 |"),
            "Partial without a card": api.replace(" Uploads are BE-S4-02.", ""),
            "bare Not applicable": api.replace("The API has one version and one prefix.", "n/a"),
            "unknown status": api.replace("| Not done |", "| Planned |"),
            "unknown SEC ID": api.replace("SEC-03", "SEC-09"),
            "duplicate row": api.replace("| API4 |", "| API1 |"),
            "non-ASCII": api.replace("checks scope.", "checks scope \u2014 always."),
            "no table": "# API\n\nWe are secure.\n",
        }
        for name, text in bad.items():
            write({"01-owasp-api-top-10.md": text})
            assert check(folder, root, spec), f"self-test: '{name}' was not caught"
        write({"01-owasp-api-top-10.md": api})
        os.remove(os.path.join(folder, "06-claims.md"))
        assert check(folder, root, spec), "self-test: a missing file was not caught"
        write({"06-claims.md": "# Claims\n\n## Can claim\n"})
        assert check(folder, root, spec), "self-test: a missing claims section was not caught"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="check_security.py")
    ap.add_argument("dir")
    ap.add_argument("--spec", help="the technical specs folder or its security file")
    ap.add_argument("--root", default=".", help="the repo root that cited paths are relative to")
    a = ap.parse_args(argv)
    errs = check(a.dir, a.root, a.spec)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    print("security standard OK")


if __name__ == "__main__":
    main(sys.argv[1:])
