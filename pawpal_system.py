"""PawPal+ backend — all scheduling logic lives here. No Streamlit imports."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str  # "HH:MM" — 24-hour format
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    priority: str = "medium"  # "high" | "medium" | "low"  (Extension 3)

    def mark_complete(self) -> Optional["Task"]:
        """Mark task complete; return next recurrence Task if recurring, else None."""
        ...


@dataclass
class Pet:
    """Represents a pet with a list of care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        ...

    def task_count(self) -> int:
        """Return the number of tasks for this pet."""
        ...


class Owner:
    """Manages a roster of pets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        ...

    def get_pets(self) -> list[Pet]:
        """Return all pets owned."""
        ...

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Serialize owner, pets, and tasks to a JSON file. (Extension 2)"""
        ...

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load owner, pets, and tasks from a JSON file. (Extension 2)"""
        ...


class Scheduler:
    """Algorithmic brain: sorting, filtering, conflict detection, recurrence."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return flat list of (pet_name, task) tuples across all pets."""
        ...

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted chronologically by HH:MM string."""
        ...

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name and/or completion status."""
        ...

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for every pair of tasks sharing the same time slot."""
        ...

    def mark_task_complete(self, pet_name: str, task_description: str) -> None:
        """Mark a task complete and append its next recurrence to the pet's list."""
        ...

    def get_today_schedule(self) -> list[tuple[str, Task]]:
        """Return today's schedule sorted by time; print conflict warnings."""
        ...

    def find_next_available_slot(
        self, pet_name: str, duration_minutes: int = 30
    ) -> str:
        """Find first 30-min slot from 07:00–21:00 with no existing task. (Extension 1)"""
        ...

    def sort_by_priority_then_time(self) -> list[tuple[str, Task]]:
        """Sort tasks by priority (high first) then by time. (Extension 3)"""
        ...
