"""Build a standalone interactive Cytoscape viewer from an OKF Markdown bundle."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import yaml


FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]*)?\)")
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)

TYPE_COLORS = {
    "project": "#183153",
    "feature": "#0b6e4f",
    "spec": "#2563eb",
    "backend-module": "#7c3aed",
    "frontend-module": "#db2777",
    "architecture": "#0369a1",
    "decision": "#b45309",
    "deployment": "#047857",
    "security": "#b91c1c",
    "quality": "#4f46e5",
    "git-history": "#475569",
    "risk": "#dc2626",
    "documentation": "#0891b2",
}


def parse_concept(path: Path, root: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    metadata = yaml.safe_load(match.group(1)) if match else {}
    metadata = metadata if isinstance(metadata, dict) else {}
    body = text[match.end() :] if match else text
    relative = path.relative_to(root).as_posix()
    concept_id = str(PurePosixPath(relative).with_suffix(""))
    title_match = HEADING.search(body)
    title = str(metadata.get("title") or (title_match.group(1).strip() if title_match else concept_id))
    concept_type = str(metadata.get("type") or path.parent.name or "concept")
    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [item.strip() for item in tags.split(",") if item.strip()]
    return {
        "id": concept_id,
        "label": title,
        "type": concept_type,
        "description": str(metadata.get("description") or ""),
        "resource": str(metadata.get("resource") or relative),
        "tags": tags if isinstance(tags, list) else [],
        "status": str(metadata.get("status") or "active"),
        "generated": str(metadata.get("generated") or ""),
        "verified": metadata.get("verified", []),
        "trust_tier": str(metadata.get("trust_tier") or "unverified"),
        "source": relative,
        "body": body.strip(),
        "color": TYPE_COLORS.get(concept_type, "#64748b"),
    }


def resolve_link(source: Path, target: str, root: Path) -> str | None:
    clean = target.split("#", 1)[0]
    resolved = (source.parent / clean).resolve()
    try:
        return resolved.relative_to(root.resolve()).with_suffix("").as_posix()
    except ValueError:
        return None


def build_bundle(root: Path) -> tuple[dict[str, object], list[str]]:
    files = sorted(
        path
        for path in root.rglob("*.md")
        if path.name.lower() not in {"index.md", "log.md", "readme.md", "agents.md"}
    )
    concepts = [parse_concept(path, root) for path in files]
    ids = {str(concept["id"]) for concept in concepts}
    edges: list[dict[str, str]] = []
    broken: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path, concept in zip(files, concepts, strict=True):
        text = path.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            target_id = resolve_link(path, target, root)
            if not target_id or target_id not in ids:
                broken.append(f"{concept['source']} -> {target}")
                continue
            key = (str(concept["id"]), target_id)
            if key not in seen:
                seen.add(key)
                edges.append({"source": key[0], "target": key[1], "relation": "references"})

    types = sorted({str(concept["type"]) for concept in concepts})
    payload = {
        "name": root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nodes": concepts,
        "edges": edges,
        "types": types,
        "stats": {"nodes": len(concepts), "edges": len(edges), "types": len(types)},
    }
    return payload, broken


def render_html(bundle: dict[str, object]) -> str:
    payload = json.dumps(bundle, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(str(bundle["name"]))
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - OKF Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
*{{box-sizing:border-box}}body{{margin:0;font:14px Inter,Segoe UI,sans-serif;color:#172033;background:#f4f7fb;height:100vh;overflow:hidden}}
header{{height:64px;display:flex;align-items:center;gap:12px;padding:10px 16px;background:#10243e;color:white}}
header strong{{font-size:17px}}header small{{color:#b9c8dc}}input,select,button{{height:36px;border:1px solid #ccd5e1;border-radius:7px;padding:0 10px;background:white}}
input{{margin-left:auto;width:260px}}button{{cursor:pointer}}main{{display:grid;grid-template-columns:minmax(0,3fr) minmax(360px,2fr);height:calc(100vh - 64px)}}
#graph{{background:white;border-right:1px solid #dbe3ed}}#detail{{padding:20px;overflow:auto}}#detail h1{{font-size:22px;margin:8px 0}}
.chip{{display:inline-block;padding:3px 8px;margin:2px;border-radius:999px;background:#e6edf6;color:#31445f;font-size:11px}}.meta{{color:#607087;font-size:12px}}
.empty{{margin:40px auto;max-width:360px;text-align:center;color:#728197}}pre{{overflow:auto;background:#132238;color:#e4edf8;padding:12px;border-radius:8px}}
table{{border-collapse:collapse}}th,td{{border:1px solid #d5deea;padding:5px}}@media(max-width:800px){{main{{grid-template-columns:1fr}}#graph{{height:55vh}}#detail{{height:45vh}}header small{{display:none}}input{{width:150px}}}}
</style>
</head>
<body>
<header><strong>{title}</strong><small id="stats"></small><input id="search" placeholder="Buscar concepto, tipo o tag"><select id="type"><option value="">Todos los tipos</option></select><select id="layout"><option value="cose">Fuerza</option><option value="breadthfirst">Jerarquía</option><option value="concentric">Concéntrico</option><option value="circle">Círculo</option><option value="grid">Cuadrícula</option></select><button id="reset">Restablecer</button></header>
<main><section id="graph"></section><aside id="detail"><div class="empty">Selecciona un nodo para ver su contenido, metadatos y relaciones.</div></aside></main>
<script>
const BUNDLE={payload};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
document.querySelector('#stats').textContent=`${{BUNDLE.stats.nodes}} nodos · ${{BUNDLE.stats.edges}} relaciones · ${{BUNDLE.stats.types}} tipos`;
const byId=Object.fromEntries(BUNDLE.nodes.map(n=>[n.id,n]));
const elements=[...BUNDLE.nodes.map(n=>({{data:{{...n,id:n.id}}}})),...BUNDLE.edges.map((e,i)=>({{data:{{id:`e${{i}}`,...e}}}}))];
const cy=cytoscape({{container:document.querySelector('#graph'),elements,style:[{{selector:'node',style:{{'background-color':'data(color)','label':'data(label)','font-size':10,'text-wrap':'wrap','text-max-width':120,'text-valign':'bottom','text-margin-y':6,'width':30,'height':30,'border-width':1,'border-color':'#10243e'}}}},{{selector:'edge',style:{{width:1.2,'line-color':'#a8b6c8','target-arrow-color':'#a8b6c8','target-arrow-shape':'triangle','curve-style':'bezier'}}}},{{selector:':selected',style:{{'border-width':4,'border-color':'#f59e0b','line-color':'#f59e0b','target-arrow-color':'#f59e0b'}}}},{{selector:'.dim',style:{{opacity:.12}}}}],layout:{{name:'cose',animate:false,nodeRepulsion:9000,idealEdgeLength:110}}}});
const type=document.querySelector('#type');BUNDLE.types.forEach(t=>type.add(new Option(t,t)));
function applyLayout(){{cy.layout({{name:document.querySelector('#layout').value,animate:true,padding:28}}).run()}}
function filter(){{const q=document.querySelector('#search').value.toLowerCase();const t=type.value;cy.nodes().forEach(el=>{{const n=el.data();const hay=[n.label,n.type,n.description,...(n.tags||[])].join(' ').toLowerCase();el.toggleClass('dim',!!((q&&!hay.includes(q))||(t&&n.type!==t)))}})}}
function show(n){{const incoming=BUNDLE.edges.filter(e=>e.target===n.id).map(e=>byId[e.source]?.label).filter(Boolean);const outgoing=BUNDLE.edges.filter(e=>e.source===n.id).map(e=>byId[e.target]?.label).filter(Boolean);document.querySelector('#detail').innerHTML=`<div><span class="chip">${{esc(n.type)}}</span><span class="chip">${{esc(n.status)}}</span><span class="chip">${{esc(n.trust_tier)}}</span></div><h1>${{esc(n.label)}}</h1><p>${{esc(n.description)}}</p><div class="meta"><b>ID:</b> ${{esc(n.id)}}<br><b>Recurso:</b> ${{esc(n.resource)}}<br><b>Fuente:</b> ${{esc(n.source)}}<br><b>Tags:</b> ${{(n.tags||[]).map(x=>`<span class="chip">${{esc(x)}}</span>`).join(' ')}}</div><hr><div>${{marked.parse(n.body||'')}}</div><hr><h3>Referencias salientes</h3><p>${{outgoing.map(esc).join(' · ')||'Ninguna'}}</p><h3>Referenciado por</h3><p>${{incoming.map(esc).join(' · ')||'Ninguno'}}</p>`}}
cy.on('tap','node',e=>show(e.target.data()));document.querySelector('#search').addEventListener('input',filter);type.addEventListener('change',filter);document.querySelector('#layout').addEventListener('change',applyLayout);document.querySelector('#reset').addEventListener('click',()=>{{document.querySelector('#search').value='';type.value='';filter();applyLayout();cy.fit(undefined,30)}});
</script></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = args.bundle.resolve()
    output = (args.output or root / "viz.html").resolve()
    bundle, broken = build_bundle(root)
    if broken:
        print("Broken links:")
        for item in broken:
            print(f"  {item}")
        if args.strict:
            return 1
    rendered = render_html(bundle)
    output.write_text(rendered, encoding="utf-8")
    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    print(f"OKF viewer: {bundle['stats']['nodes']} nodes, {bundle['stats']['edges']} edges")
    print(f"Output: {output}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
