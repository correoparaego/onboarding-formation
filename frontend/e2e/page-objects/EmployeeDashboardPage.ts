import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class EmployeeDashboardPage extends BasePage {
  async goto() {
    await this.page.goto('/employee');
    await this.waitForLoad();
  }

  async getEnrollmentCount(): Promise<number> {
    await this.page.waitForTimeout(2000);
    return await this.page.locator('[data-testid^="enrollment-card-"]').count();
  }

  async getFirstEnrollmentId(): Promise<number | null> {
    const cards = this.page.locator('[data-testid^="enrollment-card-"]');
    const count = await cards.count();
    if (count === 0) return null;
    const testId = await cards.first().getAttribute('data-testid');
    if (!testId) return null;
    const match = testId.match(/enrollment-card-(\d+)/);
    return match ? parseInt(match[1], 10) : null;
  }

  async clickContinueReading(enrollmentId: number) {
    await this.getByTestId(`enrollment-card-${enrollmentId}`).getByTestId('continue-reading-btn').click();
    await this.page.waitForURL('**/employee/read**');
  }

  async clickFirstContinueReading() {
    const id = await this.getFirstEnrollmentId();
    if (id === null) throw new Error('No enrollment cards found');
    await this.clickContinueReading(id);
    return id;
  }

  async expectEmptyState() {
    await expect(this.getByTestId('empty-state')).toBeVisible();
  }
}
