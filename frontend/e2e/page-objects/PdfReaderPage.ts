import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class PdfReaderPage extends BasePage {
  async goto(enrollmentId: number) {
    await this.page.goto(`/employee/read?enrollment=${enrollmentId}`);
    await this.waitForLoad();
  }

  async isLocked(): Promise<boolean> {
    return await this.getByTestId('locked-overlay').isVisible();
  }

  async waitForUnlock(timeout = 20000) {
    await this.page.waitForFunction(
      () => !document.querySelector('[data-testid="locked-overlay"]'),
      { timeout }
    );
  }

  async getTimerText(): Promise<string> {
    return (await this.getByTestId('reading-timer').textContent()) || '';
  }

  async navigateSection(direction: 'next' | 'prev') {
    const text = direction === 'next' ? 'Siguiente' : 'Anterior';
    await this.getByTestId('section-nav-btn').filter({ hasText: text }).click();
    await this.page.waitForTimeout(500);
  }
}
