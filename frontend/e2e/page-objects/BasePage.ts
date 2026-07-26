import { Page, Locator } from '@playwright/test';

export class BasePage {
  constructor(protected page: Page) {}

  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async screenshot(name: string) {
    const path = `screenshots/flows/${name}.png`;
    await this.page.screenshot({ path, fullPage: false });
    console.log(`  Screenshot: ${path}`);
    return path;
  }

  getByTestId(testId: string): Locator {
    return this.page.getByTestId(testId);
  }
}
