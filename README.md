# Schedule Generator — Research Milestone

Individual research prototype for our capstone (**MLRT**, a class-schedule optimizer for students).
It tries out the stack I'm proposing to the team, **FastAPI (Python) + React (Vite + TypeScript)**, by building a small version of our core feature: the **Schedule Generator**.

## What the app does

1. **Pick courses** from a sample catalog. You can search by code or title.
2. **Set preferences:**
   - no classes before or after a given time
   - days to keep free
   - recurring blocked times (practice, lunch, work)
   - what to optimize for: fewest days on campus, back-to-back classes, or the latest start
3. **Generate.** The backend finds every conflict-free combination of sections that follows your rules, ranks them, and returns the best options.
4. **Compare options.** Each one shows on a weekly calendar with stats: days on campus, free days, class hours per week, gap time, first class and credits.

This maps to several of our user stories:

| Persona | User story covered |
|---|---|
| Greg | See total hours in class per week; filter by start and end time |
| Sophie | Auto-optimize; prefer back-to-back classes |
| Micah | Optimize for fewest days on campus; see which days are fully free |
| Paris | Block a recurring window (3–5 p.m. practice) and full days |
| George | Block a lunch slot |

> Course data is **made up** (`backend/app/sample_data.py`), not the real USC schedule.

## Run it

You need [uv](https://docs.astral.sh/uv/) (Python package manager) and Node 20+ (npm).

**Backend** (terminal 1):

```bash
cd backend
uv sync                          # creates .venv and installs FastAPI + pytest from pyproject.toml / uv.lock
uv run fastapi dev app/main.py   # http://127.0.0.1:8000
```

Interactive API docs are at http://127.0.0.1:8000/docs. FastAPI generates them from the code.

**Frontend** (terminal 2):

```bash
cd frontend
npm install     # installs from package.json, writes package-lock.json
npm run dev     # http://localhost:5173
```

Vite forwards `/api/*` requests to the backend, so both must be running.

**Tests:**

```bash
cd backend && uv run pytest
```

## How it's built

```
backend/
  app/models.py       Pydantic models: request/response shapes + validation
  app/sample_data.py  Hand-made course sections
  app/scheduler.py    Core logic: filter -> backtracking search -> rank
  app/main.py         FastAPI routes (/api/courses, /api/schedules/generate)
  tests/              pytest: overlap logic, constraints, ranking, API
frontend/
  src/api.ts          fetch wrappers for the backend
  src/types.ts        TypeScript mirrors of the Pydantic models
  src/App.tsx         page state
  src/components/     CoursePicker, PreferencesForm, ScheduleResults, WeekGrid
```

**Algorithm:**
1. Drop every section that breaks a hard rule.
2. Backtrack through the remaining sections, skipping any combination with a time overlap. Courses with the fewest sections are tried first.
3. Score each valid schedule for the chosen goal. Lower is better.

This is fast for a handful of courses. A full catalog may need a constraint solver (see below).

## Research notes

### Backend: Python web frameworks

| | FastAPI | Django | Flask |
|---|---|---|---|
| Style | API-first, async | Full-stack, "batteries included" | Minimal microframework |
| Validation | Built in (Pydantic type hints) | Forms / DRF serializers | Add-on libraries |
| API docs | Auto-generated at `/docs` | Needs DRF + extra packages | Add-on |
| Auth / admin | Add a library (e.g. fastapi-users) | Built in | Add-ons |
| ORM / database | Bring your own (SQLAlchemy / SQLModel) | Built-in ORM + migrations | Bring your own |
| Best fit | JSON API for a separate frontend | Server-rendered apps, admin-heavy apps | Small apps, full control |

**Takeaway:** for a React frontend that talks to an API, FastAPI needs the least boilerplate, and the type hints double as validation and documentation. Django would win if we wanted server-rendered pages plus a free admin panel and auth.

### Frontend

- **React + Vite:**
  - Biggest ecosystem and very fast dev server.
  - Components map cleanly onto our Mockitt screens (course card, schedule grid, preference form).
  - The Generator's interactive calendar is a natural fit.
- **Django templates / plain HTML:**
  - One language and simpler deployment.
  - Interactive pieces like the calendar would need hand-written JavaScript.
- **Next.js:**
  - Adds server rendering and routing.
  - Probably more than we need, since our backend is already Python.

### Package managers

- **uv (Python):**
  - `pyproject.toml` declares the dependencies, and `uv.lock` pins exact versions so every teammate gets the same install.
  - `uv run` runs commands inside the project's `.venv` without activating it.
  - Much faster than pip.
- **npm (JavaScript):**
  - `package.json` declares the dependencies, and `package-lock.json` pins exact versions.
  - `node_modules/` is never committed.
- **Rule for the team:** commit both lockfiles. When something "works on my machine," run `uv sync` / `npm install` first.

### Open questions for the team

- **Scheduling engine:**
  - Brute-force backtracking (this prototype) is simple and fine for about 6 courses.
  - Google OR-Tools CP-SAT handles big catalogs and "soft" preferences. Worth prototyping next.
- **Course data source:** scrape USC class search, import a CSV, or keep a hand-made dataset early on?
- **Database:**
  - PostgreSQL for production, SQLite locally.
  - Access it through SQLAlchemy or SQLModel (made by FastAPI's author).
- **Login:** email/password, e.g. fastapi-users or Supabase Auth. Real university SSO likely needs IT approval.
- **Deployment:** Render or Railway for the API, Vercel or Netlify for the React build.
