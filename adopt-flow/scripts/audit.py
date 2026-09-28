#!/usr/bin/env python3
"""Audit which tech-lead flow documents a repository already has.

  audit.py [REPO]        print the audit table and the skills to run, in order
  audit.py --self-test

Each document is found in its folder form or its older single-file form. A
document that the change lane creates on first use (business docs, task
breakdown) is reported but never scheduled. Standard library only.
"""
import os
import sys
import tempfile

# (phase, document, skill, paths that count as present, first path is the current form)
DOCS = [
    ("2", "Technical specs", "technical-spec", ["docs/technical-specs/_index.md"]),
    ("2", "API specs", "api-spec", ["docs/api-specs/_index.md"]),
    ("3", "Deployment plan", "deployment-plan", ["docs/deployment-plan/_index.md", "docs/DEPLOYMENT_PLAN.md", "DEPLOYMENT_PLAN.md"]),
    ("4", "Test harness and tooling", "tech-lead-setups", []),
    ("4", "Coding standard", "coding-standard", ["docs/coding-standard/_index.md", "docs/CODING_STANDARD.md", "CODING_STANDARD.md", "CODING_STANDARDS.md", "docs/CODING_STANDARDS.md"]),
    ("4", "Review checklist", "coding-standard", ["docs/code-review-checklist/_index.md", "docs/CODE_REVIEW_CHECKLIST.md", "CODE_REVIEW_CHECKLIST.md"]),
    ("4", "CI workflows", "github-project-init", [".github/workflows"]),
    ("5", "Glossary", "project-docs", ["docs/GLOSSARY.md", "GLOSSARY.md"]),
    ("5", "Development guide", "project-docs", ["docs/development-guide/_index.md", "docs/DEVELOPMENT_SCENARIO_GUIDE.md", "DEVELOPMENT_SCENARIO_GUIDE.md"]),
    ("5", "Onboarding guide", "project-docs", ["docs/onboarding/_index.md", "docs/ONBOARDING_GUIDE.md", "ONBOARDING_GUIDE.md"]),
    ("5", "Agent manual", "init-claude", ["CLAUDE.md", "AGENTS.md"]),
    ("7", "Business docs", "to-prd", ["docs/business"]),
    ("7", "Task breakdown", "to-issues", ["docs/task-breakdown/_index.md", "docs/TASK_BREAKDOWN.md", "TASK_BREAKDOWN.md"]),
    ("Later", "Troubleshooting guide", "troubleshooting", ["docs/troubleshooting/_index.md", "docs/TROUBLESHOOTING.md", "TROUBLESHOOTING.md"]),
]
ON_FIRST_USE = {"to-prd", "to-issues"}
LATER = {"troubleshooting"}
MANIFESTS = ["package.json", "go.mod", "Cargo.toml", "pyproject.toml", "setup.py", "pom.xml", "build.gradle",
             "build.gradle.kts", "composer.json", "Gemfile", "mix.exs", "deno.json", "pubspec.yaml"]


def has_code(root):
    if any(os.path.exists(os.path.join(root, m)) for m in MANIFESTS):
        return True
    return any(os.path.isdir(os.path.join(root, d)) for d in ("src", "app", "apps", "cmd", "lib", "packages"))


def audit(root):
    rows, run = [], []
    for phase, doc, skill, paths in DOCS:
        if not paths:
            status, found = "check", "the skill audits the tooling itself"
        else:
            hit = next((p for p in paths if os.path.exists(os.path.join(root, p))), None)
            if hit == ".github/workflows" and not any(
                    f.endswith((".yml", ".yaml")) for f in os.listdir(os.path.join(root, hit))):
                hit = None  # an empty workflows folder is not CI
            folder = os.path.join(root, os.path.dirname(paths[0])) if paths[0].endswith("/_index.md") else None
            if hit is None and folder and os.path.isdir(folder) and any(f.endswith(".md") for f in os.listdir(folder)):
                status, found = "present, older layout (no _index.md)", os.path.dirname(paths[0]) + "/"
            elif hit is None:
                status, found = "missing", "-"
            elif hit == paths[0] or skill == "init-claude":
                status, found = "present", hit
            else:
                status, found = "present, older single file", hit
        if skill in ON_FIRST_USE and status == "missing":
            status = "created on first new feature"
        if skill in LATER and status == "missing":
            status = "later, once incidents exist"
        rows.append((phase, doc, found, skill, status))
        if status in ("missing", "check") and skill not in run:
            run.append(skill)
    return rows, run


def render(root):
    code = has_code(root)
    rows, run = audit(root)
    out = [f"Repository: {os.path.abspath(root)}",
           f"Running project: {'yes' if code else 'no, start with product-discovery instead'}", "",
           "| Phase | Document | Found at | Skill | Status |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {p} | {d} | `{f}` | `{s}` | {st} |" if f != "-" and not f.startswith("the skill")
            else f"| {p} | {d} | {f} | `{s}` | {st} |" for p, d, f, s, st in rows]
    out += ["", "Run in this order, each in its adopt mode:"]
    out += [f"{i}. {s}" for i, s in enumerate(run, 1)] if code else ["(none: not a running project)"]
    return "\n".join(out) + "\n"


def self_test():
    with tempfile.TemporaryDirectory() as root:
        assert not has_code(root)
        open(os.path.join(root, "package.json"), "w").close()
        os.makedirs(os.path.join(root, "docs/technical-specs"))
        open(os.path.join(root, "docs/technical-specs/_index.md"), "w").close()
        open(os.path.join(root, "CODE_REVIEW_CHECKLIST.md"), "w").close()
        open(os.path.join(root, "CLAUDE.md"), "w").close()
        assert has_code(root)
        rows, run = audit(root)
        status = {d: st for _, d, _, _, st in rows}
        assert status["Technical specs"] == "present", status
        os.makedirs(os.path.join(root, "docs/api-specs"))
        open(os.path.join(root, "docs/api-specs/0.index.md"), "w").close()
        assert {d: st for _, d, _, _, st in audit(root)[0]}["API specs"] == "present, older layout (no _index.md)"
        rows, run = audit(root)
        status = {d: st for _, d, _, _, st in rows}
        assert status["Review checklist"] == "present, older single file", status
        assert status["Coding standard"] == "missing", status
        assert status["Agent manual"] == "present", status
        assert status["Business docs"] == "created on first new feature", status
        assert status["Troubleshooting guide"] == "later, once incidents exist", status
        assert "technical-spec" not in run and "to-prd" not in run and "troubleshooting" not in run, run
        assert run[:2] == ["deployment-plan", "tech-lead-setups"], run
        assert "coding-standard" in run and "init-claude" not in run, run
        assert "Run in this order" in render(root)
        os.makedirs(os.path.join(root, ".github/workflows"))
        open(os.path.join(root, ".github/PULL_REQUEST_TEMPLATE.md"), "w").close()
        assert "github-project-init" in audit(root)[1], "a PR template without workflows must not count as CI"
        open(os.path.join(root, ".github/workflows/ci.yml"), "w").close()
        assert "github-project-init" not in audit(root)[1], "a workflow file counts as CI"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    root = argv[0] if argv else "."
    if not os.path.isdir(root):
        sys.exit(f"not a directory: {root}")
    sys.stdout.write(render(root))


if __name__ == "__main__":
    main(sys.argv[1:])
