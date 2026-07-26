import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ImportPage extends BasePage {
  async goto() {
    await this.page.goto('/admin/import');
    await this.waitForLoad();
  }

  async uploadFile(filePath: string) {
    const fileInput = this.page.locator('input[type="file"]');
    await fileInput.waitFor({ state: 'attached', timeout: 10000 });
    await fileInput.setInputFiles(filePath);
    await this.page.waitForTimeout(500);
    const submitBtn = this.getByTestId('import-submit-btn');
    if (await submitBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await submitBtn.click();
    }
    await this.page.waitForTimeout(3000);
  }

  async expectSuccess() {
    await expect(this.getByTestId('import-result-stats')).toBeVisible();
  }

  async getStats(): Promise<string> {
    const el = this.getByTestId('import-result-stats');
    if (await el.isVisible({ timeout: 3000 }).catch(() => false)) {
      return (await el.textContent()) || '';
    }
    return '';
  }
}
