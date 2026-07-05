"""Behavior tests for Task completion and Pet task management."""

from pawpal_system import Pet, Task


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
