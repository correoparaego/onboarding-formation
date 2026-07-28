# Graph Report - onboarding formation

## Generation
- Generated: `2026-07-28T18:25:17.239072+00:00`
- Git commit: `ce62f59607cf9558e76866599de6982dbb9cbb36`
- Extractor: `graphifyy 0.1.14` with path-safe node namespaces
- Clustering: deterministic NetworkX Louvain (`seed=42`)
- Output: `C:/Users/Egoitz/Documents/onboarding formation/graphify-out`

## Corpus
- 304 source files
- 2057 nodes
- 2603 edges
- 188 communities

## God Nodes
- `jquery.js`: 86 edges · `backend/staticfiles/admin/js/vendor/jquery/jquery.js`
- `select2.full.js`: 64 edges · `backend/staticfiles/admin/js/vendor/select2/select2.full.js`
- `jquery.min.js`: 54 edges · `backend/staticfiles/admin/js/vendor/jquery/jquery.min.js`
- `jquery-3.7.1.min.js`: 54 edges · `backend/staticfiles/rest_framework/js/jquery-3.7.1.min.js`
- `xregexp.js`: 39 edges · `backend/staticfiles/admin/js/vendor/xregexp/xregexp.js`
- `seed_test_data.py`: 30 edges · `backend/seed_test_data.py`
- `services.py`: 29 edges · `backend/reading_gate/services.py`
- `build_graphify.py`: 28 edges · `tools/knowledge_graph/build_graphify.py`
- `react`: 28 edges · ``
- `xregexp.min.js`: 27 edges · `backend/staticfiles/admin/js/vendor/xregexp/xregexp.min.js`
- `django_db`: 27 edges · ``
- `views.py`: 22 edges · `backend/courses/views.py`
- `tests.py`: 22 edges · `backend/reading_gate/tests.py`
- `tests.py`: 19 edges · `backend/ai_generation/tests.py`
- `views.py`: 19 edges · `backend/reading_gate/views.py`
- `views.py`: 18 edges · `backend/employees/views.py`
- `tests.py`: 18 edges · `backend/notifications/tests.py`
- `Design: MVP Formación Inicial`: 18 edges · `openspec/changes/archive/2026-07-15-mvp-formacion-inicial/design.md`
- `test`: 18 edges · ``
- `Tasks: MVP Formación Inicial`: 17 edges · `openspec/changes/archive/2026-07-15-mvp-formacion-inicial/tasks.md`

## Communities

### 0. Backend · Code
- Nodes: 221
- Examples: fake_llm.py, fake_generate_course_content(), fake_generate_test_questions(), 0001_initial.py, Migration, models.py, AdminLLMKey, .get_raw_key()

### 1. Frontend · Code
- Nodes: 119
- Examples: AdminApp.tsx, handleLogout(), AiKeyForm.tsx, submit(), GuidedContent.tsx, discardDraft(), generate(), restoreDraft()

### 2. Technical Documentation.Md · Document
- Nodes: 103
- Examples: Arquitectura y documentación técnica de Onboarding Formation, 8. IA y herramientas de ingeniería, 8.1 IA integrada en el producto, Selección efectiva de proveedor, Controles, Riesgos, 8.2 Herramientas/agentes usados en desarrollo, 8.3 Flujo de IA recomendado para ingeniería

### 3. Frontend · Code
- Nodes: 101
- Examples: test-data.ts, getEmployeeToken(), AdminFlow.ts, AdminFlow, .completeFullFlow(), .constructor(), .createCourse(), .generateAIContent()

### 4. Backend · Code
- Nodes: 87
- Examples: jquery.js, addCombinator(), addGetHookIf(), addToPrefiltersOrTransports(), adjustCSS(), adoptValue(), ajaxConvert(), ajaxExtend()

### 5. Openspec · Document
- Nodes: 77
- Examples: Apply Progress — mvp-formacion-inicial (PR1 + PR2 + PR3 + PR4 + PR5 + PR6), Issues Found, Completed Tasks (PR3 — cumulative continuation), PR3 — Course Management + AI Generation + Enrollment Assignment, PR4 — Timed Reading Gate + Comprehension Test (stacked-to-main), Files Changed (PR3), Work Unit Evidence (PR3), PR3 — Course management

### 6. Backend · Code
- Nodes: 68
- Examples: prompts.py, build_content_prompt(), build_test_prompt(), sanitizer.py, sanitize_many(), sanitize_text(), models.py, EmployeeAccessToken

### 7. Backend · Code
- Nodes: 65
- Examples: select2.full.js, AjaxAdapter(), AllowClear(), ArrayAdapter(), AttachBody(), AttachContainer(), BaseAdapter(), BaseConstructor()

### 8. Backend · Code
- Nodes: 53
- Examples: jquery.min.js, A(), Ae(), at(), B(), Be(), c(), Ct()

### 9. Backend · Code
- Nodes: 53
- Examples: jquery-3.7.1.min.js, A(), Ae(), at(), B(), Be(), c(), Ct()

### 10. Backend · Code
- Nodes: 42
- Examples: TestCase, ComprehensionTestTests, ._correct_answers(), .setUp(), .test_fail_resets_reading_and_increments(), .test_fourth_attempt_is_blocked_and_exhausted(), .test_get_questions_withholds_correct_index(), .test_pass_flow_sets_passed()

### 11. Backend · Code
- Nodes: 40
- Examples: xregexp.js, addMatch(), _arrayLikeToArray(), _arrayWithHoles(), augment(), buildAstral(), cacheAstral(), cacheInvertedBmp()

### 12. Backend · Code
- Nodes: 37
- Examples: crypto.py, decrypt_legacy_value(), decrypt_value(), _derive_key(), _derive_lookup_key(), dni_lookup_hash(), encrypt_value(), retention.py

### 13. Frontend · Document
- Nodes: 35
- Examples: Guia de Captura de Pantallas — Plataforma de Onboarding, Gestion de cursos (/admin/courses), Detalle de curso, Clave IA (/admin/ai/key), Contenido IA (/admin/ai/content), Test desde PDF (/admin/ai/tests), Expediente (/admin/expediente), Acceso empleado (/employee/redeem)

### 14. Backend · Code
- Nodes: 33
- Examples: models.py, Course, .__str__(), CourseVersion, .__str__(), Meta, Position, .save()

### 15. Backend · Code
- Nodes: 28
- Examples: xregexp.min.js, addMatch(), _arrayLikeToArray(), augment(), cacheAstral(), cacheInvertedBmp(), charCode(), clipDuplicates()

### 16. Backend · Code
- Nodes: 27
- Examples: generar_dnis.py, calcular_letra_dni(), generar_dni_valido(), generar_lista_dnis(), services.py, _all_sections_complete(), apply_assignment(), assign_courses()

### 17. Deployment Render.Md · Document
- Nodes: 25
- Examples: Despliegue en Render, 7. Seed data (opcional), Solución de problemas, Pasos de despliegue, El backend no arranca, Error de CORS, Error de CSRF, 1. Preparar el repositorio

### 18. Openspec · Document
- Nodes: 25
- Examples: Design: MVP Formación Inicial, Testing Strategy, Threat Matrix, Migration / Rollout, Open Questions, Tenancy Model (explicit, config rule), Design: MVP Formación Inicial, Architecture Overview

### 19. Backend · Code
- Nodes: 24
- Examples: urls.py, urls.py, urls.py, urls.py, urls.py, urls.py, urls.py, views.py

### 20. Backend · Code
- Nodes: 22
- Examples: apps.py, AppConfig, AiGenerationConfig, apps.py, AppConfig, AuthenticationConfig, apps.py, AppConfig

### 21. Readme.Md · Document
- Nodes: 21
- Examples: MVP Formación Inicial, Section PDF storage, Frontend — run locally, Tests, Backend (two equivalent harnesses), Option A — Django test runner (always works):, Option B — pytest (requires pytest-django, already added to requirements):, Navigation and workflow walkthrough

### 22. Openspec · Document
- Nodes: 19
- Examples: Tasks: MVP Formación Inicial, Suggested Work Units (PR slices), Phase 2: Data Model & Migrations, Phase 3: Authentication, Tasks: MVP Formación Inicial, Phase 4: Employee Import, Phase 5: Course Management, Phase 6: AI Generation

### 23. Backend · Code
- Nodes: 18
- Examples: TestCase, AuditApiTests, .setUp(), .test_get_filters_by_date(), .test_get_filters_by_employee(), .test_get_filters_by_enrollment(), .test_get_filters_by_event_type(), .test_no_dni_in_payloads()

### 24. Idea.Txt · Document
- Nodes: 18
- Examples: Plataforma de Formación Inicial para Empleados (Onboarding multi-empresa), 3. Flujo principal, Plataforma de Formación Inicial para Empleados (Onboarding multi-empresa), 4. Funcionalidades detalladas, 4.1 Carga de empleados (Excel), 4.2 Notificaciones (SMS / WhatsApp), 4.3 Catálogo de cursos por puesto, 4.4 Lector PDF con control anti-salto

### 25. Openspec · Document
- Nodes: 18
- Examples: Proposal: MVP Formación Inicial, Rollback Plan, Dependencies, Success Criteria, Out of Scope (MVP), Proposal: MVP Formación Inicial, Capabilities (contract with sdd-spec), New Capabilities

### 26. Backend · Code
- Nodes: 17
- Examples: client.py, FakeLLMClient, .chat(), .__init__(), GeminiClient, .chat(), .__init__(), LLMClient

### 27. Backend · Code
- Nodes: 17
- Examples: select2.full.min.js, A(), b(), c(), D(), e(), i(), l()

### 28. Openspec · Document
- Nodes: 17
- Examples: Delta for ai-generation, Scenario: Key stored encrypted and never exposed, Scenario: Employee routes never load the key, Delta for ai-generation, Requirement: OpenAI-Compatible Client, Scenario: Generation uses stored provider config, Requirement: Guided Content Generation, ADDED Requirements

### 29. Openspec · Document
- Nodes: 17
- Examples: Delta for ai-generation, Scenario: Key stored encrypted and never exposed, Scenario: Employee routes never load the key, Delta for ai-generation, Requirement: OpenAI-Compatible Client, Scenario: Generation uses stored provider config, Requirement: Guided Content Generation, ADDED Requirements

### 30. Backend · Code
- Nodes: 16
- Examples: TestCase, BatchAccessCodeTests, .setUp(), .test_batch_endpoint_requires_csrf(), .test_batch_limit_is_enforced(), .test_batch_returns_unique_codes_once_and_invalidates_old_access(), .test_missing_employees_and_non_object_json_are_reported(), IssuanceTests

### 31. Technical Documentation.Md · Document
- Nodes: 16
- Examples: 9. Despliegue en Render, 9.1 Infraestructura actual, 9.2 Build de imagen, 9.3 Arranque actual, 9.4 Enrutamiento, 9.5 Variables y secretos, Declaradas en render.yaml, Soportadas, no declaradas en Blueprint

### 32. Backend · Code
- Nodes: 14
- Examples: TestCase, CourseManagementTests, .setUp(), .test_catalog_case_insensitive(), .test_catalog_lookup_returns_mandatory_courses(), .test_course_create_with_sections(), .test_draft_can_be_edited_and_published_without_changing_version_one(), .test_single_correct_enforced_on_save()

### 33. Backend · Code
- Nodes: 14
- Examples: RelatedObjectLookups.js, addPopupIndex(), dismissAddRelatedObjectPopup(), dismissChangeRelatedObjectPopup(), dismissChildPopups(), dismissDeleteRelatedObjectPopup(), dismissRelatedLookupPopup(), removePopupIndex()

### 34. Openspec · Document
- Nodes: 14
- Examples: Exploration: mvp-formacion-inicial, 8. Ready for Proposal, 2. MVP Scope (tightened), Actors (MVP), Exploration: mvp-formacion-inicial, Core flows, Out of scope (MVP — explicit), 3. Compliance & Legal Assumptions (RGPD / LOPDGDD)

### 35. Frontend · Document
- Nodes: 13
- Examples: E2E Test Results — Phase B, How to Run, Admin Flow Results, E2E Test Results — Phase B, Employee Flow Results, Files Created, Page Objects (e2e/page-objects/), Flows (e2e/flows/)

### 36. Openspec · Document
- Nodes: 13
- Examples: Delta for comprehension-test, Requirement: Distinct Question Subset Per Attempt, Scenario: Different subsets, Delta for comprehension-test, Requirement: Single Correct Answer, Scenario: Validation on authoring, Requirement: Fail Restarts Reading, Scenario: Fail triggers restart

### 37. Openspec · Document
- Nodes: 13
- Examples: Verification Report — mvp-formacion-inicial, RESOLVED (previously BLOCKING), WARNING (non-blocking — informational), SUGGESTION (informational), 7. Final Verdict, Archive gate, Verification Report — mvp-formacion-inicial, 2. Build / Test / Coverage Evidence

### 38. Openspec · Document
- Nodes: 13
- Examples: Delta for comprehension-test, Requirement: Distinct Question Subset Per Attempt, Scenario: Different subsets, Delta for comprehension-test, Requirement: Single Correct Answer, Scenario: Validation on authoring, Requirement: Fail Restarts Reading, Scenario: Fail triggers restart

### 39. Backend · Code
- Nodes: 11
- Examples: actions.js, affectedCheckboxes(), checker(), clearAcross(), hide(), ready(), reset(), show()

### 40. Deployment.Md · Document
- Nodes: 11
- Examples: Despliegue — MVP Formación Inicial, 2. Push de ramas y PRs (stacked-to-main), Despliegue — MVP Formación Inicial, ... y así con las 7, en orden., 3. Variables de entorno (backend Django), 4. Despliegue del backend (Django), 5. Despliegue del frontend (React/Vite), 6. Verificación post-despliegue

### 41. Openspec · Document
- Nodes: 11
- Examples: Delta for audit-log, Scenario: Event appended, Requirement: No Mutation, Delta for audit-log, Scenario: Delete rejected, Requirement: Cross-Device Context, Scenario: Context captured, Requirement: Event Coverage

### 42. Openspec · Document
- Nodes: 11
- Examples: Delta for authentication, Scenario: Admin login, Requirement: Employee Magic-Link/Code Access, Delta for authentication, Scenario: Employee enters code, Requirement: Session Isolation, Scenario: Employee blocked from admin, Requirement: Admin Logout

### 43. Openspec · Document
- Nodes: 11
- Examples: Delta for badges, Requirement: Award "Primer curso", Scenario: First pass awards badge, Delta for badges, Requirement: Award "Catálogo completo", Scenario: All position courses passed, Requirement: Award "Sin fallos", Scenario: Clean first-pass

### 44. Openspec · Document
- Nodes: 11
- Examples: Delta for employee-import, Requirement: DNI Stored Verbatim (RGPD), Delta for employee-import, Scenario: DNI preserved byte-for-byte, Requirement: Validation Report, Scenario: Rejected rows reported, Requirement: Dedupe by DNI, ADDED Requirements

### 45. Openspec · Document
- Nodes: 11
- Examples: Delta for timed-reading, Scenario: Advance blocked before minTime, Requirement: Active-Time Accumulation via Heartbeats, Delta for timed-reading, Scenario: Heartbeat credited, Requirement: Cross-Device Resume, Scenario: Resume on new device, Requirement: Completion on Full Gate Pass

### 46. Openspec · Document
- Nodes: 11
- Examples: Delta for audit-log, Scenario: Event appended, Requirement: No Mutation, Delta for audit-log, Scenario: Delete rejected, Requirement: Cross-Device Context, Scenario: Context captured, Requirement: Event Coverage

### 47. Openspec · Document
- Nodes: 11
- Examples: Delta for authentication, Scenario: Admin login, Requirement: Employee Magic-Link/Code Access, Delta for authentication, Scenario: Employee enters code, Requirement: Session Isolation, Scenario: Employee blocked from admin, Requirement: Admin Logout

### 48. Openspec · Document
- Nodes: 11
- Examples: Delta for badges, Requirement: Award "Primer curso", Scenario: First pass awards badge, Delta for badges, Requirement: Award "Catálogo completo", Scenario: All position courses passed, Requirement: Award "Sin fallos", Scenario: Clean first-pass

### 49. Openspec · Document
- Nodes: 11
- Examples: Delta for employee-import, Requirement: DNI Stored Verbatim (RGPD), Delta for employee-import, Scenario: DNI preserved byte-for-byte, Requirement: Validation Report, Scenario: Rejected rows reported, Requirement: Dedupe by DNI, ADDED Requirements

### 50. Openspec · Document
- Nodes: 11
- Examples: Delta for timed-reading, Scenario: Advance blocked before minTime, Requirement: Active-Time Accumulation via Heartbeats, Delta for timed-reading, Scenario: Heartbeat credited, Requirement: Cross-Device Resume, Scenario: Resume on new device, Requirement: Completion on Full Gate Pass

### 51. Backend · Code
- Nodes: 10
- Examples: prettify-min.js, B(), C(), D(), E(), k(), L(), M()

### 52. Openspec · Document
- Nodes: 10
- Examples: Archive Report — mvp-formacion-inicial, Final Stack, Archive Report — mvp-formacion-inicial, Scope, Verification Result, Resolved W1 Debt (DNI crypto), Source of Truth Updated, Archive Contents (audit trail — preserved, never modified)

### 53. Openspec · Document
- Nodes: 10
- Examples: SDD Init — onboarding-formation, Stack detection, SDD Init — onboarding-formation, Architecture detection, Conventions detection, Testing capability, Open product / legal questions (from idea.txt), Persistence

### 54. Backend · Document
- Nodes: 9
- Examples: Information about icons in this directory, Usage, Information about icons in this directory, Modifications, Contributing SVG Icons, ⚠️ Important: Changing Font Awesome Version, License, Adding a new icon

### 55. Openspec · Document
- Nodes: 9
- Examples: Delta for certificate, Scenario: Certificate generated on pass, Requirement: DNI Verbatim on Certificate, Delta for certificate, Scenario: DNI reproduced, Requirement: One Certificate Per Passed Enrollment, Scenario: Regeneration, ADDED Requirements

### 56. Openspec · Document
- Nodes: 9
- Examples: Delta for course-management, Requirement: Test and Question-Bank Authoring, Delta for course-management, Scenario: Bank attached to course, Requirement: Catalog by Position, Scenario: Position catalog lookup, ADDED Requirements, Requirement: PDF Course Authoring

### 57. Openspec · Document
- Nodes: 9
- Examples: Delta for expediente, Requirement: Admin Filter by Course Completion, Scenario: Filter completed, Delta for expediente, Requirement: Retention Policy, Scenario: Rollback preserves, ADDED Requirements, Requirement: Result Storage Per Enrollment

### 58. Openspec · Document
- Nodes: 9
- Examples: Delta for notifications, Requirement: Spanish Templates, Scenario: Access email in Spanish, Delta for notifications, Requirement: Delivery Logging, Scenario: Logged without token, ADDED Requirements, Requirement: Configurable Email Transport

### 59. Openspec · Document
- Nodes: 9
- Examples: Delta for secure-access, Scenario: Token issued on assignment, Requirement: Token Delivery, Delta for secure-access, Scenario: Link delivered by email, Requirement: Token Consumption, Scenario: Reuse blocked, ADDED Requirements

### 60. Openspec · Document
- Nodes: 9
- Examples: Delta for certificate, Scenario: Certificate generated on pass, Requirement: DNI Verbatim on Certificate, Delta for certificate, Scenario: DNI reproduced, Requirement: One Certificate Per Passed Enrollment, Scenario: Regeneration, ADDED Requirements

### 61. Openspec · Document
- Nodes: 9
- Examples: Delta for course-management, Requirement: Test and Question-Bank Authoring, Delta for course-management, Scenario: Bank attached to course, Requirement: Catalog by Position, Scenario: Position catalog lookup, ADDED Requirements, Requirement: PDF Course Authoring

### 62. Openspec · Document
- Nodes: 9
- Examples: Delta for expediente, Requirement: Admin Filter by Course Completion, Scenario: Filter completed, Delta for expediente, Requirement: Retention Policy, Scenario: Rollback preserves, ADDED Requirements, Requirement: Result Storage Per Enrollment

### 63. Openspec · Document
- Nodes: 9
- Examples: Delta for notifications, Requirement: Spanish Templates, Scenario: Access email in Spanish, Delta for notifications, Requirement: Delivery Logging, Scenario: Logged without token, ADDED Requirements, Requirement: Configurable Email Transport

### 64. Openspec · Document
- Nodes: 9
- Examples: Delta for secure-access, Scenario: Token issued on assignment, Requirement: Token Delivery, Delta for secure-access, Scenario: Link delivered by email, Requirement: Token Consumption, Scenario: Reuse blocked, ADDED Requirements

### 65. Backend · Code
- Nodes: 8
- Examples: EncryptedDNIField, .from_db_value(), .get_prep_value(), .__init__(), HashedDNILookupField, .from_db_value(), .get_prep_value(), .__init__()

### 66. Backend · Code
- Nodes: 8
- Examples: TestCase, DniCryptoTests, .test_dni_roundtrip_verbatim(), .test_duplicate_dni_rejected_via_lookup(), .test_equal_dnis_diff_ciphertext_same_lookup(), .test_fixed_nonce_gone(), .test_import_rejects_duplicate_dni(), .test_legacy_ciphertext_recoverable()

### 67. Backend · Code
- Nodes: 8
- Examples: bootstrap.min.js, e(), i(), l(), n(), r(), s(), u()

### 68. Backend · Document
- Nodes: 8
- Examples: MVP Formación Inicial — backend dependencies, Phase 4 — Excel employee import, Phase 11 — Certificate PDF generation, Phase 8 — Optional Resend email transport (only needed when EMAILTRANSPORT=resend), MVP Formación Inicial — backend dependencies, Phase 15 — QA harness (pytest can also be run via python manage.py test), Production, Later phases will extend this list (reportlab, pdfplumber, ...).

### 69. Backend · Code
- Nodes: 7
- Examples: middleware.py, APICsrfeExemptionMiddleware, .__call__(), .__init__(), RoleIsolationMiddleware, .__call__(), .__init__()

### 70. Backend · Code
- Nodes: 7
- Examples: TestCase, HappyPathIntegrationTests, ._employee_session(), ._import_employee(), ._read_to_complete(), .setUp(), .test_import_read_test_cert_audit()

### 71. Openspec · Document
- Nodes: 7
- Examples: Delta for enrollment-assignment, Scenario: Auto-enrollment on import, Requirement: Assignment Idempotency, Delta for enrollment-assignment, Scenario: Re-import skips duplicates, ADDED Requirements, Requirement: Mandatory Assignment Per Position

### 72. Openspec · Document
- Nodes: 7
- Examples: Delta for enrollment-assignment, Scenario: Auto-enrollment on import, Requirement: Assignment Idempotency, Delta for enrollment-assignment, Scenario: Re-import skips duplicates, ADDED Requirements, Requirement: Mandatory Assignment Per Position

### 73. Backend · Code
- Nodes: 6
- Examples: TestCase, EmployeePositionManagementTests, .setUp(), .test_bulk_position_change(), .test_employee_routes_require_admin(), .test_individual_position_change_preserves_imported_label()

### 74. Backend · Code
- Nodes: 5
- Examples: core.js, findPosX(), findPosY(), quickElement(), removeChildren()

### 75. Frontend · External
- Nodes: 5
- Examples: index.ts, es_json, i18next, i18next_browser_languagedetector, react_i18next

### 76. Backend · Code
- Nodes: 4
- Examples: models.py, Meta, NotificationLog, .__str__()

### 77. Backend · Code
- Nodes: 4
- Examples: theme.js, cycleTheme(), initTheme(), setTheme()

### 78. Backend · Code
- Nodes: 4
- Examples: ajax-form.js, captureSubmittingElement(), doAjaxSubmit(), replaceDocument()

### 79. Backend · Code
- Nodes: 4
- Examples: csrf.js, csrfSafeMethod(), getCookie(), sameOrigin()

### 80. Tools · Document
- Nodes: 4
- Examples: graphifyy depends on a legacy graspologic stack that is incompatible with, graphifyy depends on a legacy graspologic stack that is incompatible with, Python 3.14. Install the package itself with --no-deps on 3.14; the compatible, runtime dependencies used by this repository are pinned below.

### 81. Backend · Code
- Nodes: 3
- Examples: cancel.js, handleClick(), ready()

### 82. Backend · Code
- Nodes: 3
- Examples: urlify.js, downcode(), URLify()

### 83. Frontend · External
- Nodes: 3
- Examples: vite.config.ts, plugin_react, vite

### 84. Tools · Document
- Nodes: 3
- Examples: Knowledge graph generation, Toolchain, Knowledge graph generation

### 85. Backend · Code
- Nodes: 2
- Examples: calendar.js, Calendar()

### 86. Backend · Code
- Nodes: 2
- Examples: nav_sidebar.js, initSidebarQuickFilter()

### 87. Backend · Code
- Nodes: 2
- Examples: bs.js, e()

### 88. Backend · Code
- Nodes: 2
- Examples: cs.js, e()

### 89. Backend · Code
- Nodes: 2
- Examples: hr.js, n()

### 90. Backend · Code
- Nodes: 2
- Examples: lt.js, n()

### 91. Backend · Code
- Nodes: 2
- Examples: lv.js, e()

### 92. Backend · Code
- Nodes: 2
- Examples: ru.js, n()

### 93. Backend · Code
- Nodes: 2
- Examples: sr.js, n()

### 94. Backend · Code
- Nodes: 2
- Examples: sr-Cyrl.js, n()

### 95. Backend · Code
- Nodes: 2
- Examples: uk.js, n()

### 96. Frontend · Code
- Nodes: 2
- Examples: client.ts, axios

### 97. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 98. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 99. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 100. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 101. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 102. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 103. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 104. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 105. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 106. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 107. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 108. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 109. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 110. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 111. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 112. Backend · Code
- Nodes: 1
- Examples: __init__.py

### 113. Backend · Code
- Nodes: 1
- Examples: DateTimeShortcuts.js

### 114. Backend · Code
- Nodes: 1
- Examples: autocomplete.js

### 115. Backend · Code
- Nodes: 1
- Examples: change_form.js

### 116. Backend · Code
- Nodes: 1
- Examples: filters.js

### 117. Backend · Code
- Nodes: 1
- Examples: inlines.js

### 118. Backend · Code
- Nodes: 1
- Examples: jquery.init.js

### 119. Backend · Code
- Nodes: 1
- Examples: popup_response.js

### 120. Backend · Code
- Nodes: 1
- Examples: prepopulate.js

### 121. Backend · Code
- Nodes: 1
- Examples: prepopulate_init.js

### 122. Backend · Code
- Nodes: 1
- Examples: SelectBox.js

### 123. Backend · Code
- Nodes: 1
- Examples: SelectFilter2.js

### 124. Backend · Code
- Nodes: 1
- Examples: af.js

### 125. Backend · Code
- Nodes: 1
- Examples: ar.js

### 126. Backend · Code
- Nodes: 1
- Examples: az.js

### 127. Backend · Code
- Nodes: 1
- Examples: bg.js

### 128. Backend · Code
- Nodes: 1
- Examples: bn.js

### 129. Backend · Code
- Nodes: 1
- Examples: ca.js

### 130. Backend · Code
- Nodes: 1
- Examples: da.js

### 131. Backend · Code
- Nodes: 1
- Examples: de.js

### 132. Backend · Code
- Nodes: 1
- Examples: dsb.js

### 133. Backend · Code
- Nodes: 1
- Examples: el.js

### 134. Backend · Code
- Nodes: 1
- Examples: en.js

### 135. Backend · Code
- Nodes: 1
- Examples: es.js

### 136. Backend · Code
- Nodes: 1
- Examples: et.js

### 137. Backend · Code
- Nodes: 1
- Examples: eu.js

### 138. Backend · Code
- Nodes: 1
- Examples: fa.js

### 139. Backend · Code
- Nodes: 1
- Examples: fi.js

### 140. Backend · Code
- Nodes: 1
- Examples: fr.js

### 141. Backend · Code
- Nodes: 1
- Examples: gl.js

### 142. Backend · Code
- Nodes: 1
- Examples: he.js

### 143. Backend · Code
- Nodes: 1
- Examples: hi.js

### 144. Backend · Code
- Nodes: 1
- Examples: hsb.js

### 145. Backend · Code
- Nodes: 1
- Examples: hu.js

### 146. Backend · Code
- Nodes: 1
- Examples: hy.js

### 147. Backend · Code
- Nodes: 1
- Examples: id.js

### 148. Backend · Code
- Nodes: 1
- Examples: is.js

### 149. Backend · Code
- Nodes: 1
- Examples: it.js

### 150. Backend · Code
- Nodes: 1
- Examples: ja.js

### 151. Backend · Code
- Nodes: 1
- Examples: ka.js

### 152. Backend · Code
- Nodes: 1
- Examples: km.js

### 153. Backend · Code
- Nodes: 1
- Examples: ko.js

### 154. Backend · Code
- Nodes: 1
- Examples: mk.js

### 155. Backend · Code
- Nodes: 1
- Examples: ms.js

### 156. Backend · Code
- Nodes: 1
- Examples: nb.js

### 157. Backend · Code
- Nodes: 1
- Examples: ne.js

### 158. Backend · Code
- Nodes: 1
- Examples: nl.js

### 159. Backend · Code
- Nodes: 1
- Examples: pl.js

### 160. Backend · Code
- Nodes: 1
- Examples: ps.js

### 161. Backend · Code
- Nodes: 1
- Examples: pt.js

### 162. Backend · Code
- Nodes: 1
- Examples: pt-BR.js

### 163. Backend · Code
- Nodes: 1
- Examples: ro.js

### 164. Backend · Code
- Nodes: 1
- Examples: sk.js

### 165. Backend · Code
- Nodes: 1
- Examples: sl.js

### 166. Backend · Code
- Nodes: 1
- Examples: sq.js

### 167. Backend · Code
- Nodes: 1
- Examples: sv.js

### 168. Backend · Code
- Nodes: 1
- Examples: th.js

### 169. Backend · Code
- Nodes: 1
- Examples: tk.js

### 170. Backend · Code
- Nodes: 1
- Examples: tr.js

### 171. Backend · Code
- Nodes: 1
- Examples: vi.js

### 172. Backend · Code
- Nodes: 1
- Examples: zh-CN.js

### 173. Backend · Code
- Nodes: 1
- Examples: zh-TW.js

### 174. Backend · Code
- Nodes: 1
- Examples: default.js

### 175. Backend · Code
- Nodes: 1
- Examples: load-ajax-form.js

### 176. Frontend · Code
- Nodes: 1
- Examples: index.ts

### 177. Frontend · Code
- Nodes: 1
- Examples: index.ts

### 178. Frontend · Code
- Nodes: 1
- Examples: index.ts

### 179. Frontend · Code
- Nodes: 1
- Examples: ProgressBar.tsx

### 180. Frontend · Code
- Nodes: 1
- Examples: Skeleton.tsx

### 181. Frontend · Code
- Nodes: 1
- Examples: Spinner.tsx

### 182. Frontend · Code
- Nodes: 1
- Examples: vite-env.d.ts

### 183. Frontend · Code
- Nodes: 1
- Examples: vite.config.d.ts

### 184. Backend · Documentation
- Nodes: 1
- Examples: LICENSE-SELECT2.md

### 185. Backend · Documentation
- Nodes: 1
- Examples: LICENSE.txt

### 186. Backend · Documentation
- Nodes: 1
- Examples: LICENSE.md

### 187. Backend · Documentation
- Nodes: 1
- Examples: LICENSE.txt
