import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class EmployeeRedeemPage extends BasePage {
  async goto() {
    await this.page.goto('/employee/redeem');
    await this.waitForLoad();
  }

  async redeemToken(token: string) {
    await this.getByTestId('token-input').fill(token);
    await this.getByTestId('redeem-submit-btn').click();
    await this.page.waitForURL('**/employee**', { timeout: 10000 });
  }

  async expectError(message: string) {
    await expect(this.getByTestId('redeem-error-msg')).toContainText(message);
  }
}
