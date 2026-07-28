# Knowledge graph generation

The repository versions four canonical graph outputs:

| Corpus | Graphify | OKF |
|---|---|---|
| Full repository | `graphify-out/` | `okf-bundle/viz.html` |
| Technical document | `graphify-technical-documentation/` | `okf-technical-documentation/viz.html` |

## Toolchain

Install the pinned tools in an isolated environment:

```powershell
py -3.13 -m venv .graph-tools
.\.graph-tools\Scripts\python -m pip install -r tools\knowledge_graph\requirements.txt
```

On Python 3.14, install Graphify without its incompatible legacy clustering
dependency. This project uses NetworkX Louvain clustering instead:

```powershell
.\.graph-tools\Scripts\python -m pip install graphifyy==0.1.14 --no-deps
```

Graphify generation follows the extraction pipeline published by `graphifyy`:
deterministic AST extraction for code, semantic extraction for documents, graph
merge, community clustering, labeling, and HTML/JSON/report export. Python 3.14
builds use deterministic NetworkX Louvain clustering because the upstream
`graspologic` dependency cannot be installed on that interpreter version.

```powershell
.\.graph-tools\Scripts\python tools\knowledge_graph\build_graphify.py . graphify-out --clean
.\.graph-tools\Scripts\python tools\knowledge_graph\build_graphify.py . graphify-technical-documentation --only TECHNICAL_DOCUMENTATION.md --clean
```

OKF bundles are validated with `okf validate`. The interactive viewer is built
with the repository-owned generator because `okf-cli` does not provide a viz
command:

```powershell
.\.graph-tools\Scripts\python tools\knowledge_graph\build_okf_viz.py okf-bundle --strict
.\.graph-tools\Scripts\python tools\knowledge_graph\build_technical_okf.py TECHNICAL_DOCUMENTATION.md okf-technical-documentation --clean
.\.graph-tools\Scripts\python tools\knowledge_graph\build_okf_viz.py okf-technical-documentation --strict
```

Before rebuilding the full graph, keep generated folders and build caches in
`.graphifyignore`; otherwise Graphify can ingest its own output recursively.
