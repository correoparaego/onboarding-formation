# SDD Init — onboarding-formation

**Detected**: 2026-07-14
**Persistence mode**: openspec (file backend)
**External memory (Engram/MCP)**: unavailable this session — openspec file backend only
**Strict TDD**: false (no test runner detected — greenfield)

## Project
- Key: onboarding-formation
- Workspace: C:\Users\Egoitz\Documents\onboarding formation
- Nature: Greenfield web application
- Idea source: idea.txt (Spanish, evolving)

## Stack detection
No build/manifest files found (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`,
Makefile). No source code present. Stack **NOT detected** — recorded by absence, not guessed.
Candidates to decide (web app): a language + web framework (e.g. Node/Next.js,
Python/Django or FastAPI, Go). No constraints observed in repo.

## Architecture detection
No code or patterns observable. The idea doc implies (not yet implemented):
- Actors: company administrator, employee, platform super-admin (optional).
- MVP scope: single company (no complex multi-tenant), Excel employee import,
  1-2 PDF courses with timed reader + manual test, email notification, basic PDF
  certificate, minimal gamification (initial badges).
- Deferred to later phases: SMS/WhatsApp, multi-tenancy, full gamification,
  AI-assisted course generation (manual / semi-auto / auto modes).

## Conventions detection
- No linter, formatter, or type-checker config detected.
- No project-level convention files (AGENTS.md, CLAUDE.md, .cursorrules,
  GEMINI.md, copilot-instructions.md) present.
- User-level agent instructions exist at `~/.config/opencode/AGENTS.md`
  (Gentle AI persona + Engram protocol) — governs agent behavior, not project
  code style.

## Testing capability
| Layer        | Available | Tool |
| ------------ | --------- | ---- |
| Unit         | ❌        | — |
| Integration  | ❌        | — |
| E2E          | ❌        | — |
| Coverage     | ❌        | — |
| Linter       | ❌        | — |
| Type checker | ❌        | — |
| Formatter    | ❌        | — |

Strict TDD cannot be enforced until a stack and test runner are selected.

## Open product / legal questions (from idea.txt)
- RGPD/LOPDGDD: DNI is sensitive data — needs consent, encryption at rest/in
  transit, per-company isolation.
- Reading-time integrity: ensure real activity vs. open-tab bypass.
- Employee identity verification during reading/exam.
- Notification channel cost and opt-in (SMS/WhatsApp).
- Certificate legal validity / electronic signature.
- Multi-tenant strict data separation.
- Audit/trace logs for reading and exam (compliance).

## Persistence
- openspec/config.yaml — context, strict_tdd, testing, phase rules.
- openspec/sdd-init/onboarding-formation.md — this context record.
- .atl/skill-registry.md — already present and current; refreshed 2026-07-14.

## Next steps
Run `/sdd-explore` to refine MVP scope and select the technology stack before any
change proposal. Re-run init once a manifest/test runner exists to enable strict TDD.
