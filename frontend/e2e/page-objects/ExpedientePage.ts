import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ExpedientePage extends BasePage {
  async goto() {
    await this.page.goto('/admin/expediente');
    await this.waitForLoad();
  }

  async search(query: string) {
    await this.getByTestId('expediente-search-input').fill(query);
    await this.page.waitForTimeout(500);
  }

  async getRowCount(): Promise<number> {
    return await this.getByTestId('expediente-table').locator('tbody tr').count();
  }

  async expectRowExists(employeeName: string) {
    await expect(this.page.getByText(employeeName, { exact: false })).toBeVisible();
  }
}
