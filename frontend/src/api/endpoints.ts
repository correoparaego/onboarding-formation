import client from "./client";

export interface CourseSectionPayload {
  id?: number;
  order: number;
  title: string;
  content: string;
  section_base: number;
  has_pdf?: boolean;
}

export interface CourseVersionPayload {
  id: number;
  number: number;
  title: string;
  min_time_divisor: number;
  status: string;
  sections: CourseSectionPayload[];
}

export const healthApi = {
  check: () => client.get<{ status: string; service: string }>("/health/"),
};

export const authApi = {
  login: (payload: { username: string; password: string }) =>
    client.post<{ ok: boolean; user: { username: string } }>("/auth/admin/login", payload),
  logout: () => client.post("/auth/admin/logout"),
  redeem: (payload: { token: string }) =>
    client.post<{ ok: boolean; employee: { id: number; name: string } }>(
      "/auth/employee/redeem",
      payload
    ),
  status: () =>
    client.get<{ admin: { username: string } | null; employee: { id: number; name: string } | null }>(
      "/auth/status"
    ),
};

export const importApi = {
  // POST /api/import  (Phase 4)
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return client.post("/import", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export const coursesApi = {
    list: () => client.get<{ courses: Array<{ id: number; title: string }> }>("/courses/"),
  create: (payload: {
    title: string;
    min_time_divisor?: number;
    position_ids?: number[];
    sections?: CourseSectionPayload[];
  }) =>
    client.post("/courses/", payload),
  detail: (id: number) =>
    client.get<{
      id: number;
      title: string;
      min_time_divisor: number;
      positions: Array<{ id: number; name: string }>;
      active_version: CourseVersionPayload | null;
      editing_version: CourseVersionPayload | null;
      sections: CourseSectionPayload[];
      banks: Array<{
        id: number;
        questions: Array<{ text: string; options: string[]; correct_index: number }>;
      }>;
    }>(`/courses/${id}/`),
  delete: (id: number) => client.delete(`/courses/${id}/`),
  createDraft: (id: number) =>
    client.post<{ version: CourseVersionPayload }>(`/courses/${id}/draft/`),
  updateVersion: (
    id: number,
    payload: {
      title: string;
      min_time_divisor: number;
      position_ids: number[];
      sections: CourseSectionPayload[];
    }
  ) => client.patch<{ version: CourseVersionPayload }>(`/course-versions/${id}/`, payload),
  publishVersion: (id: number) =>
    client.post<{ version: CourseVersionPayload }>(`/course-versions/${id}/publish/`),
  uploadSectionPdf: (sectionId: number, file: File) => {
    const form = new FormData();
    form.append("pdf", file);
    return client.post(`/sections/${sectionId}/pdf/`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deleteSectionPdf: (sectionId: number) => client.delete(`/sections/${sectionId}/pdf/`),
  positions: () => client.get<{ positions: Array<{ id: number; name: string }> }>("/positions/"),
  catalog: (position: string) =>
    client.get("/courses/catalog/", { params: { position } }),
};

export const banksApi = {
  // POST /api/banks/  (Phase 5) — single-correct enforced server-side
  create: (payload: {
    course_id: number;
    questions: Array<{ text: string; options: string[]; correct_index: number }>;
  }) => client.post("/banks/", payload),
};

export interface EmployeeSummary {
  id: number;
  name: string;
  position: string;
  current_position: { id: number; name: string } | null;
  email: string;
}

export const employeesApi = {
  list: () =>
    client.get<{ count: number; results: EmployeeSummary[] }>("/employees", {
      params: { limit: 200, offset: 0 },
    }),
  updatePosition: (employeeId: number, positionId: number) =>
    client.patch(`/employees/${employeeId}`, { position_id: positionId }),
  bulkPosition: (employeeIds: number[], positionId: number) =>
    client.post("/employees/bulk-position", {
      employee_ids: employeeIds,
      position_id: positionId,
    }),
};

export interface AssignmentSelection {
  course_ids: number[];
  employee_ids?: number[];
  position_ids?: number[];
  include_ids?: number[];
  exclude_ids?: number[];
}

export interface AdminEnrollment {
  id: number;
  employee_id: number;
  employee_name: string;
  course_id: number;
  course_title: string;
  version: number | null;
  cycle: number;
  status: string;
  active_seconds: number;
}

export const assignmentsApi = {
  preview: (payload: AssignmentSelection) =>
    client.post<{
      employees: Array<{ id: number; name: string; position: string }>;
      courses: Array<{ id: number; title: string }>;
      new_assignments: number;
      existing_assignments: number;
    }>("/admin/assignments/preview", payload),
  apply: (payload: AssignmentSelection) =>
    client.post<{ created: number; enrollment_ids: number[] }>("/admin/assignments", payload),
  enrollments: () =>
    client.get<{ enrollments: AdminEnrollment[] }>("/admin/enrollments"),
  action: (enrollmentId: number, action: "pause" | "resume" | "cancel" | "repeat") =>
    client.post(`/admin/enrollments/${enrollmentId}/${action}`),
};

export const aiApi = {
  // POST /api/ai/key  (Phase 6) — set/update encrypted BYO key (raw never returned)
  setKey: (payload: { provider: string; base_url: string; model: string; api_key: string }) =>
    client.post("/ai/key", payload),
  // GET /api/ai/key/status  (Phase 6)
  keyStatus: () =>
    client.get<{ has_key: boolean; status: string | null; provider?: string; model?: string }>(
      "/ai/key/status"
    ),
  // POST /api/ai/generate-content  (Phase 6) — guided draft, NOT persisted
  generateContent: (payload: {
    course_title: string;
    answers: Record<string, string>;
    reference_docs?: string[];
  }) => client.post("/ai/generate-content", payload),
  // POST /api/ai/generate-tests  (Phase 6) — PDF -> test draft, NOT persisted
  generateTests: (form: FormData) =>
    client.post("/ai/generate-tests", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  generateTestsText: (payload: { pdf_text: string }) =>
    client.post("/ai/generate-tests", payload),
};
