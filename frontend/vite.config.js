import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Frontend SPA (static host). API base URL is injected at build/runtime via env.
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            // Convenience for local dev: forward /api to the Django dev server.
            "/api": {
                target: process.env.VITE_API_TARGET || "http://localhost:8000",
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: "dist",
    },
});
