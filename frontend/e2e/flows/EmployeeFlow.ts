import { Page } from '@playwright/test';
import {
  EmployeeRedeemPage,
  EmployeeDashboardPage,
  PdfReaderPage,
} from '../page-objects';

export class EmployeeFlow {
  private redeemPage: EmployeeRedeemPage;
  private dashboardPage: EmployeeDashboardPage;
  private readerPage: PdfReaderPage;

  constructor(private page: Page) {
    this.redeemPage = new EmployeeRedeemPage(page);
    this.dashboardPage = new EmployeeDashboardPage(page);
    this.readerPage = new PdfReaderPage(page);
  }

  async redeemToken(token: string) {
    await this.redeemPage.goto();
    await this.redeemPage.screenshot('employee/01-redeem-page');
    await this.redeemPage.redeemToken(token);
    await this.redeemPage.screenshot('employee/02-after-redeem');
  }

  async viewEnrollments(): Promise<number> {
    await this.dashboardPage.goto();
    await this.dashboardPage.screenshot('employee/03-dashboard');
    const count = await this.dashboardPage.getEnrollmentCount();
    if (count === 0) {
      await this.dashboardPage.screenshot('employee/03b-dashboard-empty');
      console.log('  Warning: No enrollment cards found on dashboard');
    }
    return count;
  }

  async startReading(): Promise<number> {
    const enrollmentId = await this.dashboardPage.clickFirstContinueReading();
    await this.readerPage.screenshot('employee/04-pdf-reader-start');
    return enrollmentId;
  }

  async waitForReadingProgress(timeout = 20000): Promise<string> {
    const wasLocked = await this.readerPage.isLocked();
    if (wasLocked) {
      await this.readerPage.waitForUnlock(timeout);
      await this.readerPage.screenshot('employee/05-pdf-reader-unlocked');
    }
    return await this.readerPage.getTimerText();
  }

  async navigateSections() {
    await this.readerPage.navigateSection('next');
    await this.readerPage.screenshot('employee/06-pdf-reader-next-section');
  }

  async completeFullFlow(token: string) {
    await this.redeemToken(token);
    const enrollmentCount = await this.viewEnrollments();
    
    if (enrollmentCount === 0) {
      console.log('  No enrollments to read — skipping reading steps');
      return { enrollmentCount, enrollmentId: null, timer: '' };
    }
    
    const enrollmentId = await this.startReading();
    const timer = await this.waitForReadingProgress();
    await this.navigateSections();

    return { enrollmentCount, enrollmentId, timer };
  }
}
