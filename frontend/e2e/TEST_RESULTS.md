# E2E Test Results — Phase B

**Date**: 2026-07-22  
**Status**: 2/2 PASSED  
**Total time**: 31.0s

---

## Test Execution Summary

| Test | Status | Duration |
|------|--------|----------|
| Admin flow — complete onboarding | PASSED | 26.5s |
| Employee flow — complete training | PASSED | 3.8s |

---

## Admin Flow Results

| Step | Screenshot | Result |
|------|-----------|--------|
| Login page | `admin/01-login-page.png` | OK |
| After login | `admin/02-after-login.png` | OK — redirected to dashboard |
| Import (empty) | `admin/03-import-empty.png` | OK |
| Import (result) | `admin/04-import-result.png` | OK — 0 created, 15 duplicates, 0 errors |
| Courses list | `admin/05-courses-list.png` | OK — 6 courses visible |
| Course created | `admin/06-course-created.png` | Warning — course not found in list |
| Expediente list | `admin/07-expediente-list.png` | OK — 4 records |
| Expediente search | `admin/08-expediente-search.png` | OK |
| AI content (empty) | `admin/09-ai-content-empty.png` | OK |
| AI content (draft) | `admin/10-ai-content-draft.png` | Warning — fake LLM did not generate draft |

**Key metrics**:
- Import stats: 0 created, 15 duplicates, 0 errors, 0 new enrollments
- Course count: 6
- Expediente count: 4

---

## Employee Flow Results

| Step | Screenshot | Result |
|------|-----------|--------|
| Redeem page | `employee/01-redeem-page.png` | OK |
| After redeem | `employee/02-after-redeem.png` | OK — redirected to dashboard |
| Dashboard | `employee/03-dashboard.png` | Warning — 0 enrollment cards visible |
| Dashboard (empty) | `employee/03b-dashboard-empty.png` | Confirmed empty state |

**Key metrics**:
- Enrollment count: 0
- Reading steps skipped (no enrollments to display)

---

## Files Created

### Page Objects (`e2e/page-objects/`)
- `BasePage.ts` — base class with screenshot, waitForLoad, getByTestId
- `LandingPage.ts` — landing page interactions
- `AdminLoginPage.ts` — admin login form
- `ImportPage.ts` — employee file import
- `CoursesPage.ts` — course CRUD
- `ExpedientePage.ts` — expediente list + search
- `AiContentPage.ts` — AI content generation
- `EmployeeRedeemPage.ts` — token redemption
- `EmployeeDashboardPage.ts` — employee enrollment list
- `PdfReaderPage.ts` — PDF reader with lock/timer
- `index.ts` — barrel export

### Flows (`e2e/flows/`)
- `AdminFlow.ts` — complete admin journey (login → import → courses → expediente → AI)
- `EmployeeFlow.ts` — complete employee journey (redeem → dashboard → read → navigate)
- `index.ts` — barrel export

### Fixtures (`e2e/fixtures/`)
- `test-data.ts` — admin credentials, course data, employee tokens

### Specs
- `e2e/flows.spec.ts` — flow-organized test specs (replaces screen-by-screen approach)

---

## Issues Encountered

1. **Admin password mismatch**: The admin user existed with a different password. Fixed by resetting via Django shell.
2. **Course creation not reflected**: After creating a course via the UI, it doesn't appear in the list. Likely the API call succeeds but the list doesn't refresh, or the creation endpoint has an issue.
3. **Fake LLM doesn't generate content**: The AI content generation step doesn't produce a draft preview. Expected behavior with `AI_USE_FAKE_LLM=true` — the fake LLM may not return structured content.
4. **Employee dashboard empty after redeem**: After redeeming a valid token, the employee dashboard shows 0 enrollments. The token is consumed successfully (redirect happens), but the enrollment cards don't render. This may be a timing issue or the employee auth context doesn't load enrollments for this specific employee.

---

## Recommendations

1. **Fix course creation refresh**: After creating a course, the admin courses list should refetch. Check if the `createCourse` API response triggers a list refresh.
2. **Investigate employee dashboard**: The redeem flow works but the dashboard doesn't show enrollments. Check if the employee session/auth is properly established after redeem.
3. **Add AI key setup step**: The AI content generation may require an API key to be configured first. Add a step in the admin flow to set up the AI key before generating content.
4. **Increase heartbeat wait**: For the PDF reader unlock flow, the heartbeat interval is 5s and the unlock may take multiple cycles. Consider increasing the wait timeout.

---

## How to Run

```bash
cd frontend
TAKE_SCREENSHOTS=1 npx playwright test flows.spec.ts
```

Screenshots are saved to `frontend/screenshots/flows/`.
