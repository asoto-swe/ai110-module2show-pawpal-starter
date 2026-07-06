"""PawPal+ demo script.

Builds a small owner/pet/task world and exercises the Scheduler's sorting,
filtering, recurring-task, and conflict-detection logic in the terminal.
"""

from datetime import datetime, time

from pawpal_system import Owner, Pet, Task, Scheduler


def today_at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(datetime.now().date(), time(hour, minute))


def all_tasks(owner: Owner) -> list[Task]:
    """Flatten every task across all of the owner's pets."""
    return [task for pet in owner.pets for task in pet.tasks]


def build_world() -> Owner:
    """Create an owner with two pets and tasks added deliberately out of order."""
    owner = Owner(name="Jordan", preferences={"quiet_hours": "22:00-07:00"})

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks are added OUT OF TIME ORDER on purpose so sort_by_time has work to do.
    mochi.add_task(Task("Evening walk", duration_minutes=20, priority="medium",
                        due_time=today_at(18, 0)))
    mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high",
                        due_time=today_at(7, 30), recurrence="daily",
                        notes="Around the block, then the park."))
    luna.add_task(Task("Clean litter box", duration_minutes=10, priority="medium",
                       due_time=today_at(12, 0)))
    # Same-time clash with Luna's litter box (12:00) -- different pet, exact match.
    mochi.add_task(Task("Vet phone call", duration_minutes=15, priority="medium",
                        due_time=today_at(12, 0)))
    luna.add_task(Task("Feed breakfast", duration_minutes=10, priority="high",
                       due_time=today_at(8, 15), recurrence="daily"))
    # Overlaps Mochi's 18:00-18:20 evening walk -> a detectable conflict.
    luna.add_task(Task("Playtime", duration_minutes=15, priority="low",
                       due_time=today_at(18, 10)))

    # Mark one task done so the status filter has something to hide.
    luna.tasks[1].mark_complete()  # Feed breakfast

    return owner


def fmt(task: Task) -> str:
    """One-line label for a task."""
    when = task.due_time.strftime("%H:%M") if task.due_time else "--:--"
    return f"{when}  {task.title} ({task.duration_minutes} min, {task.priority})"


def main() -> None:
    owner = build_world()
    scheduler = Scheduler()
    tasks = all_tasks(owner)

    print(f"\n=== PawPal+ demo for {owner.name} ===")

    # 1. Sort by time -----------------------------------------------------------
    print("\n[Sorted by time]")
    for task in scheduler.sort_by_time(tasks):
        print("  " + fmt(task))

    # 2. Filter by pet ----------------------------------------------------------
    print("\n[Filter: Luna's tasks]")
    for task in scheduler.sort_by_time(scheduler.filter_by_pet(owner, "Luna")):
        print("  " + fmt(task))

    # 3. Filter by status -------------------------------------------------------
    print("\n[Filter: still pending]")
    for task in scheduler.sort_by_time(scheduler.filter_by_status(tasks, "pending")):
        print("  " + fmt(task))

    # 4. Recurring tasks --------------------------------------------------------
    print("\n[Recurring tasks and their next occurrence]")
    for task in scheduler.get_recurring_tasks(tasks):
        nxt = scheduler.next_occurrence(task)
        print(f"  {task.title} ({task.recurrence}) -> next {nxt:%Y-%m-%d %H:%M}")

    # 5a. Same-time warnings (lightweight, exact-match) -------------------------
    print("\n[Same-time warnings]")
    warnings = scheduler.conflict_warnings(tasks)
    if not warnings:
        print("  No same-time clashes.")
    for message in warnings:
        print("  " + message)

    # 5b. Overlap detection (duration-aware) ------------------------------------
    print("\n[Overlapping durations]")
    conflicts = scheduler.find_conflicts(tasks)
    if not conflicts:
        print("  None.")
    for a, b in conflicts:
        print(f"  '{a.title}' ({a.due_time:%H:%M}) overlaps '{b.title}' ({b.due_time:%H:%M})")

    # 6. Completing a recurring task auto-creates the next occurrence ------------
    print("\n[Completing a recurring task]")
    mochi = owner.pets[0]
    morning_walk = mochi.tasks[1]  # the daily 'Morning walk'
    print(f"  Before: Mochi has {len(mochi.tasks)} tasks.")
    follow_up = mochi.complete_task(morning_walk)
    print(f"  Marked '{morning_walk.title}' complete (status={morning_walk.status}).")
    if follow_up:
        print(f"  Auto-created next '{follow_up.title}' for {follow_up.due_time:%Y-%m-%d %H:%M} "
              f"(status={follow_up.status}).")
    print(f"  After:  Mochi has {len(mochi.tasks)} tasks.")

    print()


if __name__ == "__main__":
    main()
