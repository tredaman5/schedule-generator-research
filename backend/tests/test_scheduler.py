"""Tests for the scheduling logic and the API.

Run with:  uv run pytest
"""

from fastapi.testclient import TestClient

from app.main import app
from app.models import CustomEvent, GenerateRequest, Goal, Section
from app.sample_data import load_courses
from app.scheduler import compute_stats, generate

CATALOG = load_courses()
client = TestClient(app)


def make_section(days, start, end, code="TEST 100"):
    return Section(
        course_code=code, title="Test", section="001", credits=3,
        days=days, start=start, end=end, instructor="X", room="Y",
    )


def no_conflicts(sections):
    return not any(a.overlaps(b) for i, a in enumerate(sections) for b in sections[i + 1:])


# --- overlap logic -----------------------------------------------------------

def test_overlap_same_day_same_time():
    assert make_section(["Mon"], "09:00", "10:00").overlaps(make_section(["Mon"], "09:30", "10:30"))


def test_back_to_back_is_not_an_overlap():
    assert not make_section(["Mon"], "09:00", "10:00").overlaps(make_section(["Mon"], "10:00", "11:00"))


def test_different_days_never_overlap():
    assert not make_section(["Mon"], "09:00", "10:00").overlaps(make_section(["Tue"], "09:00", "10:00"))


# --- generator ---------------------------------------------------------------

def test_every_generated_schedule_is_conflict_free():
    req = GenerateRequest(course_codes=["CSCE 146", "CSCE 211", "CSCE 240", "CSCE 247"], max_results=20)
    result = generate(req, CATALOG)
    assert result.schedules
    for schedule in result.schedules:
        assert no_conflicts(schedule.sections)
        assert len(schedule.sections) == 4


def test_free_days_are_respected():
    req = GenerateRequest(course_codes=["CSCE 240", "CSCE 247", "SPCH 140"], free_days=["Fri"], max_results=20)
    for schedule in generate(req, CATALOG).schedules:
        assert all("Fri" not in s.days for s in schedule.sections)
        assert "Fri" in schedule.stats.free_days


def test_earliest_start_is_respected():
    req = GenerateRequest(course_codes=["CSCE 146", "CSCE 211"], earliest_start="10:00", max_results=20)
    for schedule in generate(req, CATALOG).schedules:
        assert all(s.start_min >= 600 for s in schedule.sections)


def test_custom_event_blocks_time():
    practice = CustomEvent(label="Practice", days=["Mon", "Tue", "Wed", "Thu", "Fri"], start="15:00", end="17:00")
    req = GenerateRequest(course_codes=["CSCE 211", "CSCE 240"], events=[practice], max_results=20)
    result = generate(req, CATALOG)
    assert result.schedules
    for schedule in result.schedules:
        assert all(not s.overlaps(practice) for s in schedule.sections)


def test_impossible_request_returns_warning_not_error():
    # CSCE 247 only meets MWF or TTh; keeping all of those days free makes it impossible.
    req = GenerateRequest(course_codes=["CSCE 247"], free_days=["Mon", "Tue", "Wed", "Thu", "Fri"])
    result = generate(req, CATALOG)
    assert result.schedules == []
    assert result.warnings


def test_fewest_days_ranks_fewer_days_first():
    req = GenerateRequest(course_codes=["CSCE 211", "CSCE 240", "CSCE 247"], goal=Goal.fewest_days, max_results=20)
    days = [s.stats.days_on_campus for s in generate(req, CATALOG).schedules]
    assert days == sorted(days)


def test_stats_gap_and_hours():
    a = make_section(["Mon"], "09:00", "10:00", code="A 1")
    b = make_section(["Mon"], "11:00", "12:00", code="B 1")
    stats = compute_stats([a, b])
    assert stats.total_gap_minutes == 60
    assert stats.class_hours_per_week == 2
    assert stats.free_days == ["Tue", "Wed", "Thu", "Fri"]


# --- API ---------------------------------------------------------------------

def test_api_lists_courses():
    response = client.get("/api/courses")
    assert response.status_code == 200
    assert any(c["code"] == "CSCE 240" for c in response.json())


def test_api_generate():
    response = client.post("/api/schedules/generate", json={"course_codes": ["CSCE 240", "CSCE 247"]})
    assert response.status_code == 200
    assert response.json()["schedules"]


def test_api_unknown_course_is_404():
    response = client.post("/api/schedules/generate", json={"course_codes": ["FAKE 999"]})
    assert response.status_code == 404


def test_api_rejects_bad_time_format():
    response = client.post("/api/schedules/generate", json={"course_codes": ["CSCE 240"], "earliest_start": "9am"})
    assert response.status_code == 422
