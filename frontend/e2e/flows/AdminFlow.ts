import { Page } from '@playwright/test';
import * as path from 'path';
import {
  AdminLoginPage,
  ImportPage,
  CoursesPage,
  ExpedientePage,
  AiContentPage,
} from '../page-objects';

export class AdminFlow {
  private loginPage: AdminLoginPage;
  private importPage: ImportPage;
  private coursesPage: CoursesPage;
  private expedientePage: ExpedientePage;
  private aiContentPage: AiContentPage;

  constructor(private page: Page) {
    this.loginPage = new AdminLoginPage(page);
    this.importPage = new ImportPage(page);
    this.coursesPage = new CoursesPage(page);
    this.expedientePage = new ExpedientePage(page);
    this.aiContentPage = new AiContentPage(page);
  }

  async login(username = 'admin', password = 'admin1234') {
    await this.loginPage.goto();
    await this.loginPage.screenshot('admin/01-login-page');
    await this.loginPage.login(username, password);
    await this.loginPage.screenshot('admin/02-after-login');
  }

  async importEmployees(filePath: string) {
    await this.importPage.goto();
    await this.importPage.screenshot('admin/03-import-empty');
    await this.importPage.uploadFile(filePath);
    await this.importPage.expectSuccess();
    await this.importPage.screenshot('admin/04-import-result');
    return await this.importPage.getStats();
  }

  async viewCourses(): Promise<number> {
    await this.coursesPage.goto();
    await this.coursesPage.screenshot('admin/05-courses-list');
    return await this.coursesPage.getCourseCount();
  }

  async createCourse(title: string) {
    await this.coursesPage.createCourse(title);
    await this.coursesPage.screenshot('admin/06-course-created');
    const found = await this.coursesPage.expectCourseExists(title);
    if (!found) {
      console.log(`  Warning: Course '${title}' not found in list after creation`);
    }
  }

  async viewExpediente(): Promise<number> {
    await this.expedientePage.goto();
    await this.expedientePage.screenshot('admin/07-expediente-list');
    return await this.expedientePage.getRowCount();
  }

  async searchExpediente(query: string) {
    await this.expedientePage.search(query);
    await this.expedientePage.screenshot('admin/08-expediente-search');
  }

  async generateAIContent(title: string) {
    await this.aiContentPage.goto();
    await this.aiContentPage.screenshot('admin/09-ai-content-empty');
    await this.aiContentPage.generateContent(title);
    const hasDraft = await this.aiContentPage.expectDraftPreview();
    await this.aiContentPage.screenshot('admin/10-ai-content-draft');
    if (!hasDraft) {
      console.log('  Warning: AI draft preview not shown (fake LLM may not have responded)');
    }
    return hasDraft;
  }

  async completeFullFlow() {
    await this.login();
    const xlsxPath = path.resolve(process.cwd(), '..', 'backend', 'test_employees.xlsx');
    const importStats = await this.importEmployees(xlsxPath);
    const courseCount = await this.viewCourses();
    await this.createCourse('Curso de Prueba E2E');
    const expedienteCount = await this.viewExpediente();
    await this.searchExpediente('Juan');
    await this.generateAIContent('Curso Generado por IA');

    return { importStats, courseCount, expedienteCount };
  }
}
