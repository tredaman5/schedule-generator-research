import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server forwards any request starting with /api to the FastAPI
// backend on port 8000, so the React code can just call fetch("/api/...").
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
