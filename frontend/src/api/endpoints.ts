import client from "./client";

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
  create: (payload: { title: string; sections?: Array<{ order: number; section_base: number }> }) =>
    client.post("/courses/", payload),
  detail: (id: number) =>
    client.get<{
      id: number;
      title: string;
      min_time_divisor: number;
      positions: string[];
      sections: Array<{ order: number; section_base: number }>;
      banks: Array<{
        id: number;
        questions: Array<{ text: string; options: string[]; correct_index: number }>;
      }>;
    }>(`/courses/${id}/`),
  delete: (id: number) => client.delete(`/courses/${id}/`),
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
