import { useState } from "react";
import { DAYS, type CustomEvent, type Day, type Goal } from "../types";

export interface Preferences {
  earliestStart: string; // "" means no limit
  latestEnd: string;
  freeDays: Day[];
  events: CustomEvent[];
  goal: Goal;
  lunchBreak: boolean;
}

interface Props {
  prefs: Preferences;
  onChange: (prefs: Preferences) => void;
}

const GOALS: { value: Goal; label: string }[] = [
  { value: "fewest_days", label: "Fewest days on campus" },
  { value: "compact", label: "Back-to-back (least gap time)" },
  { value: "late_start", label: "Latest start time" },
];

function toggleDay(days: Day[], day: Day): Day[] {
  return days.includes(day) ? days.filter((d) => d !== day) : [...days, day];
}

export default function PreferencesForm({ prefs, onChange }: Props) {
  // Draft state for the "add event" mini-form.
  const [label, setLabel] = useState("");
  const [eventDays, setEventDays] = useState<Day[]>([]);
  const [start, setStart] = useState("12:00");
  const [end, setEnd] = useState("13:00");

  const update = (patch: Partial<Preferences>) => onChange({ ...prefs, ...patch });

  const eventValid = label.trim() !== "" && eventDays.length > 0 && start < end;

  function addEvent() {
    if (!eventValid) return;
    update({ events: [...prefs.events, { label: label.trim(), days: eventDays, start, end }] });
    setLabel("");
    setEventDays([]);
  }

  return (
    <div className="card">
      <h2>2. Set your preferences</h2>

      <div className="row">
        <label className="field">
          <span>No classes before</span>
          <input type="time" value={prefs.earliestStart} onChange={(e) => update({ earliestStart: e.target.value })} />
        </label>
        <label className="field">
          <span>No classes after</span>
          <input type="time" value={prefs.latestEnd} onChange={(e) => update({ latestEnd: e.target.value })} />
        </label>
      </div>

      <div className="field">
        <span>Keep these days free</span>
        <div className="chips">
          {DAYS.map((day) => (
            <button
              key={day}
              type="button"
              className={`chip ${prefs.freeDays.includes(day) ? "on" : ""}`}
              onClick={() => update({ freeDays: toggleDay(prefs.freeDays, day) })}
            >
              {day}
            </button>
          ))}
        </div>
      </div>

      <label className="field">
        <span>Optimize for</span>
        <select value={prefs.goal} onChange={(e) => update({ goal: e.target.value as Goal })}>
          {GOALS.map((g) => (
            <option key={g.value} value={g.value}>{g.label}</option>
          ))}
        </select>
      </label>

      <label className="field" style={{ flexDirection: "row", alignItems: "center" }}>
        <input
          type="checkbox"
          checked={prefs.lunchBreak}
          onChange={(e) => update({ lunchBreak: e.target.checked })}
        />
        <span>Keep a 45-min lunch break (11:00-14:00)</span>
      </label>

      <div className="field">
        <span>Blocked times (practice, lunch, work...)</span>
        <div className="event-form">
          <input placeholder="Label, e.g. Track practice" value={label} onChange={(e) => setLabel(e.target.value)} />
          <div className="chips small">
            {DAYS.map((day) => (
              <button
                key={day}
                type="button"
                className={`chip ${eventDays.includes(day) ? "on" : ""}`}
                onClick={() => setEventDays(toggleDay(eventDays, day))}
              >
                {day}
              </button>
            ))}
          </div>
          <div className="row">
            <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
            <input type="time" value={end} onChange={(e) => setEnd(e.target.value)} />
            <button type="button" className="btn outline" onClick={addEvent} disabled={!eventValid}>
              Add
            </button>
          </div>
        </div>
        <ul className="event-list">
          {prefs.events.map((ev, i) => (
            <li key={`${ev.label}-${i}`}>
              <span>
                <strong>{ev.label}</strong> · {ev.days.join("/")} {ev.start}-{ev.end}
              </span>
              <button
                type="button"
                className="remove"
                aria-label={`Remove ${ev.label}`}
                onClick={() => update({ events: prefs.events.filter((_, j) => j !== i) })}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
