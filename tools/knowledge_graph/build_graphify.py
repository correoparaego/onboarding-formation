"""Build a path-safe Graphify graph for code and Markdown corpora."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import networkx as nx
from graphify.export import to_html, to_json, to_obsidian
from graphify.extract import extract


CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx"}
DOC_EXTENSIONS = {".md", ".txt", ".rst"}
BUILTIN_SKIPS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "root"


def git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_ignores(root: Path) -> list[str]:
    path = root / ".graphifyignore"
    if not path.exists():
        return []
    return [
        line.strip().replace("\\", "/")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def ignored(relative: PurePosixPath, patterns: list[str]) -> bool:
    text = relative.as_posix()
    parts = relative.parts
    if any(part in BUILTIN_SKIPS or part.endswith(".egg-info") for part in parts):
        return True
    for pattern in patterns:
        normalized = pattern.rstrip("/")
        if pattern.endswith("/") and (
            text == normalized or text.startswith(normalized + "/") or normalized in parts
        ):
            return True
        if fnmatch.fnmatch(text, pattern) or fnmatch.fnmatch(relative.name, pattern):
            return True
    return False


def collect_files(root: Path, only: Path | None = None) -> tuple[list[Path], list[Path]]:
    if only:
        return ([], [only]) if only.suffix.lower() in DOC_EXTENSIONS else ([only], [])
    patterns = load_ignores(root)
    code: list[Path] = []
    docs: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if ignored(relative, patterns):
            continue
        suffix = path.suffix.lower()
        if suffix in CODE_EXTENSIONS:
            code.append(path)
        elif suffix in DOC_EXTENSIONS:
            docs.append(path)
    return sorted(code), sorted(docs)


def make_node_id(prefix: str, relative: str, local_id: str | None = None) -> str:
    base = slug(str(PurePosixPath(relative).with_suffix("")))
    return f"{prefix}_{base}" + (f"_{slug(local_id)}" if local_id else "")


def extract_code(root: Path, files: list[Path]) -> tuple[list[dict], list[dict]]:
    all_nodes: dict[str, dict] = {}
    raw_edges: list[dict] = []
    aliases: dict[str, list[str]] = {}

    for path in files:
        relative = path.relative_to(root).as_posix()
        result = extract([path])
        local_ids = {node["id"] for node in result.get("nodes", [])}
        id_map: dict[str, str] = {}
        file_stem = slug(path.stem)

        for node in result.get("nodes", []):
            local_id = node["id"]
            is_file = local_id == file_stem and str(node.get("label", "")).endswith(path.suffix)
            namespaced = make_node_id("code", relative, None if is_file else local_id)
            id_map[local_id] = namespaced
            normalized = {
                **node,
                "id": namespaced,
                "source_file": relative,
                "source_location": node.get("source_location") or "L1",
            }
            all_nodes[namespaced] = normalized
            aliases.setdefault(local_id, []).append(namespaced)

        for edge in result.get("edges", []):
            raw_edges.append(
                {
                    **edge,
                    "source": id_map.get(edge["source"], edge["source"]),
                    "target": id_map.get(edge["target"], edge["target"]),
                    "source_file": relative,
                    "_external_target": edge["target"] not in local_ids,
                }
            )

    valid_ids = set(all_nodes)
    edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in raw_edges:
        target = edge["target"]
        if edge.pop("_external_target", False):
            candidates = aliases.get(target, [])
            if len(candidates) == 1:
                target = candidates[0]
            else:
                target = f"external_{slug(target)}"
                all_nodes.setdefault(
                    target,
                    {
                        "id": target,
                        "label": edge["target"],
                        "file_type": "external",
                        "source_file": "",
                        "source_location": "",
                    },
                )
        source = edge["source"]
        if source not in valid_ids:
            continue
        key = (source, target, str(edge.get("relation", "related_to")))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        edges.append({**edge, "source": source, "target": target})
    return list(all_nodes.values()), edges


def heading_type(title: str) -> str:
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
    if "arquitectura" in lower or "modelo" in lower or "flujo" in lower:
        return "architecture"
    if "git" in lower or "pull request" in lower or "pr " in lower:
        return "git-history"
    return "document"


def extract_documents(root: Path, files: list[Path]) -> tuple[list[dict], list[dict]]:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    file_ids: dict[Path, str] = {}

    for path in files:
        relative = path.relative_to(root).as_posix()
        file_id = make_node_id("doc", relative)
        file_ids[path.resolve()] = file_id
        text = path.read_text(encoding="utf-8", errors="replace")
        first_heading = HEADING.search(text)
        nodes[file_id] = {
            "id": file_id,
            "label": first_heading.group(2).strip() if first_heading else path.name,
            "file_type": "document",
            "concept_type": "documentation",
            "source_file": relative,
            "source_location": "L1",
        }
        stack: list[tuple[int, str]] = []
        for match in HEADING.finditer(text):
            level = len(match.group(1))
            title = re.sub(r"[`*_]", "", match.group(2)).strip()
            line = text.count("\n", 0, match.start()) + 1
            heading_id = make_node_id("doc", relative, f"l{line}_{title}")
            nodes[heading_id] = {
                "id": heading_id,
                "label": title,
                "file_type": "document",
                "concept_type": heading_type(title),
                "source_file": relative,
                "source_location": f"L{line}",
            }
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent = stack[-1][1] if stack else file_id
            if heading_id != file_id:
                edges.append(
                    {
                        "source": parent,
                        "target": heading_id,
                        "relation": "contains",
                        "confidence": "EXTRACTED",
                        "confidence_score": 1.0,
                        "source_file": relative,
                        "source_location": f"L{line}",
                        "weight": 1.0,
                    }
                )
            stack.append((level, heading_id))

    for path in files:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        source = file_ids[path.resolve()]
        for raw_target in MARKDOWN_LINK.findall(text):
            target_text = raw_target.split("#", 1)[0]
            if not target_text.lower().endswith((".md", ".txt", ".rst")):
                continue
            target_path = (path.parent / target_text).resolve()
            target = file_ids.get(target_path)
            if target:
                edges.append(
                    {
                        "source": source,
                        "target": target,
                        "relation": "references",
                        "confidence": "EXTRACTED",
                        "confidence_score": 1.0,
                        "source_file": relative,
                        "source_location": "L1",
                        "weight": 1.0,
                    }
                )
    return list(nodes.values()), edges


def deduplicate(nodes: list[dict], edges: list[dict]) -> tuple[list[dict], list[dict]]:
    node_map = {node["id"]: node for node in nodes}
    valid = set(node_map)
    clean_edges: dict[tuple[str, str, str], dict] = {}
    for edge in edges:
        if edge["source"] not in valid or edge["target"] not in valid:
            continue
        key = (edge["source"], edge["target"], str(edge.get("relation", "related_to")))
        clean_edges[key] = edge
    return list(node_map.values()), list(clean_edges.values())


def cluster_graph(graph: nx.Graph) -> dict[int, list[str]]:
    if graph.number_of_nodes() == 0:
        return {}
    connected = graph.subgraph([node for node in graph if graph.degree(node) > 0])
    groups: list[set[str]] = []
    if connected.number_of_nodes():
        groups = list(nx.community.louvain_communities(connected, seed=42))
    groups.extend([{node} for node in graph if graph.degree(node) == 0])
    groups.sort(key=lambda group: (-len(group), sorted(group)[0]))
    return {index: sorted(group) for index, group in enumerate(groups)}


def community_labels(graph: nx.Graph, communities: dict[int, list[str]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for community, members in communities.items():
        concept_types = Counter(
            str(graph.nodes[node].get("concept_type") or graph.nodes[node].get("file_type") or "concept")
            for node in members
        )
        source_roots = Counter(
            str(graph.nodes[node].get("source_file", "")).replace("\\", "/").split("/")[0]
            for node in members
            if graph.nodes[node].get("source_file")
        )
        dominant_type = concept_types.most_common(1)[0][0].replace("-", " ").title()
        dominant_root = source_roots.most_common(1)[0][0].replace("_", " ").title() if source_roots else "Core"
        labels[community] = f"{dominant_root} · {dominant_type}"
    return labels


def graph_report(
    root: Path,
    output: Path,
    graph: nx.Graph,
    communities: dict[int, list[str]],
    labels: dict[int, str],
    files: list[Path],
    head: str,
) -> str:
    degrees = sorted(graph.degree(), key=lambda item: (-item[1], item[0]))
    lines = [
        f"# Graph Report - {root.name}",
        "",
        "## Generation",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Git commit: `{head}`",
        "- Extractor: `graphifyy 0.1.14` with path-safe node namespaces",
        "- Clustering: deterministic NetworkX Louvain (`seed=42`)",
        f"- Output: `{output.as_posix()}`",
        "",
        "## Corpus",
        f"- {len(files)} source files",
        f"- {graph.number_of_nodes()} nodes",
        f"- {graph.number_of_edges()} edges",
        f"- {len(communities)} communities",
        "",
        "## God Nodes",
    ]
    for node, degree in degrees[:20]:
        data = graph.nodes[node]
        lines.append(
            f"- `{data.get('label', node)}`: {degree} edges · `{data.get('source_file', '')}`"
        )
    lines.extend(["", "## Communities"])
    for community, members in communities.items():
        examples = ", ".join(str(graph.nodes[node].get("label", node)) for node in members[:8])
        lines.extend(
            [
                "",
                f"### {community}. {labels[community]}",
                f"- Nodes: {len(members)}",
                f"- Examples: {examples}",
            ]
        )
    return "\n".join(lines) + "\n"


def manifest(root: Path, files: list[Path]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in files:
        content = path.read_bytes()
        result[path.relative_to(root).as_posix()] = {
            "mtime": path.stat().st_mtime,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--only", type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    only = args.only.resolve() if args.only else None
    if args.clean and output.exists():
        for child in output.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output.mkdir(parents=True, exist_ok=True)

    code_files, doc_files = collect_files(root, only)
    code_nodes, code_edges = extract_code(root, code_files)
    doc_nodes, doc_edges = extract_documents(root, doc_files)
    nodes, edges = deduplicate(code_nodes + doc_nodes, code_edges + doc_edges)

    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node["id"], **{key: value for key, value in node.items() if key != "id"})
    for edge in edges:
        graph.add_edge(
            edge["source"],
            edge["target"],
            **{key: value for key, value in edge.items() if key not in {"source", "target"}},
        )
    communities = cluster_graph(graph)
    labels = community_labels(graph, communities)
    source_files = code_files + doc_files
    head = git_head(root)

    to_json(graph, communities, str(output / "graph.json"))
    to_html(graph, communities, str(output / "graph.html"), community_labels=labels)
    to_obsidian(
        graph,
        communities,
        str(output / "obsidian"),
        community_labels=labels,
        cohesion={community: 0.0 for community in communities},
    )
    (output / "GRAPH_REPORT.md").write_text(
        graph_report(root, output, graph, communities, labels, source_files, head),
        encoding="utf-8",
    )
    (output / "manifest.json").write_text(
        json.dumps(manifest(root, source_files), indent=2), encoding="utf-8"
    )
    (output / "generation.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "git_commit": head,
                "root": str(root),
                "only": str(only) if only else None,
                "extractor": "graphifyy 0.1.14",
                "clustering": "networkx-louvain-seed-42",
                "files": len(source_files),
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "communities": len(communities),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Graphify: {len(source_files)} files, {graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges, {len(communities)} communities"
    )
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
