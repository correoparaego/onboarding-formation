import { test, expect } from '@playwright/test';

/**
 * End-to-end happy path for the MVP onboarding flow:
 *   admin imports employees -> employee reads the course (timed gate)
 *   -> passes the comprehension test -> admin issues the certificate
 *   -> the append-only audit trail records every step.
 *
 * This spec is SKIPPED unless RUN_E2E=1 (and a reachable backend + built
 * SPA). It is intentionally non-fatal so local/dev builds without browsers
 * stay green. Selectors below use data-testid hooks; align them with the
 * actual components in src/admin/* and src/employee/* when enabling E2E.
 */
const RUN_E2E = process.env.RUN_E2E === '1';

test.describe('onboarding happy path (import -> read -> test -> cert)', () => {
  test.beforeAll(async ({ request }) => {
    if (!RUN_E2E) {
      test.skip(true, 'RUN_E2E not set — skipping Playwright E2E');
    }
    // Smoke-check the backend is up; skip gracefully if not.
    try {
      const health = await request.get('/api/health/');
      if (!health.ok()) test.skip(true, 'backend /api/health not healthy');
    } catch {
      test.skip(true, 'backend unreachable');
    }
  });

  test('admin imports an employee, employee reads + passes, cert is issued', async ({
    page,
  }) => {
    // 1) Admin login.
    await page.goto('/admin/login');
    await page.getByTestId('admin-username').fill('admin');
    await page.getByTestId('admin-password').fill('pw');
    await page.getByTestId('admin-login-submit').click();

    // 2) Import employees via the Excel upload.
    await page.goto('/admin/import');
    const xlsx = 'e2e/fixtures/employees.xlsx'; // build or commit a sample
    await page.getByTestId('import-file').setInputFiles(xlsx);
    await page.getByTestId('import-submit').click();
    await expect(page.getByTestId('import-created')).toContainText('1');

    // 3) Employee redeems the magic-link/code (here we drive the token UI).
    //    The magic link is emailed on import; in E2E we surface it via the
    //    console transport or a test fixture. Then read the timed PDF.
    await page.goto('/empleado/lectura');
    await page.getByTestId('reader-start').click();
    // Heartbeats advance the gate; complete every section.
    for (let i = 1; i <= 2; i++) {
      await page.getByTestId(`section-${i}-heartbeat`).click();
      await expect(page.getByTestId(`section-${i}-complete`)).toBeVisible();
    }

    // 4) Take the comprehension test and answer correctly.
    await page.goto('/empleado/test');
    await expect(page.getByTestId('test-questions')).toBeVisible();
    const options = page.getByTestId('question-option-correct');
    const count = await options.count();
    for (let i = 0; i < count; i++) {
      await options.nth(i).click();
    }
    await page.getByTestId('test-submit').click();
    await expect(page.getByTestId('test-result')).toContainText('apto');

    // 5) Admin issues the certificate PDF.
    await page.goto('/admin/expediente');
    await page.getByTestId('issue-certificate').first().click();
    const download = await page.waitForEvent('download');
    expect(download.suggestedFilename()).toContain('certificado');

    // 6) Audit trail records the issuance (append-only, read-only API).
    const audit = await page.request.get('/api/audit?event_type=certificate_issued');
    const auditBody = await audit.json();
    expect(auditBody.count).toBeGreaterThanOrEqual(1);
  });
});
