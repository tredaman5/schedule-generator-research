// TypeScript mirrors of the backend's Pydantic models (backend/app/models.py).
// If you change a model on the backend, update it here too.

export const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"] as const;
export type Day = (typeof DAYS)[number];

export interface Section {
  course_code: string;
  title: string;
  section: string;
  credits: number;
  days: Day[];
  start: string; // "HH:MM"
  end: string;
  instructor: string;
  room: string;
}

export interface Course {
  code: string;
  title: string;
  credits: number;
  sections: Section[];
}

export interface CustomEvent {
  label: string;
  days: Day[];
  start: string;
  end: string;
}

export type Goal = "fewest_days" | "compact" | "late_start";

export interface GenerateRequest {
  course_codes: string[];
  earliest_start: string | null;
  latest_end: string | null;
  free_days: Day[];
  events: CustomEvent[];
  goal: Goal;
  max_results: number;
}

export interface ScheduleStats {
  days_on_campus: number;
  free_days: Day[];
  class_hours_per_week: number;
  total_gap_minutes: number;
  earliest_start: string;
  total_credits: number;
}

export interface Schedule {
  rank: number;
  score: number;
  sections: Section[];
  stats: ScheduleStats;
}

export interface GenerateResponse {
  schedules: Schedule[];
  combinations_checked: number;
  warnings: string[];
}
