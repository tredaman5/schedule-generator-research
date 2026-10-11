// All calls to the FastAPI backend live here, so components never deal with fetch directly.
import type { Course, GenerateRequest, GenerateResponse } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    // FastAPI puts error messages in a "detail" field.
    const body = await response.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export function fetchCourses(): Promise<Course[]> {
  return request<Course[]>("/api/courses");
}

export function generateSchedules(body: GenerateRequest): Promise<GenerateResponse> {
  return request<GenerateResponse>("/api/schedules/generate", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
