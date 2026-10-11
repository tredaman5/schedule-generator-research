"""FastAPI app: the HTTP layer.

Run it with:   uv run fastapi dev app/main.py
Then open:     http://127.0.0.1:8000/docs   (auto-generated, try the endpoints there)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import Course, GenerateRequest, GenerateResponse
from app.sample_data import load_courses
from app.scheduler import generate

app = FastAPI(
    title="Schedule Generator API",
    description="Research prototype: generate conflict-free class schedules from a student's preferences.",
    version="0.1.0",
)

# The React dev server runs on a different port (5173), so the browser needs
# permission to call this API. In production you'd list your real domain here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG = load_courses()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/courses", response_model=list[Course])
def list_courses() -> list[Course]:
    """Every course in the catalog, with its sections."""
    return list(CATALOG.values())


@app.get("/api/courses/{code}", response_model=Course)
def get_course(code: str) -> Course:
    course = CATALOG.get(code.upper().replace("-", " "))
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    return course


@app.post("/api/schedules/generate", response_model=GenerateResponse)
def generate_schedules(req: GenerateRequest) -> GenerateResponse:
    """Build ranked, conflict-free schedules for the requested courses."""
    unknown = [c for c in req.course_codes if c not in CATALOG]
    if unknown:
        raise HTTPException(status_code=404, detail=f"Unknown course(s): {', '.join(unknown)}")
    return generate(req, CATALOG)
