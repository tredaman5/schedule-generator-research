import { useEffect, useState } from "react";
import { fetchCourses, generateSchedules } from "./api";
import CoursePicker from "./components/CoursePicker";
import PreferencesForm, { type Preferences } from "./components/PreferencesForm";
import ScheduleResults from "./components/ScheduleResults";
import type { Course, GenerateResponse } from "./types";

const DEFAULT_PREFS: Preferences = {
  earliestStart: "",
  latestEnd: "",
  freeDays: [],
  events: [],
  goal: "fewest_days",
};

export default function App() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [prefs, setPrefs] = useState<Preferences>(DEFAULT_PREFS);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load the course catalog once when the page opens.
  useEffect(() => {
    fetchCourses()
      .then(setCourses)
      .catch((e: Error) => setError(`Could not reach the API. Is the backend running? (${e.message})`));
  }, []);

  function toggleCourse(code: string) {
    setSelected((prev) => (prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]));
  }

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const response = await generateSchedules({
        course_codes: selected,
        earliest_start: prefs.earliestStart || null,
        latest_end: prefs.latestEnd || null,
        free_days: prefs.freeDays,
        events: prefs.events,
        goal: prefs.goal,
        max_results: 5,
      });
      setResult(response);
    } catch (e) {
      setError((e as Error).message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-name">Scheduling App</span>
          <span className="brand-tag">Plan - Schedule - Succeed</span>
        </div>
        <span className="badge">Research prototype</span>
      </header>

      <main className="layout">
        <aside className="panel left">
          <CoursePicker courses={courses} selected={selected} onToggle={toggleCourse} />
          <PreferencesForm prefs={prefs} onChange={setPrefs} />
          <button className="btn primary wide" onClick={handleGenerate} disabled={selected.length === 0 || loading}>
            {loading ? "Generating..." : `Generate schedules (${selected.length} course${selected.length === 1 ? "" : "s"})`}
          </button>
          {error && <p className="error">{error}</p>}
        </aside>

        <section className="panel right">
          <ScheduleResults result={result} events={prefs.events} />
        </section>
      </main>
    </div>
  );
}
