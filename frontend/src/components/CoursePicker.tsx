import { useState } from "react";
import type { Course } from "../types";

interface Props {
  courses: Course[];
  selected: string[];
  onToggle: (code: string) => void;
}

export default function CoursePicker({ courses, selected, onToggle }: Props) {
  const [query, setQuery] = useState("");

  const q = query.trim().toLowerCase();
  const visible = courses.filter(
    (c) => c.code.toLowerCase().includes(q) || c.title.toLowerCase().includes(q),
  );

  return (
    <div className="card">
      <h2>1. Pick courses</h2>
      <input
        className="search"
        placeholder="Search by code or title, e.g. CSCE 2"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <ul className="course-list">
        {visible.map((course) => {
          const isOn = selected.includes(course.code);
          return (
            <li key={course.code}>
              <label className={`course-row ${isOn ? "on" : ""}`}>
                <input type="checkbox" checked={isOn} onChange={() => onToggle(course.code)} />
                <span className="course-code">{course.code}</span>
                <span className="course-title">{course.title}</span>
                <span className="muted">{course.sections.length} sec · {course.credits} cr</span>
              </label>
            </li>
          );
        })}
        {visible.length === 0 && <li className="muted">No courses match "{query}".</li>}
      </ul>
    </div>
  );
}
