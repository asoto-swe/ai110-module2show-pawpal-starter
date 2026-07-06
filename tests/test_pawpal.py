"""Behavior tests for Task completion and Pet task management."""

from datetime import datetime, timedelta

from pawpal_system import Pet, Task, Scheduler


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", duration_minutes=20, priority="high")

    # A new task starts out pending...
    assert task.status == "pending"

    task.mark_complete()

    # ...and mark_complete() flips it to complete.
    assert task.status == "complete"


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed breakfast", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Evening walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2


def test_completing_daily_task_creates_next_occurrence():
    pet = Pet("Mochi", "dog", 3)
    due = datetime(2026, 7, 5, 7, 30)
    walk = Task("Morning walk", 30, "high", due_time=due, recurrence="daily")
    pet.add_task(walk)

    follow_up = pet.complete_task(walk)

    # Original is complete; a fresh pending occurrence was added for the next day.
    assert walk.status == "complete"
    assert follow_up is not None
    assert follow_up.status == "pending"
    assert follow_up.due_time == due + timedelta(days=1)
    assert len(pet.tasks) == 2


def test_completing_weekly_task_advances_by_a_week():
    pet = Pet("Luna", "cat", 5)
    due = datetime(2026, 7, 5, 9, 0)
    groom = Task("Grooming", 45, "medium", due_time=due, recurrence="weekly")
    pet.add_task(groom)

    follow_up = pet.complete_task(groom)

    assert follow_up.due_time == due + timedelta(weeks=1)


def test_completing_one_off_task_creates_no_new_occurrence():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Vet visit", 60, "high", due_time=datetime(2026, 7, 5, 14, 0))
    pet.add_task(task)

    follow_up = pet.complete_task(task)

    # Non-recurring task: completed, but nothing new is spawned.
    assert follow_up is None
    assert task.status == "complete"
    assert len(pet.tasks) == 1


def test_recurring_task_without_due_time_spawns_nothing():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Daily meds", 5, "high", recurrence="daily")  # no due_time
    pet.add_task(task)

    assert pet.complete_task(task) is None
    assert len(pet.tasks) == 1


def test_conflict_warnings_flags_two_tasks_at_the_same_time():
    when = datetime(2026, 7, 5, 12, 0)
    tasks = [
        Task("Clean litter box", 10, "medium", due_time=when),
        Task("Vet phone call", 15, "medium", due_time=when),
    ]
    warnings = Scheduler().conflict_warnings(tasks)

    assert len(warnings) == 1
    assert "12:00" in warnings[0]
    assert "Clean litter box" in warnings[0] and "Vet phone call" in warnings[0]


def test_conflict_warnings_empty_when_times_differ():
    tasks = [
        Task("A", 10, "low", due_time=datetime(2026, 7, 5, 8, 0)),
        Task("B", 10, "low", due_time=datetime(2026, 7, 5, 9, 0)),
        Task("C", 10, "low"),  # no due_time -> ignored, not a clash
    ]
    assert Scheduler().conflict_warnings(tasks) == []
