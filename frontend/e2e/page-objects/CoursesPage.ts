import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class CoursesPage extends BasePage {
  async goto() {
    await this.page.goto('/admin/courses');
    await this.waitForLoad();
  }

  async createCourse(title: string) {
    await this.getByTestId('create-course-btn').click();
    await this.getByTestId('course-title-input').fill(title);
    await this.getByTestId('course-submit-btn').click();
    await this.page.waitForTimeout(2000);
  }

  async deleteCourse(courseId: number) {
    await this.getByTestId(`course-row-${courseId}`).getByTestId('delete-course-btn').click();
    await this.getByTestId('confirm-btn').click();
    await this.page.waitForTimeout(1000);
  }

  async expectCourseExists(title: string) {
    await this.page.waitForTimeout(1000);
    const found = await this.page.getByText(title, { exact: false }).first().isVisible({ timeout: 5000 }).catch(() => false);
    return found;
  }

  async getCourseCount(): Promise<number> {
    return await this.getByTestId('courses-table').locator('tbody tr').count();
  }
}
