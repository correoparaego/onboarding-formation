import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class AdminLoginPage extends BasePage {
  async goto() {
    await this.page.goto('/admin/login');
    await this.waitForLoad();
  }

  async login(username: string, password: string) {
    await this.getByTestId('username-input').fill(username);
    await this.getByTestId('password-input').fill(password);
    await this.getByTestId('login-submit-btn').click();
    await this.page.waitForURL('**/admin/dashboard**', { timeout: 10000 }).catch(() =>
      this.page.waitForURL((url) => url.pathname !== '/admin/login' && url.pathname.startsWith('/admin'), { timeout: 10000 })
    );
    await this.page.waitForTimeout(500);
  }

  async expectError(message: string) {
    await expect(this.getByTestId('login-error-msg')).toContainText(message);
  }
}
