"""The schedule generator: the core logic of the app.

Approach (simple on purpose, so it's easy to follow):
  1. FILTER  - for each course, throw away sections that break a hard rule
               (too early, too late, on a day the student wants free,
               or overlapping a custom event like practice).
  2. SEARCH  - try every combination of the remaining sections
               (backtracking), skipping any combo where two classes overlap.
  3. RANK    - score each valid schedule against the student's goal and
               return the best few.

With 4-6 courses x 2-4 sections that's at most a few thousand combinations,
which is instant. A real university catalog could need a constraint solver
such as Google OR-Tools; that's a research question for the team.
"""

from app.models import (
    DAYS,
    Course,
    GenerateRequest,
    GenerateResponse,
    Goal,
    Schedule,
    ScheduleStats,
    Section,
    to_minutes,
)

MAX_COMBINATIONS = 200_000  # safety valve so a huge request can't hang the server


def _fmt(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def section_allowed(section: Section, req: GenerateRequest) -> str | None:
    """Return None if the section is OK, otherwise a short reason it was rejected."""
    if req.earliest_start and section.start_min < to_minutes(req.earliest_start):
        return f"starts before {req.earliest_start}"
    if req.latest_end and section.end_min > to_minutes(req.latest_end):
        return f"ends after {req.latest_end}"
    blocked_days = set(section.days) & set(req.free_days)
    if blocked_days:
        return f"meets on {', '.join(sorted(blocked_days, key=DAYS.index))} (kept free)"
    for event in req.events:
        if section.overlaps(event):
            return f"overlaps {event.label}"
    return None


def compute_stats(sections: list[Section]) -> ScheduleStats:
    days_used = {d for s in sections for d in s.days}
    gap_total = 0
    for day in DAYS:
        todays = sorted((s for s in sections if day in s.days), key=lambda s: s.start_min)
        for earlier, later in zip(todays, todays[1:]):
            gap_total += max(0, later.start_min - earlier.end_min)
    class_minutes = sum((s.end_min - s.start_min) * len(s.days) for s in sections)
    return ScheduleStats(
        days_on_campus=len(days_used),
        free_days=[d for d in DAYS if d not in days_used],
        class_hours_per_week=round(class_minutes / 60, 2),
        total_gap_minutes=gap_total,
        earliest_start=_fmt(min(s.start_min for s in sections)),
        total_credits=sum(s.credits for s in sections),
    )


def score(stats: ScheduleStats, goal: Goal) -> float:
    """Lower is better. The main goal dominates; the other numbers break ties."""
    days = stats.days_on_campus
    gaps = stats.total_gap_minutes
    start = to_minutes(stats.earliest_start)
    if goal is Goal.fewest_days:
        return days * 1000 + gaps
    if goal is Goal.compact:
        return gaps * 10 + days * 100
    # late_start: a later first class is better, so subtract it
    return -start * 10 + days * 100 + gaps


def generate(req: GenerateRequest, catalog: dict[str, Course]) -> GenerateResponse:
    warnings: list[str] = []

    # --- 1. FILTER -------------------------------------------------------
    candidates: list[list[Section]] = []
    for code in dict.fromkeys(req.course_codes):  # dedupe, keep order
        course = catalog[code]
        allowed = []
        for section in course.sections:
            reason = section_allowed(section, req)
            if reason is None:
                allowed.append(section)
        if not allowed:
            warnings.append(f"{code}: every section breaks one of your rules, so no schedule can include it.")
            return GenerateResponse(schedules=[], combinations_checked=0, warnings=warnings)
        candidates.append(allowed)

    # Try courses with the fewest options first: prunes dead ends sooner.
    candidates.sort(key=len)

    # --- 2. SEARCH (backtracking) ----------------------------------------
    found: list[list[Section]] = []
    checked = 0

    def backtrack(index: int, chosen: list[Section]) -> None:
        nonlocal checked
        if checked >= MAX_COMBINATIONS:
            return
        if index == len(candidates):
            found.append(list(chosen))
            return
        for section in candidates[index]:
            checked += 1
            if any(section.overlaps(other) for other in chosen):
                continue  # time conflict, skip this branch
            chosen.append(section)
            backtrack(index + 1, chosen)
            chosen.pop()

    backtrack(0, [])

    if checked >= MAX_COMBINATIONS:
        warnings.append("Stopped early: too many combinations. Results may not be the very best.")
    if not found:
        warnings.append("Every combination of these courses has a time conflict. Try removing a course or loosening a rule.")

    # --- 3. RANK -----------------------------------------------------------
    scored = []
    for sections in found:
        stats = compute_stats(sections)
        scored.append((score(stats, req.goal), sections, stats))
    scored.sort(key=lambda item: item[0])

    schedules = [
        Schedule(
            rank=i + 1,
            score=s,
            sections=sorted(sections, key=lambda x: (DAYS.index(x.days[0]), x.start_min)),
            stats=stats,
        )
        for i, (s, sections, stats) in enumerate(scored[: req.max_results])
    ]
    return GenerateResponse(schedules=schedules, combinations_checked=checked, warnings=warnings)
