import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';
import { AdminFlow, EmployeeFlow } from './flows';
import { TEST_DATA, getEmployeeToken } from './fixtures/test-data';

const TAKE_SCREENSHOTS = process.env.TAKE_SCREENSHOTS === '1';
const SCREENSHOTS_DIR = path.resolve(process.cwd(), 'screenshots', 'flows');

test.describe('Complete user flows', () => {
  test.beforeAll(() => {
    if (!TAKE_SCREENSHOTS) {
      test.skip(true, 'TAKE_SCREENSHOTS not set');
    }
    if (!fs.existsSync(SCREENSHOTS_DIR)) {
      fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    }
  });

  test.describe('Admin flow - complete onboarding', () => {
    test('should complete full admin workflow', async ({ page }) => {
      test.setTimeout(120000);
      await page.setViewportSize({ width: 1280, height: 800 });
      const adminFlow = new AdminFlow(page);

      const results = await adminFlow.completeFullFlow();

      console.log('\n=== Admin Flow Results ===');
      console.log(`Import stats: ${results.importStats}`);
      console.log(`Course count: ${results.courseCount}`);
      console.log(`Expediente count: ${results.expedienteCount}`);

      expect(results.courseCount).toBeGreaterThan(0);
    });
  });

  test.describe('Employee flow - complete training', () => {
    test('should complete full employee workflow', async ({ page }) => {
      const token = getEmployeeToken();
      test.skip(!token, 'EMPLOYEE_TEST_TOKEN not set - skipping employee flow');
      test.setTimeout(120000);

      await page.setViewportSize({ width: 1280, height: 800 });
      const employeeFlow = new EmployeeFlow(page);

      const results = await employeeFlow.completeFullFlow(token);

      console.log('\n=== Employee Flow Results ===');
      console.log(`Enrollment count: ${results.enrollmentCount}`);
      console.log(`Enrollment ID: ${results.enrollmentId}`);
      console.log(`Timer: ${results.timer}`);

      expect(results.enrollmentCount).toBeGreaterThanOrEqual(0);
    });
  });
});
