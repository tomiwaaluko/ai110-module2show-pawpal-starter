# PawPal+ SKILL — Shared Agent Context

## Project
PawPal+ is a smart pet care management system for AI110 @ CodePath.
Due: Monday March 30 2:59AM EDT.

## File Map
- `pawpal_system.py` — all backend classes (logic layer)
- `app.py` — Streamlit UI (provided as starter)
- `main.py` — CLI demo/testing script
- `tests/test_pawpal.py` — pytest suite
- `README.md` — professional documentation
- `reflection.md` — structured reflection
- `uml_final.png` — final UML diagram export

## Core Classes (Python dataclasses where applicable)
- `Task`: description, time (HH:MM str), frequency (once/daily/weekly), completed (bool), due_date (date)
- `Pet`: name, species, tasks (list[Task])
- `Owner`: name, pets (list[Pet])
- `Scheduler`: owner (Owner) — the "brain"

## Scheduler Required Methods
- `get_all_tasks()` → flat list of (pet_name, task) tuples
- `sort_by_time()` → sorted task list by HH:MM
- `filter_tasks(pet_name=None, completed=None)` → filtered list
- `detect_conflicts()` → list of warning strings for same-time tasks
- `mark_task_complete(pet_name, task_description)` → marks task, auto-generates next recurrence
- `get_today_schedule()` → sorted, conflict-checked schedule for display

## Algorithmic Requirements
- Sort: `sorted(tasks, key=lambda t: t.time)` — HH:MM string sort works chronologically
- Conflict: O(n²) exact time match check — returns warning strings, never crashes
- Recurrence: `timedelta(days=1)` for daily, `timedelta(weeks=1)` for weekly
- Filter: by pet name AND/OR completion status

## Streamlit State Pattern
```python
if 'owner' not in st.session_state:
    st.session_state.owner = Owner("My Name")
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
```

## Commit Convention
- `chore:` setup/skeleton
- `feat:` new functionality
- `test:` test suite work
- `docs:` README/reflection/docstrings
- `fix:` bug fixes

## Agent Roles (for this session)
- DESIGN AGENT: UML, class skeletons, reflection section 1a/1b
- BACKEND AGENT: full pawpal_system.py implementation + main.py demo
- TEST AGENT: tests/test_pawpal.py with pytest
- UI AGENT: app.py wiring + Streamlit polish
- DOCS AGENT: README.md, reflection.md, uml_final generation

## Grading Phases Checklist
- [ ] Phase 1: UML + class skeletons committed
- [ ] Phase 2: Full implementation + CLI demo passing
- [ ] Phase 3: app.py wired to pawpal_system.py
- [ ] Phase 4: sorting, filtering, conflict detection, recurrence
- [ ] Phase 5: pytest suite passing (3+ test cases)
- [ ] Phase 6: UI polished, README finalized, reflection complete
- [ ] Extension 1: Advanced algorithm (next available slot or priority)
- [ ] Extension 2: JSON persistence (save/load)
- [ ] Extension 3: Priority-based scheduling + UI color coding
- [ ] Extension 4: tabulate CLI formatting
- [ ] Extension 5: reflection.md Prompt Comparison section
