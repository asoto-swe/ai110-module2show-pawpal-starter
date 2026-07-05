"""Tests for the PawPal+ domain classes and scheduler."""

from datetime import datetime

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


# --------------------------------------------------------------------------- #
# Task
# --------------------------------------------------------------------------- #
def test_task_defaults():
    task = Task("Walk", duration_minutes=20, priority="low")
    assert task.due_time is None
    assert task.notes == ""


@pytest.mark.parametrize(
    "priority, expected",
    [("high", True), ("HIGH", True), ("High", True), ("medium", False), ("low", False)],
)
def test_is_high_priority_is_case_insensitive(priority, expected):
    assert Task("t", 10, priority).is_high_priority() is expected


# --------------------------------------------------------------------------- #
# Pet
# --------------------------------------------------------------------------- #
def test_pet_add_and_remove_task():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", 20, "high")

    pet.add_task(task)
    assert pet.tasks == [task]

    pet.remove_task(task)
    assert pet.tasks == []


def test_pets_do_not_share_task_lists():
    """Guards against the classic mutable-default-argument bug."""
    a = Pet("A", "dog", 1)
    b = Pet("B", "cat", 2)
    a.add_task(Task("Walk", 20, "high"))
    assert b.tasks == []


# --------------------------------------------------------------------------- #
# Owner
# --------------------------------------------------------------------------- #
def test_owner_add_and_remove_pet():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", 3)

    owner.add_pet(pet)
    assert owner.pets == [pet]

    owner.remove_pet(pet)
    assert owner.pets == []


def test_owners_do_not_share_pet_lists():
    a = Owner("A")
    b = Owner("B")
    a.add_pet(Pet("Mochi", "dog", 3))
    assert b.pets == []


# --------------------------------------------------------------------------- #
# Scheduler
# --------------------------------------------------------------------------- #
def _at(hour, minute=0):
    return datetime(2026, 7, 5, hour, minute)


def test_sort_tasks_orders_by_priority():
    low = Task("low", 10, "low")
    high = Task("high", 10, "high")
    medium = Task("medium", 10, "medium")

    ordered = Scheduler().sort_tasks([low, high, medium])
    assert [t.title for t in ordered] == ["high", "medium", "low"]


def test_sort_tasks_breaks_priority_ties_by_time_then_duration():
    later = Task("later", 10, "high", due_time=_at(9))
    earlier = Task("earlier", 30, "high", due_time=_at(7))
    no_time_short = Task("no_time_short", 5, "high")
    no_time_long = Task("no_time_long", 45, "high")

    ordered = Scheduler().sort_tasks([no_time_long, later, earlier, no_time_short])
    # Timed tasks come first (earliest first); untimed tasks last, shortest first.
    assert [t.title for t in ordered] == [
        "earlier",
        "later",
        "no_time_short",
        "no_time_long",
    ]


def test_sort_tasks_does_not_mutate_input():
    original = [Task("a", 10, "low"), Task("b", 10, "high")]
    snapshot = list(original)
    Scheduler().sort_tasks(original)
    assert original == snapshot


def test_unknown_priority_sorts_after_known_ones():
    urgent = Task("urgent", 10, "urgent")  # not in the rank table
    high = Task("high", 10, "high")
    ordered = Scheduler().sort_tasks([urgent, high])
    assert [t.title for t in ordered] == ["high", "urgent"]


def test_build_daily_plan_gathers_tasks_across_all_pets():
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("walk", 20, "medium", due_time=_at(18)))
    cat.add_task(Task("feed", 10, "high", due_time=_at(8)))

    plan = Scheduler().build_daily_plan(owner)
    assert [t.title for t in plan] == ["feed", "walk"]


def test_build_daily_plan_empty_owner():
    assert Scheduler().build_daily_plan(Owner("Nobody")) == []


def test_explain_plan_empty():
    assert Scheduler().explain_plan([]) == "No tasks to schedule today."


def test_explain_plan_lists_every_task_in_order():
    tasks = [
        Task("Feed breakfast", 10, "high", due_time=_at(8)),
        Task("Evening walk", 20, "medium"),
    ]
    text = Scheduler().explain_plan(tasks)
    lines = text.splitlines()

    assert lines[0].startswith("Planned 2 task(s)")
    assert lines[1].startswith("1. Feed breakfast at 08:00")
    assert "high priority" in lines[1]
    assert lines[2].startswith("2. Evening walk at no set time")
