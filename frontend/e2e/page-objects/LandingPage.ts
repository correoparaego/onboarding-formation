import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class LandingPage extends BasePage {
  async goto() {
    await this.page.goto('/');
    await this.waitForLoad();
  }

  async clickAdminAccess() {
    await this.getByTestId('admin-access-link').click();
    await this.page.waitForURL('**/admin/**');
  }

  async clickEmployeeAccess() {
    await this.getByTestId('employee-access-link').click();
    await this.page.waitForURL('**/employee/**');
  }

  async expectVisible() {
    await expect(this.getByTestId('landing-page')).toBeVisible();
  }
}
