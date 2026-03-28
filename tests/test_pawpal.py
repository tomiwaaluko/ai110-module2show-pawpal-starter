"""Automated test suite for PawPal+ system."""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def make_scheduler():
    """Helper: returns a Scheduler with two pets and several tasks."""
    owner = Owner("Test Owner")
    dog = Pet("Rex", "dog")
    cat = Pet("Luna", "cat")
    dog.add_task(Task("Evening walk", "18:00", "daily"))
    dog.add_task(Task("Morning feeding", "07:30", "daily"))
    dog.add_task(Task("Vet appointment", "14:00", "once"))
    cat.add_task(Task("Medication", "08:00", "daily"))
    cat.add_task(Task("Playtime", "14:00", "once"))  # conflict with dog's vet at 14:00
    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner)


def test_task_completion_changes_status():
    """Marking a task complete should set completed=True."""
    task = Task("Feed cat", "08:00", "once")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_daily_task_creates_next_occurrence():
    """Completing a daily task should return a new Task for tomorrow."""
    today = date.today()
    task = Task("Morning walk", "07:00", "daily", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task should return a new Task one week later."""
    today = date.today()
    task = Task("Bath time", "11:00", "weekly", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.completed is False


def test_once_task_returns_none_on_complete():
    """Completing a one-time task should not create a recurrence."""
    task = Task("Vet appointment", "14:00", "once")
    result = task.mark_complete()
    assert result is None


def test_adding_task_increases_pet_task_count():
    """Adding a task to a pet should increment its task count."""
    pet = Pet("Buddy", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "09:00"))
    assert pet.task_count() == 1
    pet.add_task(Task("Feed", "17:00"))
    assert pet.task_count() == 2


def test_sorting_returns_chronological_order():
    """sort_by_time should return tasks ordered earliest to latest."""
    scheduler = make_scheduler()
    sorted_tasks = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_tasks]
    assert times == sorted(times)


def test_conflict_detection_flags_same_time():
    """Scheduler should detect when two tasks share the same time slot."""
    scheduler = make_scheduler()
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0
    assert "14:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Scheduler should not flag conflicts when all times are unique."""
    owner = Owner("Clean Owner")
    pet = Pet("Solo", "cat")
    pet.add_task(Task("Task A", "08:00"))
    pet.add_task(Task("Task B", "09:00"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_filter_by_completion_status():
    """filter_tasks with completed=False should return only incomplete tasks."""
    scheduler = make_scheduler()
    scheduler.mark_task_complete("Rex", "Morning feeding")
    incomplete = scheduler.filter_tasks(completed=False)
    for _, task in incomplete:
        assert task.completed is False


def test_mark_complete_adds_recurrence_to_pet():
    """After marking a daily task complete, pet should have a new recurrence task."""
    owner = Owner("Recurrence Owner")
    pet = Pet("Pip", "hamster")
    pet.add_task(Task("Water change", "10:00", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    initial_count = pet.task_count()
    scheduler.mark_task_complete("Pip", "Water change")
    assert pet.task_count() == initial_count + 1


def test_filter_by_pet_name():
    """filter_tasks by pet_name should return only that pet's tasks."""
    scheduler = make_scheduler()
    rex_tasks = scheduler.filter_tasks(pet_name="Rex")
    for pet_name, _ in rex_tasks:
        assert pet_name == "Rex"


def test_get_all_tasks_count():
    """get_all_tasks should return every task across all pets."""
    scheduler = make_scheduler()
    all_tasks = scheduler.get_all_tasks()
    # Rex: 3 tasks, Luna: 2 tasks
    assert len(all_tasks) == 5


def test_find_next_available_slot_avoids_occupied():
    """find_next_available_slot should not return a time already occupied."""
    owner = Owner("Slot Owner")
    pet = Pet("Dot", "cat")
    pet.add_task(Task("Feeding", "07:00"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    slot = scheduler.find_next_available_slot("Dot")
    occupied = {task.time for _, task in scheduler.get_all_tasks()}
    assert slot not in occupied


def test_priority_sort_high_before_low():
    """sort_by_priority_then_time should place high-priority tasks before low."""
    owner = Owner("Prio Owner")
    pet = Pet("Ace", "dog")
    pet.add_task(Task("Low task", "07:00", priority="low"))
    pet.add_task(Task("High task", "09:00", priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_priority_then_time()
    priorities = [task.priority for _, task in sorted_tasks]
    assert priorities[0] == "high"
    assert priorities[-1] == "low"
