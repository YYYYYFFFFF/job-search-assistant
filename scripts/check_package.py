#!/usr/bin/env python3
"""Check package paths, Markdown navigation, Skill metadata and obvious data leaks."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"AGENTS.md", "README.md", "LICENSE", ".gitignore", "plugin.json", "skills", "scripts", "templates", "examples", "docs", "tests", ".github"}


def anchor(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def check(root=ROOT):
    problems = []
    files = [p for p in root.rglob("*") if p.is_file() and not any(part in {".git", "__pycache__", ".career"} for part in p.relative_to(root).parts)]
    for file in files:
        relative = file.relative_to(root)
        if relative.parts[0] not in ALLOWED:
            problems.append("Unexpected package path: " + str(relative))
        if file.is_symlink():
            problems.append("Symlink in distributable: " + str(relative))
        text = file.read_text(encoding="utf-8")
        if file.suffix == ".py":
            ast.parse(text, filename=str(relative))
        if file.suffix == ".json":
            json.loads(text)
        home_prefixes = ["/" + "Users/", "/" + "home/"]
        if any(prefix in text for prefix in home_prefixes):
            problems.append("Machine-specific home path: " + str(relative))
        if re.search(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}|BEGIN " + "PRIVATE KEY)", text):
            problems.append("Possible secret: " + str(relative))
        for email in re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text):
            domain = email.rsplit("@", 1)[1]
            if domain not in {"example.test", "example.com", "users.noreply.github.com"} and not domain.endswith(".example.test"):
                problems.append("Non-example email in " + str(relative))
        if file.suffix != ".md":
            continue
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if urlsplit(link).scheme:
                continue
            path, _, fragment = unquote(link).partition("#")
            target = (file.parent / path).resolve() if path else file
            if root.resolve() != target and root.resolve() not in target.parents:
                problems.append("Link escapes package: " + str(relative) + " -> " + link)
            elif not target.exists():
                problems.append("Broken link: " + str(relative) + " -> " + link)
            elif fragment and target.is_file():
                anchors = {anchor(h) for h in re.findall(r"^#+\s+(.+)$", target.read_text(), re.M)}
                if fragment not in anchors:
                    problems.append("Missing anchor: " + str(relative) + " -> " + link)
    expected = {"job-search", "job-application", "career-maintenance", "question-bank"}
    found = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if found != expected:
        problems.append("Expected exactly four workflow Skills")
    for name in found:
        text = (root / "skills" / name / "SKILL.md").read_text()
        if not text.startswith("---\nname: " + name + "\ndescription: "):
            problems.append("Invalid Skill metadata: " + name)
    manifest = json.loads((root / "plugin.json").read_text())
    if manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json" or manifest.get("name") != "job-search-assistant":
        problems.append("Invalid portable manifest")
    return {"files_checked": len(files), "skills": len(found), "problems": problems}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2))
    sys.exit(bool(result["problems"]))
