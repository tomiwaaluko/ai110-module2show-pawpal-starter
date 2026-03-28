"""PawPal+ CLI demo -- exercises all backend features with formatted tabulate output."""

import sys
import io
from datetime import date
from tabulate import tabulate
from pawpal_system import Task, Pet, Owner, Scheduler

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def print_schedule(scheduler: Scheduler) -> None:
    """Print today's full schedule as a formatted table."""
    tasks = scheduler.sort_by_time()
    rows = [
        [
            pet_name,
            task.time,
            task.description,
            task.frequency,
            task.priority,
            "done" if task.completed else "todo",
            task.due_date.isoformat(),
        ]
        for pet_name, task in tasks
    ]
    print("\n+==========================================+")
    print("|           TODAY'S SCHEDULE               |")
    print("+==========================================+\n")
    print(
        tabulate(
            rows,
            headers=["Pet", "Time", "Task", "Freq", "Priority", "Status", "Due"],
            tablefmt="grid",
        )
    )


def main() -> None:
    # --- Build the data model ---
    owner = Owner("Alex")

    biscuit = Pet("Biscuit", "dog")
    biscuit.add_task(Task("Evening walk", "18:00", "daily", priority="medium"))
    biscuit.add_task(Task("Morning feeding", "07:30", "daily", priority="high"))
    biscuit.add_task(Task("Vet appointment", "14:00", "once", priority="high"))

    mochi = Pet("Mochi", "cat")
    mochi.add_task(Task("Medication", "08:00", "daily", priority="high"))
    mochi.add_task(Task("Playtime", "14:00", "once", priority="low"))  # conflict at 14:00

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)

    # --- Today's schedule ---
    print_schedule(scheduler)

    # --- Conflict detection ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\n[!] CONFLICTS DETECTED:")
        for c in conflicts:
            print(f"  {c}")
    else:
        print("\n[OK] No scheduling conflicts.")

    # --- Next available slot ---
    slot = scheduler.find_next_available_slot("Biscuit")
    print(f"\n[SLOT] Next available slot for Biscuit: {slot}")

    # --- Mark a task complete and show recurrence ---
    print("\n--- Marking 'Morning feeding' complete ---")
    scheduler.mark_task_complete("Biscuit", "Morning feeding")
    print(f"Biscuit now has {biscuit.task_count()} tasks (recurrence auto-added).")
    print_schedule(scheduler)

    # --- Filter: incomplete tasks only ---
    incomplete = scheduler.filter_tasks(completed=False)
    print(f"\n[FILTER] Incomplete tasks: {len(incomplete)}")
    rows = [
        [pet_name, task.time, task.description, task.priority]
        for pet_name, task in incomplete
    ]
    print(
        tabulate(rows, headers=["Pet", "Time", "Task", "Priority"], tablefmt="simple")
    )

    # --- Priority sort ---
    print("\n[PRIORITY] Priority-sorted schedule (high -> low):")
    priority_tasks = scheduler.sort_by_priority_then_time()
    rows = [
        [pet_name, task.priority, task.time, task.description]
        for pet_name, task in priority_tasks
    ]
    print(
        tabulate(rows, headers=["Pet", "Priority", "Time", "Task"], tablefmt="simple")
    )

    # --- JSON persistence ---
    owner.save_to_json("data.json")
    print("\n[SAVE] Schedule saved to data.json")
    reloaded = Owner.load_from_json("data.json")
    total = sum(p.task_count() for p in reloaded.get_pets())
    print(f"[LOAD] Reloaded from JSON: {len(reloaded.get_pets())} pets, {total} tasks total")


if __name__ == "__main__":
    main()
