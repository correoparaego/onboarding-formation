"""Derive a navigable OKF bundle from headings in TECHNICAL_DOCUMENTATION.md."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path


HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def slug(value: str) -> str:
    value = re.sub(r"[`*_]", "", value).lower()
    value = re.sub(r"[^a-z0-9áéíóúüñ]+", "-", value)
    return value.strip("-") or "concept"


def concept_type(title: str) -> str:
    lower = title.lower()
    if re.match(r"f-?\d+", lower) or "feature" in lower:
        return "feature"
    if lower.startswith("adr-") or "decisión" in lower:
        return "decision"
    if "riesgo" in lower or "deuda" in lower:
        return "risk"
    if "seguridad" in lower or "rgpd" in lower:
        return "security"
    if "render" in lower or "despliegue" in lower:
        return "deployment"
    if "test" in lower or "calidad" in lower:
        return "quality"
    if "git" in lower or "pull request" in lower or "ramas" in lower:
        return "git-history"
    if "arquitectura" in lower or "modelo" in lower or "flujo" in lower:
        return "architecture"
    return "documentation"


def description(lines: list[str], start: int) -> str:
    for raw in lines[start:]:
        line = raw.strip()
        if not line or line.startswith(("#", "|", "```", "-", ">")):
            continue
        clean = re.sub(r"[`*_]", "", line)
        return clean[:280]
    return "Sección estructurada de la documentación técnica maestra."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    concepts = output / "concepts"
    if args.clean and output.exists():
        for child in output.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    concepts.mkdir(parents=True, exist_ok=True)

    lines = source.read_text(encoding="utf-8").splitlines()
    headings: list[dict[str, object]] = []
    stack: list[dict[str, object]] = []
    used: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = re.sub(r"[`*_]", "", match.group(2)).strip()
        base = slug(title)
        used[base] = used.get(base, 0) + 1
        concept_slug = base if used[base] == 1 else f"{base}-{used[base]}"
        while stack and int(stack[-1]["level"]) >= level:
            stack.pop()
        item = {
            "level": level,
            "title": title,
            "slug": concept_slug,
            "line": index + 1,
            "description": description(lines, index + 1),
            "type": "project" if level == 1 else concept_type(title),
            "parent": stack[-1]["slug"] if stack else None,
        }
        headings.append(item)
        stack.append(item)

    roots = {
        str(item["type"]): str(item["slug"])
        for item in headings
        if int(item["level"]) == 2
    }
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source.parent, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        head = "unknown"

    for item in headings:
        relations: list[str] = []
        if item["parent"]:
            relations.append(f"- Parent: [{item['parent']}](./{item['parent']}.md)")
        root = roots.get(str(item["type"]))
        if root and root != item["slug"] and root != item["parent"]:
            relations.append(f"- Area: [{root}](./{root}.md)")
        content = "\n".join(
            [
                "---",
                f"type: {item['type']}",
                f'title: "{str(item["title"]).replace(chr(34), chr(39))}"',
                f'description: "{str(item["description"]).replace(chr(34), chr(39))}"',
                f"resource: TECHNICAL_DOCUMENTATION.md#L{item['line']}",
                f"generated: {date.today().isoformat()}",
                "status: active",
                "trust_tier: human-reviewed",
                f'verified: ["{head}"]',
                "---",
                "",
                f"# {item['title']}",
                "",
                str(item["description"]),
                "",
                "## Fuente",
                "",
                f"`TECHNICAL_DOCUMENTATION.md:{item['line']}`",
                "",
                "## Relaciones",
                "",
                *(relations or ["- Concepto raíz del documento."]),
                "",
            ]
        )
        (concepts / f"{item['slug']}.md").write_text(content, encoding="utf-8")

    index_lines = [
        "---",
        "type: index",
        "description: Technical documentation knowledge graph",
        f"generated: {date.today().isoformat()}",
        "status: active",
        "---",
        "",
        "# Technical Documentation OKF",
        "",
    ]
    for item in headings:
        indent = "  " * max(0, int(item["level"]) - 1)
        index_lines.append(f"{indent}- [{item['title']}](concepts/{item['slug']}.md)")
    (output / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Technical OKF: {len(headings)} concepts")
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
