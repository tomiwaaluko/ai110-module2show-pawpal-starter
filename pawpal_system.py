"""PawPal+ backend — all scheduling logic lives here. No Streamlit imports."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import json


@dataclass
class Task:
    """Represents a single pet care activity with time, frequency, and priority."""

    description: str
    time: str  # "HH:MM" — 24-hour format
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    priority: str = "medium"  # "high" | "medium" | "low"  (Extension 3)

    def mark_complete(self) -> Optional["Task"]:
        """Mark task complete; return next recurrence Task if recurring, else None."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                self.description,
                self.time,
                self.frequency,
                False,
                self.due_date + timedelta(days=1),
                self.priority,
            )
        elif self.frequency == "weekly":
            return Task(
                self.description,
                self.time,
                self.frequency,
                False,
                self.due_date + timedelta(weeks=1),
                self.priority,
            )
        return None


@dataclass
class Pet:
    """Represents a pet with a list of care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the number of tasks for this pet."""
        return len(self.tasks)


class Owner:
    """Manages a roster of pets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets owned."""
        return self.pets

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Serialize owner, pets, and tasks to a JSON file. (Extension 2)"""
        data = {
            "name": self.name,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [
                        {
                            "description": task.description,
                            "time": task.time,
                            "frequency": task.frequency,
                            "completed": task.completed,
                            "due_date": task.due_date.isoformat(),
                            "priority": task.priority,
                        }
                        for task in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load owner, pets, and tasks from a JSON file. (Extension 2)"""
        with open(filepath, "r") as f:
            data = json.load(f)
        owner = cls(data["name"])
        for pet_data in data["pets"]:
            pet = Pet(pet_data["name"], pet_data["species"])
            for t in pet_data["tasks"]:
                task = Task(
                    description=t["description"],
                    time=t["time"],
                    frequency=t["frequency"],
                    completed=t["completed"],
                    due_date=date.fromisoformat(t["due_date"]),
                    priority=t.get("priority", "medium"),
                )
                pet.add_task(task)
            owner.add_pet(pet)
        return owner


class Scheduler:
    """Algorithmic brain: sorting, filtering, conflict detection, recurrence."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Return flat list of (pet_name, task) tuples across all pets."""
        result = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return all tasks sorted chronologically by HH:MM string."""
        return sorted(self.get_all_tasks(), key=lambda x: x[1].time)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name and/or completion status."""
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [(n, t) for n, t in tasks if n == pet_name]
        if completed is not None:
            tasks = [(n, t) for n, t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for every pair of tasks sharing the same time slot."""
        warnings = []
        all_tasks = self.get_all_tasks()
        for i in range(len(all_tasks)):
            for j in range(i + 1, len(all_tasks)):
                pet1, task1 = all_tasks[i]
                pet2, task2 = all_tasks[j]
                if task1.time == task2.time:
                    warnings.append(
                        f"⚠ CONFLICT: {pet1} '{task1.description}' and "
                        f"{pet2} '{task2.description}' both scheduled at {task1.time}"
                    )
        return warnings

    def mark_task_complete(self, pet_name: str, task_description: str) -> None:
        """Mark a task complete and append its next recurrence to the pet's list."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.description == task_description and not task.completed:
                        next_task = task.mark_complete()
                        if next_task is not None:
                            pet.add_task(next_task)
                        return

    def get_today_schedule(self) -> list[tuple[str, Task]]:
        """Return today's schedule sorted by time; print conflict warnings."""
        conflicts = self.detect_conflicts()
        for warning in conflicts:
            print(warning)
        return self.sort_by_time()

    def find_next_available_slot(
        self, pet_name: str, duration_minutes: int = 30
    ) -> str:
        """Find first 30-min slot from 07:00–21:00 with no existing task. (Extension 1)"""
        occupied = {task.time for _, task in self.get_all_tasks()}
        hour, minute = 7, 0
        while hour < 21:
            slot = f"{hour:02d}:{minute:02d}"
            if slot not in occupied:
                return slot
            minute += 30
            if minute >= 60:
                minute = 0
                hour += 1
        return "No available slot found today"

    def sort_by_priority_then_time(self) -> list[tuple[str, Task]]:
        """Sort tasks by priority (high first) then by time. (Extension 3)"""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            self.get_all_tasks(),
            key=lambda x: (priority_order.get(x[1].priority, 1), x[1].time),
        )
