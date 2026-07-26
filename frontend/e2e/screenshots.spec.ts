import { test, expect, Page } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Screenshot capture spec for every key UI screen.
 *
 * OPT-IN: only runs when TAKE_SCREENSHOTS=1 is set.
 * Requires:
 *   - Backend running (python manage.py runserver)
 *   - Frontend dev server running (npm run dev)
 *   - Seed data loaded (python backend/seed_test_data.py)
 *
 * Screenshots are saved to frontend/screenshots/.
 */
const TAKE_SCREENSHOTS = process.env.TAKE_SCREENSHOTS === '1';
const SCREENSHOTS_DIR = path.resolve(process.cwd(), 'screenshots');
const EMPLOYEE_TEST_TOKEN = process.env.EMPLOYEE_TEST_TOKEN || '';

let screenshotIndex = 0;

async function takeScreenshot(page: Page, name: string) {
  screenshotIndex++;
  const padded = String(screenshotIndex).padStart(2, '0');
  const filePath = path.join(SCREENSHOTS_DIR, `${padded}-${name}.png`);
  await page.screenshot({ path: filePath, fullPage: false });
  console.log(`  Screenshot saved: ${filePath}`);
}

/** Reusable admin login helper — uses label-based selectors (Spanish UI). */
async function adminLogin(page: Page) {
  await page.goto('/admin/login');
  await page.waitForLoadState('networkidle');
  // Input IDs are auto-generated from Spanish labels: "Usuario" → "usuario", "Contraseña" → "contraseña"
  await page.getByLabel('Usuario').fill('admin');
  await page.getByLabel('Contraseña').fill('admin1234');
  await page.getByRole('button', { name: /iniciar sesión/i }).click();
  // Wait until we land on an admin page (dashboard, import, etc.)
  await page.waitForURL('**/admin/**', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(500);
}

test.describe('UI screenshot capture', () => {
  test.beforeAll(async () => {
    if (!TAKE_SCREENSHOTS) {
      test.skip(true, 'TAKE_SCREENSHOTS not set — skipping screenshot capture');
    }
    if (!fs.existsSync(SCREENSHOTS_DIR)) {
      fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    }
  });

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  test('01 — Landing page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await takeScreenshot(page, 'landing');
  });

  test('02 — Admin login page', async ({ page }) => {
    await page.goto('/admin/login');
    await page.waitForLoadState('networkidle');
    await takeScreenshot(page, 'admin-login');
  });

  test('03 — Admin import (empty state)', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/import');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-import-empty');
  });

  test('04 — Admin import (after upload)', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/import');
    await page.waitForLoadState('networkidle');

    const xlsxPath = path.resolve(process.cwd(), '..', 'backend', 'test_employees.xlsx');
    if (fs.existsSync(xlsxPath)) {
      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.isVisible()) {
        await fileInput.setInputFiles(xlsxPath);
        // Wait for auto-upload or click submit if needed
        const submitBtn = page.getByRole('button', { name: /importar|subir|cargar/i }).first();
        if (await submitBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
          await submitBtn.click();
        }
        await page.waitForTimeout(3000);
      }
    }
    await takeScreenshot(page, 'admin-import-result');
  });

  test('05 — Admin courses list', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/courses');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-courses-list');
  });

  test('06 — Admin course detail', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/courses');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Click on the first course row or clickable element
    const firstRow = page.locator('table tbody tr, [role="row"]').first();
    if (await firstRow.isVisible({ timeout: 3000 }).catch(() => false)) {
      await firstRow.click();
      await page.waitForTimeout(1500);
    }
    await takeScreenshot(page, 'admin-course-detail');
  });

  test('07 — Admin AI key form', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/ai/key');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-ai-key');
  });

  test('08 — Admin AI content wizard', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/ai/content');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-ai-content');
  });

  test('09 — Admin AI test generation', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/ai/tests');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-ai-tests');
  });

  test('10 — Admin expediente list', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/expediente');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'admin-expediente');
  });

  test('11 — Employee redeem page', async ({ page }) => {
    await page.goto('/employee/redeem');
    await page.waitForLoadState('networkidle');
    await takeScreenshot(page, 'employee-redeem');
  });

  test('12 — Employee mis cursos (with token)', async ({ page }) => {
    if (EMPLOYEE_TEST_TOKEN) {
      await page.goto('/employee/redeem');
      await page.waitForLoadState('networkidle');
      // Input ID is "codigo-de-acceso" from label "Código de acceso"
      await page.getByLabel(/código de acceso/i).fill(EMPLOYEE_TEST_TOKEN);
      await page.getByRole('button', { name: /acceder/i }).click();
      await page.waitForURL('**/employee**', { timeout: 10000 }).catch(() => {});
    } else {
      await page.goto('/employee');
      await page.waitForLoadState('networkidle');
    }
    await page.waitForTimeout(500);
    await takeScreenshot(page, 'employee-mis-cursos');
  });

  test('13 — PDF reader (locked state)', async ({ page }) => {
    if (EMPLOYEE_TEST_TOKEN) {
      await page.goto('/employee/redeem');
      await page.waitForLoadState('networkidle');
      await page.getByLabel(/código de acceso/i).fill(EMPLOYEE_TEST_TOKEN);
      await page.getByRole('button', { name: /acceder/i }).click();
      await page.waitForURL('**/employee**', { timeout: 10000 }).catch(() => {});
    }
    await page.goto('/employee/read?enrollment=1');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await takeScreenshot(page, 'pdf-reader-locked');
  });

  test('14 — PDF reader (after heartbeat progress)', async ({ page }) => {
    if (EMPLOYEE_TEST_TOKEN) {
      await page.goto('/employee/redeem');
      await page.waitForLoadState('networkidle');
      await page.getByLabel(/código de acceso/i).fill(EMPLOYEE_TEST_TOKEN);
      await page.getByRole('button', { name: /acceder/i }).click();
      await page.waitForURL('**/employee**', { timeout: 10000 }).catch(() => {});
    }
    await page.goto('/employee/read?enrollment=1');
    await page.waitForLoadState('networkidle');
    // Wait for heartbeat cycles to accumulate time
    await page.waitForTimeout(12000);
    await takeScreenshot(page, 'pdf-reader-progress');
  });
});
