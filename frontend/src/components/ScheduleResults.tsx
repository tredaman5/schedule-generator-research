import { useEffect, useState } from "react";
import { DAYS, type CustomEvent, type GenerateResponse } from "../types";
import WeekGrid from "./WeekGrid";

interface Props {
  result: GenerateResponse | null;
  events: CustomEvent[];
}

export default function ScheduleResults({ result, events }: Props) {
  const [active, setActive] = useState(0);

  // Jump back to option 1 whenever a new result arrives.
  useEffect(() => setActive(0), [result]);

  if (!result) {
    return (
      <div className="empty">
        <h2>Your schedules will show up here</h2>
        <p className="muted">Pick a few courses, set your preferences, and hit Generate.</p>
      </div>
    );
  }

  if (result.schedules.length === 0) {
    return (
      <div className="empty">
        <h2>No schedule fits all your rules</h2>
        {result.warnings.map((w) => (
          <p key={w} className="warning">{w}</p>
        ))}
      </div>
    );
  }

  const schedule = result.schedules[Math.min(active, result.schedules.length - 1)];
  const { stats } = schedule;

  return (
    <div>
      <div className="results-head">
        <h2>Schedule options</h2>
        <span className="muted">{result.combinations_checked} combinations checked</span>
      </div>

      <div className="tabs">
        {result.schedules.map((s, i) => (
          <button key={s.rank} className={`tab ${i === active ? "on" : ""}`} onClick={() => setActive(i)}>
            Option {s.rank}
          </button>
        ))}
      </div>

      <div className="stats">
        <Stat label="Days on campus" value={stats.days_on_campus} />
        <Stat label="Class hours / week" value={stats.class_hours_per_week} />
        <Stat label="Gap time" value={`${stats.total_gap_minutes} min`} />
        <Stat label="First class" value={stats.earliest_start} />
        <Stat label="Credits" value={stats.total_credits} />
      </div>

      <div className="free-days">
        <span>Free days:</span>
        {DAYS.map((d) => (
          <span key={d} className={`day-pill ${stats.free_days.includes(d) ? "free" : ""}`}>{d}</span>
        ))}
      </div>

      {result.warnings.map((w) => (
        <p key={w} className="warning">{w}</p>
      ))}

      <WeekGrid sections={schedule.sections} events={events} />

      <table className="section-table">
        <thead>
          <tr><th>Course</th><th>Sec</th><th>Days</th><th>Time</th><th>Instructor</th><th>Room</th></tr>
        </thead>
        <tbody>
          {schedule.sections.map((s) => (
            <tr key={`${s.course_code}-${s.section}`}>
              <td><strong>{s.course_code}</strong> {s.title}</td>
              <td>{s.section}</td>
              <td>{s.days.join("/")}</td>
              <td>{s.start}-{s.end}</td>
              <td>{s.instructor}</td>
              <td>{s.room}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}
