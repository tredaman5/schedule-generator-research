"""Hand-made sample course sections.

These are realistic-looking but made up. They are NOT the real USC schedule.
The real app would load sections from a database (and eventually from the
university's class search) instead of this list.
"""

from app.models import Course, Section

MWF = ["Mon", "Wed", "Fri"]
TTH = ["Tue", "Thu"]
MW = ["Mon", "Wed"]


def _section(code, title, credits, section, days, start, end, instructor, room):
    return Section(
        course_code=code,
        title=title,
        credits=credits,
        section=section,
        days=days,
        start=start,
        end=end,
        instructor=instructor,
        room=room,
    )


_RAW = [
    # code, title, credits, [(section, days, start, end, instructor, room), ...]
    ("CSCE 146", "Algorithmic Design II", 4, [
        ("001", MWF, "08:30", "09:20", "Prof. Shephard", "SWGN 2A15"),
        ("002", MWF, "11:40", "12:30", "Prof. Shephard", "SWGN 2A15"),
        ("003", TTH, "13:15", "14:30", "Prof. Rose", "SWGN 2A27"),
    ]),
    ("CSCE 211", "Digital Logic Design", 3, [
        ("001", MWF, "10:50", "11:40", "Prof. Bakos", "SWGN 2A21"),
        ("002", TTH, "08:30", "09:45", "Prof. Bakos", "SWGN 2A21"),
        ("003", TTH, "14:50", "16:05", "Prof. Ali", "SWGN 2A11"),
    ]),
    ("CSCE 215", "UNIX/Linux Fundamentals", 1, [
        ("001", ["Mon"], "14:20", "15:10", "Prof. Lewis", "SWGN 1D11"),
        ("002", ["Wed"], "16:25", "17:15", "Prof. Lewis", "SWGN 1D11"),
        ("003", ["Thu"], "10:05", "10:55", "Prof. Lewis", "SWGN 1D11"),
    ]),
    ("CSCE 240", "Advanced Programming Techniques", 3, [
        ("001", MWF, "09:40", "10:30", "Prof. Lewis", "SWGN 2A31"),
        ("002", TTH, "11:40", "12:55", "Prof. Vidal", "SWGN 2A31"),
        ("003", MW, "15:30", "16:45", "Prof. Vidal", "SWGN 2A31"),
    ]),
    ("CSCE 247", "Software Engineering", 3, [
        ("001", TTH, "10:05", "11:20", "Prof. Bhandari", "SWGN 2A05"),
        ("002", MWF, "13:10", "14:00", "Prof. Bhandari", "SWGN 2A05"),
    ]),
    ("CSCE 311", "Operating Systems", 3, [
        ("001", TTH, "08:30", "09:45", "Prof. Huang", "SWGN 2A19"),
        ("002", MW, "13:10", "14:25", "Prof. Huang", "SWGN 2A19"),
    ]),
    ("CSCE 350", "Data Structures and Algorithms", 3, [
        ("001", MWF, "12:00", "12:50", "Prof. Buell", "SWGN 2A25"),
        ("002", TTH, "16:25", "17:40", "Prof. Buell", "SWGN 2A25"),
    ]),
    ("SPCH 140", "Public Communication", 3, [
        ("001", TTH, "10:05", "11:20", "Prof. Cates", "LC 320"),
        ("002", MWF, "10:50", "11:40", "Prof. Cates", "LC 320"),
        ("003", ["Wed"], "18:00", "20:45", "Prof. Mims", "LC 210"),
    ]),
]


def load_courses() -> dict[str, Course]:
    """Return {course_code: Course} for every sample course."""
    courses: dict[str, Course] = {}
    for code, title, credits, sections in _RAW:
        courses[code] = Course(
            code=code,
            title=title,
            credits=credits,
            sections=[_section(code, title, credits, *s) for s in sections],
        )
    return courses
