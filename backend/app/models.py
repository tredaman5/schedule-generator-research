"""Pydantic models: the shapes of data going in and out of the API.

FastAPI uses these to validate request bodies and to generate the
interactive docs at /docs automatically.
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def to_minutes(hhmm: str) -> int:
    """'13:30' -> 810 (minutes after midnight). Makes time math easy."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


class TimeBlock(BaseModel):
    """Anything that occupies time on certain weekdays: a class section or a custom event."""

    days: list[str]
    start: str = Field(examples=["09:00"])
    end: str = Field(examples=["10:15"])

    @field_validator("days")
    @classmethod
    def check_days(cls, days: list[str]) -> list[str]:
        bad = [d for d in days if d not in DAYS]
        if bad:
            raise ValueError(f"Unknown day(s) {bad}. Use {DAYS}.")
        return days

    @field_validator("start", "end")
    @classmethod
    def check_time(cls, value: str) -> str:
        try:
            minutes = to_minutes(value)
        except ValueError as exc:
            raise ValueError("Times must look like HH:MM, e.g. 09:30") from exc
        if not 0 <= minutes < 24 * 60:
            raise ValueError("Time must be between 00:00 and 23:59")
        return value

    @property
    def start_min(self) -> int:
        return to_minutes(self.start)

    @property
    def end_min(self) -> int:
        return to_minutes(self.end)

    def overlaps(self, other: "TimeBlock") -> bool:
        """True if the two blocks share a day AND their times overlap."""
        shared_day = set(self.days) & set(other.days)
        return bool(shared_day) and self.start_min < other.end_min and other.start_min < self.end_min


class Section(TimeBlock):
    course_code: str
    title: str
    section: str
    credits: int
    instructor: str
    room: str


class Course(BaseModel):
    code: str
    title: str
    credits: int
    sections: list[Section]


class CustomEvent(TimeBlock):
    """A recurring commitment the schedule must avoid: practice, lunch, a work shift."""

    label: str = Field(examples=["Track practice"])


class Goal(str, Enum):
    fewest_days = "fewest_days"  # Micah: pack classes into as few days as possible
    compact = "compact"  # Sophie: back-to-back, minimal gaps between classes
    late_start = "late_start"  # start the day as late as possible


class GenerateRequest(BaseModel):
    course_codes: list[str] = Field(min_length=1, examples=[["CSCE 240", "CSCE 247"]])
    earliest_start: str | None = Field(default=None, examples=["10:00"])
    latest_end: str | None = Field(default=None, examples=["17:00"])
    free_days: list[str] = Field(default_factory=list, examples=[["Fri"]])
    events: list[CustomEvent] = Field(default_factory=list)
    goal: Goal = Goal.fewest_days
    lunch_break: bool = False
    max_results: int = Field(default=5, ge=1, le=20)

    @field_validator("earliest_start", "latest_end")
    @classmethod
    def check_optional_time(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        return TimeBlock.check_time(value)

    @field_validator("free_days")
    @classmethod
    def check_free_days(cls, days: list[str]) -> list[str]:
        return TimeBlock.check_days(days)


class ScheduleStats(BaseModel):
    days_on_campus: int
    free_days: list[str]
    class_hours_per_week: float
    total_gap_minutes: int
    earliest_start: str
    total_credits: int


class Schedule(BaseModel):
    rank: int
    score: float
    sections: list[Section]
    stats: ScheduleStats


class GenerateResponse(BaseModel):
    schedules: list[Schedule]
    combinations_checked: int
    warnings: list[str]
