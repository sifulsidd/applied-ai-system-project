import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion():
    # Daily task: mark_complete should flag it done and return next day's occurrence
    daily_task = Task(description="Morning walk", duration=30, frequency="daily", time="07:00 AM")
    assert daily_task.completed is False
    next_task = daily_task.mark_complete()
    assert daily_task.completed is True
    assert next_task is not None
    assert next_task.date == daily_task.date + timedelta(days=1)
    assert next_task.completed is False

    # Weekly task: next occurrence should be 7 days out
    weekly_task = Task(description="Bath time", duration=45, frequency="weekly", time="02:00 PM")
    next_task = weekly_task.mark_complete()
    assert weekly_task.completed is True
    assert next_task is not None
    assert next_task.date == weekly_task.date + timedelta(weeks=1)

    # Monthly task: no auto-scheduling, returns None
    monthly_task = Task(description="Vet checkup", duration=60, frequency="monthly", time="10:00 AM")
    next_task = monthly_task.mark_complete()
    assert monthly_task.completed is True
    assert next_task is None


def test_task_addition():
    owner = Owner(name="Alex")
    buddy = Pet(name="Buddy", age=3, owner=owner)
    task = Task(description="Feed breakfast", duration=10, frequency="daily", time="08:00 AM")

    assert len(buddy.tasks) == 0
    buddy.add_task(task)
    assert len(buddy.tasks) == 1

    # Completing the task and adding the next occurrence should grow the list
    next_task = task.mark_complete()
    if next_task:
        buddy.add_task(next_task)
    assert len(buddy.tasks) == 2
    assert buddy.tasks[1].completed is False


def test_sort_by_time():
    scheduler = Scheduler()

    # Tasks added in reverse chronological order
    tasks = [
        Task(description="Evening walk",   duration=20, frequency="daily", time="06:00 PM"),
        Task(description="Afternoon nap",  duration=30, frequency="daily", time="02:00 PM"),
        Task(description="Feed breakfast", duration=10, frequency="daily", time="08:00 AM"),
        Task(description="Morning walk",   duration=30, frequency="daily", time="07:00 AM"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    expected_order = ["07:00 AM", "08:00 AM", "02:00 PM", "06:00 PM"]
    assert [t.time for t in sorted_tasks] == expected_order

    # Original list should not be mutated
    assert tasks[0].time == "06:00 PM"

    # Empty list should return empty list without error
    assert scheduler.sort_by_time([]) == []

    # Single task should return a list with that one task
    single = [Task(description="Vet checkup", duration=60, frequency="monthly", time="10:00 AM")]
    assert scheduler.sort_by_time(single) == single

    # Tasks at identical times should all be preserved (stable sort)
    same_time = [
        Task(description="Task A", duration=15, frequency="daily", time="09:00 AM"),
        Task(description="Task B", duration=15, frequency="daily", time="09:00 AM"),
    ]
    sorted_same = scheduler.sort_by_time(same_time)
    assert len(sorted_same) == 2
    assert sorted_same[0].description == "Task A"
    assert sorted_same[1].description == "Task B"

    # Midnight (12:00 AM) should sort before noon (12:00 PM)
    midnight_noon = [
        Task(description="Noon task",     duration=10, frequency="daily", time="12:00 PM"),
        Task(description="Midnight task", duration=10, frequency="daily", time="12:00 AM"),
    ]
    sorted_mn = scheduler.sort_by_time(midnight_noon)
    assert sorted_mn[0].description == "Midnight task"
    assert sorted_mn[1].description == "Noon task"


def test_daily_recurrence():
    # Marking a daily task complete should return a new task dated the following day
    task = Task(description="Morning walk", duration=30, frequency="daily", time="07:00 AM")
    original_date = task.date

    next_task = task.mark_complete()

    # Original task is now done
    assert task.completed is True

    # A new task was created (not None)
    assert next_task is not None

    # New task is scheduled exactly one day later
    assert next_task.date == original_date + timedelta(days=1)

    # New task inherits all properties from the original
    assert next_task.description == task.description
    assert next_task.duration == task.duration
    assert next_task.frequency == task.frequency
    assert next_task.time == task.time
    assert next_task.priority == task.priority

    # New task starts as pending
    assert next_task.completed is False

    # Chaining: completing the next task should schedule yet another day forward
    task_after_next = next_task.mark_complete()
    assert task_after_next is not None
    assert task_after_next.date == original_date + timedelta(days=2)
    assert task_after_next.completed is False


def test_conflict_detection():
    scheduler = Scheduler()
    owner = Owner(name="Alex")
    buddy = Pet(name="Buddy", age=3, owner=owner)
    luna = Pet(name="Luna", age=5, owner=owner)
    owner.add_pet(buddy)
    owner.add_pet(luna)

    # Overlapping: Buddy 07:00 AM (30 mins) vs Luna 07:15 AM (15 mins) — windows overlap
    buddy.add_task(Task(description="Morning walk",     duration=30, frequency="daily",   time="07:00 AM"))
    luna.add_task( Task(description="Morning grooming", duration=15, frequency="daily",   time="07:15 AM"))

    conflicts = scheduler.detect_conflicts(owner)
    assert len(conflicts) == 1
    assert "Morning walk"     in conflicts[0]
    assert "Morning grooming" in conflicts[0]

    # Back-to-back tasks that touch but do NOT overlap (07:30 AM starts exactly when first ends)
    owner2 = Owner(name="Sam")
    rex = Pet(name="Rex", age=2, owner=owner2)
    owner2.add_pet(rex)
    rex.add_task(Task(description="Feed breakfast", duration=30, frequency="daily", time="07:00 AM"))
    rex.add_task(Task(description="Play time",      duration=20, frequency="daily", time="07:30 AM"))

    assert scheduler.detect_conflicts(owner2) == []

    # No tasks at all — no conflicts
    owner3 = Owner(name="Empty")
    assert scheduler.detect_conflicts(owner3) == []

    # Single task — nothing to pair, no conflict
    owner4 = Owner(name="Solo")
    cat = Pet(name="Whiskers", age=4, owner=owner4)
    owner4.add_pet(cat)
    cat.add_task(Task(description="Vet checkup", duration=60, frequency="monthly", time="10:00 AM"))
    assert scheduler.detect_conflicts(owner4) == []

    # Exact same time on two pets — should conflict
    owner5 = Owner(name="Twins")
    pet_a = Pet(name="A", age=1, owner=owner5)
    pet_b = Pet(name="B", age=1, owner=owner5)
    owner5.add_pet(pet_a)
    owner5.add_pet(pet_b)
    pet_a.add_task(Task(description="Bath", duration=20, frequency="weekly", time="02:00 PM"))
    pet_b.add_task(Task(description="Nap",  duration=20, frequency="daily",  time="02:00 PM"))

    same_time_conflicts = scheduler.detect_conflicts(owner5)
    assert len(same_time_conflicts) == 1
