import { DAYS, type CustomEvent, type Section } from "../types";

// The grid shows 8:00 to 21:00. Each block is positioned by converting its
// start/end time into a percentage of that window.
const DAY_START = 8 * 60;
const DAY_END = 21 * 60;
const HOURS = Array.from({ length: (DAY_END - DAY_START) / 60 }, (_, i) => DAY_START / 60 + i);

function toMin(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

function position(start: string, end: string) {
  const span = DAY_END - DAY_START;
  const top = ((Math.max(toMin(start), DAY_START) - DAY_START) / span) * 100;
  const bottom = ((Math.min(toMin(end), DAY_END) - DAY_START) / span) * 100;
  return { top: `${top}%`, height: `${Math.max(bottom - top, 2)}%` };
}

function label12(hour: number): string {
  const suffix = hour >= 12 ? "pm" : "am";
  return `${((hour + 11) % 12) + 1}${suffix}`;
}

interface Props {
  sections: Section[];
  events: CustomEvent[];
}

export default function WeekGrid({ sections, events }: Props) {
  return (
    <div className="week">
      <div className="week-times">
        <div className="week-head" />
        <div className="week-body">
          {HOURS.map((h) => (
            <div key={h} className="hour-label">{label12(h)}</div>
          ))}
        </div>
      </div>

      {DAYS.map((day) => (
        <div key={day} className="week-col">
          <div className="week-head">{day}</div>
          <div className="week-body">
            {HOURS.map((h) => (
              <div key={h} className="hour-line" />
            ))}

            {events
              .filter((ev) => ev.days.includes(day))
              .map((ev) => (
                <div key={`${ev.label}-${ev.start}`} className="block event" style={position(ev.start, ev.end)}>
                  <span>{ev.label}</span>
                </div>
              ))}

            {sections
              .filter((s) => s.days.includes(day))
              .map((s) => (
                <div key={`${s.course_code}-${s.section}`} className="block class" style={position(s.start, s.end)}>
                  <strong>{s.course_code}</strong>
                  <span>{s.start}-{s.end}</span>
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
