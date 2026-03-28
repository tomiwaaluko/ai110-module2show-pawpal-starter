# PawPal+ Project Reflection

## 1. System Design

**Three core user actions:**
1. Add a pet to their profile with name and species
2. Schedule a task (feeding, walk, medication, appointment) for a specific pet at a specific time
3. View today's full schedule across all pets, sorted by time with conflict warnings

**a. Initial Design**

The system uses four classes:
- `Task` (dataclass): Represents a single activity. Holds description, scheduled time (HH:MM string), frequency (once/daily/weekly), completion status, and due date. Uses dataclass for clean attribute declaration and default values.
- `Pet` (dataclass): Stores a pet's name and species, plus a list of Task objects. Responsible for adding tasks and reporting its task count.
- `Owner`: Manages a list of Pet objects. Provides methods to add pets and retrieve all pets for the Scheduler to consume.
- `Scheduler`: The system's brain. Holds a reference to an Owner and provides all algorithmic logic — sorting, filtering, conflict detection, task completion with recurrence, and schedule retrieval.

The key design choice was making `Scheduler` the sole algorithmic layer. Owner and Pet are pure data containers. This means UI code only needs to talk to Scheduler — it never traverses pet lists directly.

**b. Design changes based on review:**

One refinement was the return value of `mark_complete()`. The initial skeleton had it return `None` always. After implementation, returning a new `Task` object for recurring tasks (rather than mutating state internally) keeps the method pure and makes the Scheduler responsible for deciding where to put the new task. This is cleaner separation of concerns. Also added `tabulate` formatting to `main.py` for readable CLI output instead of raw print statements.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: time (HH:MM of when a task must occur), frequency (once/daily/weekly, which drives recurrence), and priority (high/medium/low, which determines display order when multiple tasks exist). Time was treated as the primary constraint because pet care tasks are often time-sensitive — a medication at 08:00 cannot be freely moved. Priority was added as a secondary sort key so high-importance tasks surface first when two tasks share a close time window.

**b. Tradeoffs**

The main tradeoff is exact-time conflict detection over duration-based overlap detection. The scheduler flags tasks at the exact same HH:MM as conflicts but does not model task duration — a 60-minute walk at 09:00 and a 10-minute feeding at 09:30 would not be flagged even though they overlap in reality. This is a reasonable simplification for a daily planning tool: it keeps conflict detection O(n²) and simple to understand, and real-world pet owners typically schedule tasks at clean intervals. Modeling duration would require interval overlap logic and a notion of "duration" on each task, which was intentionally deferred to a future iteration.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used at three stages: (1) design brainstorming — generating the initial class structure and deciding which methods belong on Scheduler vs. Pet, (2) implementation — generating method bodies from docstring-level specs, and (3) debugging — diagnosing test failures and adjusting return types (e.g., `mark_complete()` returning `Optional[Task]` instead of `None`). The most useful prompts were specific and included type signatures: "Given this dataclass, implement mark_complete() such that it returns the next Task if recurring or None if once."

**b. Judgment and verification**

One AI suggestion not accepted as-is: the initial `detect_conflicts()` implementation used a dict keyed by time to bucket tasks, which is O(n) but produces different output ordering than the O(n²) pairwise loop. The O(n²) approach was chosen instead because the warning messages needed to reference both tasks by name and time, which the bucketing approach made awkward. The AI's suggestion was functionally correct but optimized for performance over readability — a wrong tradeoff for a course project where clarity matters more than scale.

---

## 4. Testing and Verification

**a. What you tested**

Nine behaviors were tested: task completion status change, daily recurrence creates next-day task, one-time tasks do not recur, adding tasks increments pet task count, sorting returns chronological order, conflict detection flags duplicate times, no false positives when times are unique, filter by completion status works, and mark_task_complete appends recurrence to correct pet. These tests matter because they cover every algorithmic guarantee the system makes — sorting, filtering, conflict detection, and recurrence are the four core algorithms.

**b. Confidence**

Confidence level: ⭐⭐⭐⭐☆ — all core logic paths are covered by tests. Untested edge cases include: empty owner (no pets), owner with a pet that has no tasks, weekly recurrence crossing a month boundary, and tasks with identical descriptions on different pets.

---

## 5. Reflection

**a. What went well**

The clean layer separation — Task/Pet/Owner as data containers, Scheduler as the algorithmic layer — made testing easy. Each unit test could construct a minimal fixture and test exactly one behavior without fighting Streamlit session state or UI concerns.

**b. What you would improve**

The time field is a plain string ("HH:MM") rather than a `datetime.time` object. This was intentional to keep sort simple (string sort works for zero-padded times), but it means validation is entirely absent — nothing stops a user from entering "25:99" and breaking sort order silently. A future iteration would use `datetime.time` for the field and serialize to string only for display.

**c. Key takeaway**

Designing the system on paper first — even as a simple four-class sketch — prevented the most common refactoring trap: adding algorithmic logic to Pet or Owner when it belongs in Scheduler. The UML forced the question "whose responsibility is this?" before writing a single line of code, which saved time during implementation.

---

## Prompt Comparison: Claude vs Copilot

**Task**: Generate the `mark_task_complete` recurrence logic in `Scheduler`.

**Prompt used**: "Given a Scheduler class that holds an Owner with Pets and Tasks, implement mark_task_complete(pet_name, task_description) such that completing a daily or weekly task automatically creates the next occurrence and adds it to the pet's task list."

**Copilot (GPT-4o via VS Code)**:
Copilot generated a working solution but used a nested for-loop approach with an explicit break, and stored recurrence as a separate list on the Scheduler rather than appending to the Pet. This created a separation of concern issue — the Scheduler was holding state that the Pet should own.

**Claude (Sonnet)**:
Claude generated the same recurrence logic but kept it on Task.mark_complete() as a pure function returning a new Task, with the Scheduler responsible only for finding the task and routing the result. This is more modular: Task knows how to clone itself for recurrence, Scheduler knows where to put the clone.

**Verdict**: Claude's version was more "Pythonic" in the sense that it respected single responsibility more cleanly. Copilot's version was slightly more readable at first glance (fewer hops to follow), but would have caused maintenance issues when adding persistence — you'd have to serialize two separate collections instead of one.
