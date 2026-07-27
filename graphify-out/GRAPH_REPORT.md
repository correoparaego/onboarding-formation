# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 893 nodes · 1446 edges · 94 communities (51 shown, 43 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3b145d2e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- reading_gate/services.py
- notifications/services.py
- encrypt_value
- reading_gate/tests.py
- useToast
- ComprehensionTestTests
- ai_generation/views.py
- AdminLLMKey
- react-dom.js
- AdminApp.tsx
- ui/index.ts
- compilerOptions
- reading_gate/models.py
- Dashboard.tsx
- certificates/services.py
- AuditApiTests
- ExpedienteList.tsx
- seed_test_data.py
- page-objects/index.ts
- dependencies
- json_body
- EmployeeFlow
- devDependencies
- Button
- make_client
- BasePage
- courses/views.py
- IssuanceTests
- AuditEvent
- AdminFlow
- compilerOptions
- CertificatePdfTests
- generar_dnis.py
- EmployeeDashboardPage
- EmployeeApp.tsx
- ErrorBoundary
- CourseManagementTests
- Expediente
- HappyPathIntegrationTests
- PdfReaderPage
- AdminSidebar.tsx
- ExpedientePage
- ImportPage
- scripts
- RoleIsolationMiddleware
- RateLimiter
- get_retention_policy
- flows.spec.ts
- AiContentPage
- frontend/package.json
- 0003_seed_badges.py
- test_import.py
- screenshots.spec.ts
- ResponsiveTable.tsx
- AiGenerationConfig
- AuthenticationConfig
- CertificatesConfig
- CoursesConfig
- EmployeesConfig
- mvp_project/urls.py
- NotificationsConfig
- ReadingGateConfig
- vite-env.d.ts
- ai_generation/migrations/0001_initial.py
- authentication/migrations/0001_initial.py
- certificates/migrations/0001_initial.py
- 0002_certificate.py
- common/__init__.py
- courses/migrations/0001_initial.py
- asgi.py
- settings.py
- wsgi.py
- notifications/migrations/0001_initial.py
- reading_gate/migrations/0001_initial.py
- 0002_expediente.py
- @hookform/resolvers
- i18next
- react-pdf
- react
- react-router-dom
- deps/package.json

## God Nodes (most connected - your core abstractions)
1. `BasePage` - 24 edges
2. `Employee` - 19 edges
3. `AdminFlow` - 17 edges
4. `useToast()` - 17 edges
5. `Position` - 16 edges
6. `Course` - 16 edges
7. `compilerOptions` - 16 edges
8. `AdminLLMKey` - 15 edges
9. `encrypt_value()` - 15 edges
10. `FakeLLMClient` - 14 edges

## Surprising Connections (you probably didn't know these)
- `LLMClient` --uses--> `AdminLLMKey`  [INFERRED]
  backend/ai_generation/client.py → backend/ai_generation/models.py
- `OpenAICompatibleClient` --uses--> `AdminLLMKey`  [INFERRED]
  backend/ai_generation/client.py → backend/ai_generation/models.py
- `Employee` --uses--> `EncryptedDNIField`  [INFERRED]
  backend/employees/models.py → backend/common/fields.py
- `Employee` --uses--> `HashedDNILookupField`  [INFERRED]
  backend/employees/models.py → backend/common/fields.py
- `CourseManagementTests` --uses--> `Position`  [INFERRED]
  backend/courses/tests.py → backend/courses/models.py

## Import Cycles
- None detected.

## Communities (94 total, 43 thin omitted)

### Community 0 - "reading_gate/services.py"
Cohesion: 0.05
Nodes (48): certificate_pdf(), is_valid_dni(), Spanish DNI format validation (structure + control letter).  Used by the emplo, Return True if ``value`` is a structurally valid Spanish DNI.      Checks: exa, employee_import(), _is_valid_email(), csrf_exempt, Employee Excel import (spec employee-import, Phase 4).  ``POST /api/import`` ( (+40 more)

### Community 1 - "notifications/services.py"
Cohesion: 0.06
Nodes (38): EmployeeAccessToken, _hash(), Meta, A single-use access token/code issued for an employee's training.      The sam, Create a token and return ``(instance, raw_token, code)``.          The raw va, Redeem a presented ``token`` or ``code``.          Returns ``(employee, "ok")`, Meta, NotificationLog (+30 more)

### Community 2 - "encrypt_value"
Cohesion: 0.08
Nodes (25): AI generation models (spec ai-generation).  ``AdminLLMKey`` stores a per-admin, Encrypt and store the raw key. Caller MUST discard ``raw_key``., Decrypt the raw key. NEVER serialize the result to a response., decrypt_legacy_value(), decrypt_value(), _derive_key(), _derive_lookup_key(), dni_lookup_hash() (+17 more)

### Community 3 - "reading_gate/tests.py"
Cohesion: 0.11
Nodes (18): Course, Meta, Position, Question, QuestionBank, Catalog key linking job positions to mandatory courses.      The design refere, Section, Tests for course-management (spec course-management, Phase 5). (+10 more)

### Community 4 - "useToast"
Cohesion: 0.11
Nodes (25): AiKeyForm(), KeyFormData, keySchema, DraftData, GuidedContent(), PdfTestGen(), Course, CourseDetail (+17 more)

### Community 5 - "ComprehensionTestTests"
Cohesion: 0.10
Nodes (8): ComprehensionTestTests, ExpedienteAndBadgesTests, _make_course_with_bank(), _make_enrollment(), TestCase, Build a course (divisor 3 -> minTime 30/s), sections, and a question bank., ReadingGateAuthzTests, ReadingGateTests

### Community 6 - "ai_generation/views.py"
Cohesion: 0.11
Nodes (20): fake_generate_course_content(), fake_generate_test_questions(), Fake LLM responses for testing. Returns deterministic course content and test q, Generate fake test questions for testing., Generate fake course draft for testing., build_content_prompt(), build_test_prompt(), Prompt builders (design §PII Guard).  These functions build LLM prompts from C (+12 more)

### Community 7 - "AdminLLMKey"
Cohesion: 0.13
Nodes (11): FakeLLMClient, Deterministic stand-in for tests. Never performs network I/O., AdminLLMKey, Meta, FakeClientTests, GenerationFlowTests, HitlSaveGuardTests, TestCase (+3 more)

### Community 8 - "react-dom.js"
Cohesion: 0.08
Nodes (11): TODO: When we delete legacy mode, we should make this error argument, TODO: Remove this dead flag, TODO: Remove outdated deferRenderPhaseUpdateToNextBatch experiment. We, NOTE: This will not work correctly for non-generic events such as `change`,, NOTE: menuitem's close tag should be omitted, but that causes problems., TODO: Remove Update flag from before mutation phase by re-landing Visibility, TODO: This prevents the assignment of defaultValue to regular, TODO: Only ignore them on controlled tags. (+3 more)

### Community 9 - "AdminApp.tsx"
Cohesion: 0.14
Nodes (16): AdminApp(), AiKeyForm, GuidedContent, PdfTestGen, authApi, AdminLogin(), AdminUser, AuthContext (+8 more)

### Community 10 - "ui/index.ts"
Cohesion: 0.10
Nodes (12): CardProps, paddingMap, EmptyStateProps, InputProps, ProgressBarProps, SkeletonCard(), SkeletonCardProps, SkeletonTable() (+4 more)

### Community 11 - "compilerOptions"
Cohesion: 0.09
Nodes (22): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+14 more)

### Community 12 - "reading_gate/models.py"
Cohesion: 0.19
Nodes (9): Authentication models for MVP Formación Inicial.  Admins reuse Django's built-, Certificate, One active certificate per passed enrollment (spec certificate §One Per)., Tests for certificate PDF + badge award (spec certificate, badges)., Certificate PDF endpoint (admin-only via RoleIsolationMiddleware)., Employee, An imported employee.      DNI is stored VERBATIM (no trim/normalise/uppercase, Tests for secure-access issuance + delivery logging (spec secure-access, notific (+1 more)

### Community 13 - "Dashboard.tsx"
Cohesion: 0.13
Nodes (15): CourseStats, Dashboard(), ExpedienteResponse, ExpedienteRow, STATUS_LABELS, StatusStats, NetworkBanner(), ThemeToggle() (+7 more)

### Community 14 - "certificates/services.py"
Cohesion: 0.14
Nodes (15): Badge, EmployeeBadge, Meta, award_badges_on_pass(), _core_fields(), _core_hash(), ensure_badges(), generate_certificate_pdf() (+7 more)

### Community 15 - "AuditApiTests"
Cohesion: 0.12
Nodes (4): AuditApiTests, AuditCoverageTests, TestCase, _seed()

### Community 16 - "ExpedienteList.tsx"
Cohesion: 0.11
Nodes (11): columns, Expediente, ExpedienteResponse, BreadcrumbItem, BreadcrumbProps, Badge(), BadgeProps, Size (+3 more)

### Community 17 - "seed_test_data.py"
Cohesion: 0.15
Nodes (8): generate_excel(), make_minimal_pdf(), Comprehensive seed script for testing the onboarding formation platform.  Crea, Generate a minimal valid 1-page PDF with the given title using reportlab., Generate a structurally valid Spanish DNI for a given index (0-based)., seed_courses(), seed_employees(), valid_dni_for_index()

### Community 19 - "dependencies"
Cohesion: 0.13
Nodes (15): axios, dependencies, axios, i18next-browser-languagedetector, react-dom, react-hook-form, react-i18next, recharts (+7 more)

### Community 20 - "json_body"
Cohesion: 0.18
Nodes (10): ai_key_set(), admin_login(), admin_logout(), employee_redeem(), csrf_exempt, Authentication views (spec authentication).  - ``POST /api/auth/admin/login``, json_body(), course_list_create() (+2 more)

### Community 22 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react (+7 more)

### Community 23 - "Button"
Cohesion: 0.17
Nodes (9): Button(), ButtonProps, Size, sizeStyles, Variant, variantStyles, ConfirmDialog(), ConfirmDialogProps (+1 more)

### Community 24 - "make_client"
Cohesion: 0.24
Nodes (7): LLMClient, make_client(), OpenAICompatibleClient, OpenAI-compatible LLM client (spec ai-generation §OpenAI-Compatible Client)., Factory: returns a fake client (tests) or a real OpenAI-compatible one., Abstract client. Subclasses implement `chat`., Talks to any OpenAI-compatible `/chat/completions` endpoint.

### Community 26 - "courses/views.py"
Cohesion: 0.22
Nodes (6): course_catalog(), question_bank_create(), Course management views (spec course-management, Phase 5).  Admin CRUD for cou, GET /api/courses/catalog?position=Operario -> mandatory courses., Return a single valid correct_index or raise ValidationError., _validate_question()

### Community 27 - "IssuanceTests"
Cohesion: 0.22
Nodes (5): IssuanceTests, _make_enrollment(), TestCase, ResendEndpointTests, TransportConfigTests

### Community 28 - "AuditEvent"
Cohesion: 0.22
Nodes (5): AuditEventAdmin, Read-only admin for the append-only audit log (spec audit-log §No Mutation)., AuditEvent, Append-only compliance log (RGPD/LOPDGDD evidence trail).      No update/delet, register

### Community 30 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, strict, include (+1 more)

### Community 31 - "CertificatePdfTests"
Cohesion: 0.31
Nodes (5): BadgeSeedTests, _build_passed_enrollment(), CertificatePdfTests, _pdf_text(), TestCase

### Community 32 - "generar_dnis.py"
Cohesion: 0.32
Nodes (7): calcular_letra_dni(), generar_dni_valido(), generar_lista_dnis(), Script para generar DNIs españoles válidos. Formato: 8 dígitos + letra de contr, Calcula la letra de control para un DNI., Genera un DNI español válido aleatorio., Genera una lista de DNIs únicos válidos.

### Community 34 - "EmployeeApp.tsx"
Cohesion: 0.36
Nodes (3): client, PdfReaderProps, Enrollment

### Community 35 - "ErrorBoundary"
Cohesion: 0.25
Nodes (3): ErrorBoundary, Props, State

### Community 37 - "Expediente"
Cohesion: 0.29
Nodes (5): Expediente, Meta, Per-(enrollment, section) accumulated reading time.      Cross-device resume i, Per-enrollment training result (spec expediente §Result Storage).      Linked, ReadingProgress

### Community 40 - "AdminSidebar.tsx"
Cohesion: 0.29
Nodes (3): AdminLayoutProps, AdminSidebarProps, navItems

### Community 43 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, test:e2e

### Community 46 - "get_retention_policy"
Cohesion: 0.40
Nodes (3): get_retention_policy(), Retention policy hook (RGPD / LOPDGDD) — task 1.4.  Centralises retention wind, Return retention window in days for ``entity`` (None = indefinite).

### Community 47 - "flows.spec.ts"
Cohesion: 0.60
Nodes (3): getEmployeeToken(), TEST_DATA, SCREENSHOTS_DIR

### Community 49 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 51 - "test_import.py"
Cohesion: 0.50
Nodes (3): Script para probar la importación de empleados y ver el error exacto., Prueba el endpoint de importación con el archivo de ejemplo., test_import()

## Knowledge Gaps
- **137 isolated node(s):** `Migration`, `Meta`, `Migration`, `Meta`, `Migration` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Course` connect `reading_gate/tests.py` to `CourseManagementTests`, `AdminLLMKey`, `reading_gate/models.py`, `certificates/services.py`, `seed_test_data.py`, `courses/views.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `Position` connect `reading_gate/tests.py` to `reading_gate/services.py`, `CourseManagementTests`, `AdminLLMKey`, `certificates/services.py`, `seed_test_data.py`, `courses/views.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Employee` connect `reading_gate/models.py` to `reading_gate/services.py`, `seed_test_data.py`, `encrypt_value`, `reading_gate/tests.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Employee` (e.g. with `EncryptedDNIField` and `HashedDNILookupField`) actually correct?**
  _`Employee` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Meta`, `Migration` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `reading_gate/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05376972530683811 - nodes in this community are weakly interconnected._
- **Should `notifications/services.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05660377358490566 - nodes in this community are weakly interconnected._