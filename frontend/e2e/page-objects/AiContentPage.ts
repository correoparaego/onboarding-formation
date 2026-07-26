import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class AiContentPage extends BasePage {
  async goto() {
    await this.page.goto('/admin/ai/content');
    await this.waitForLoad();
  }

  async generateContent(title: string) {
    await this.getByTestId('course-title-input').fill(title);
    await this.getByTestId('generate-btn').click();
    await this.page.waitForTimeout(5000);
  }

  async expectDraftPreview(): Promise<boolean> {
    return await this.getByTestId('draft-preview').isVisible({ timeout: 5000 }).catch(() => false);
  }

  async saveCourse() {
    await this.getByTestId('save-course-btn').click();
    await this.page.waitForTimeout(2000);
  }
}
