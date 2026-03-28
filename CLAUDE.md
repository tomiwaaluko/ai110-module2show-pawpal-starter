# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Streamlit UI
streamlit run app.py

# Run CLI demo
python main.py

# Run all tests
pytest tests/

# Run a single test
pytest tests/test_pawpal.py::test_function_name -v
```

## Architecture

This project is a two-layer system:

**Backend (`pawpal_system.py`)** — pure Python, no Streamlit imports. Contains four classes:
- `Task` (dataclass): `description`, `time` (HH:MM str), `frequency` (once/daily/weekly), `completed` (bool), `due_date` (date)
- `Pet` (dataclass): `name`, `species`, `tasks` (list[Task])
- `Owner` (dataclass): `name`, `pets` (list[Pet])
- `Scheduler`: wraps an `Owner`; all scheduling logic lives here

**Scheduler methods** (the algorithmic core):
- `get_all_tasks()` → flat list of `(pet_name, task)` tuples
- `sort_by_time()` → tasks sorted by HH:MM string (lexicographic = chronological)
- `filter_tasks(pet_name=None, completed=None)` → filtered subset
- `detect_conflicts()` → list of warning strings for exact same-time collisions (O(n²))
- `mark_task_complete(pet_name, task_description)` → sets `completed=True`, appends a new recurring task with `timedelta(days=1)` or `timedelta(weeks=1)`
- `get_today_schedule()` → calls `sort_by_time()` + `detect_conflicts()` for display

**UI (`app.py`)** — Streamlit frontend. Imports from `pawpal_system`. Session state is initialized with:
```python
if 'owner' not in st.session_state:
    st.session_state.owner = Owner("My Name")
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
```

**CLI (`main.py`)** — standalone demo script, no UI dependency. Exercises the backend directly.

**Tests (`tests/test_pawpal.py`)** — pytest. Must cover at minimum: sorting, conflict detection, and recurrence generation.

## Key constraints

- `pawpal_system.py` must have zero Streamlit imports — keep layers clean.
- HH:MM string sort is intentional: `sorted(..., key=lambda t: t.time)` works because zero-padded time strings sort correctly without parsing.
- `detect_conflicts()` must never raise — always return a list (empty = no conflicts).
- Recurrence: only `daily` and `weekly` frequencies generate a follow-up task; `once` does not.
