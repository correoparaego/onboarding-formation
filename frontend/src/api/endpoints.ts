// Typed API surface. Endpoints are filled in by later phases; this scaffold
// defines the shape so admin/employee components can be wired incrementally.
import client from "./client";

export const healthApi = {
  check: () => client.get<{ status: string; service: string }>("/health/"),
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
