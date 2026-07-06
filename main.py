"""PawPal+ demo script.

Builds a small owner/pet/task world and exercises the Scheduler's sorting,
filtering, recurring-task, and conflict-detection logic in the terminal --
with color-coded, emoji-tagged, tabulated output for a friendlier CLI.
"""

import sys
from datetime import datetime, time

from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from pawpal_system import Owner, Pet, Task, Scheduler

# Windows terminals default to cp1252, which can't encode emoji; switch stdout
# to UTF-8 before colorama wraps it so the emoji below print cleanly.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Reset colors automatically after every print and translate ANSI on Windows.
colorama_init(autoreset=True)

# Emoji chosen by matching keywords in the task title.
TASK_EMOJI = {
    "walk": "🚶",
    "feed": "🍽️", "breakfast": "🍽️", "dinner": "🍽️", "meal": "🍽️",
    "med": "💊", "pill": "💊",
    "groom": "✂️",
    "play": "🎾",
    "vet": "🏥",
    "litter": "🧹", "clean": "🧹",
    "water": "💧",
}

PRIORITY_COLOR = {"high": Fore.RED, "medium": Fore.YELLOW, "low": Fore.GREEN}
STATUS_COLOR = {"pending": Fore.YELLOW, "complete": Fore.GREEN}


def today_at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(datetime.now().date(), time(hour, minute))


def all_tasks(owner: Owner) -> list[Task]:
    """Flatten every task across all of the owner's pets."""
    return [task for pet in owner.pets for task in pet.tasks]


def task_emoji(task: Task) -> str:
    """Pick an emoji for a task based on keywords in its title."""
    title = task.title.lower()
    for keyword, emoji in TASK_EMOJI.items():
        if keyword in title:
            return emoji
    return "🐾"  # default paw print


def color_priority(priority: str) -> str:
    """Return the priority label tinted by urgency."""
    color = PRIORITY_COLOR.get(priority.lower(), "")
    return f"{color}{priority.upper()}{Style.RESET_ALL}"


def color_status(status: str) -> str:
    """Return a status label with a colored dot indicator."""
    color = STATUS_COLOR.get(status.lower(), "")
    dot = "●" if status.lower() == "complete" else "○"
    return f"{color}{dot} {status}{Style.RESET_ALL}"


def header(text: str) -> None:
    """Print a bold, bright section header."""
    print(f"\n{Style.BRIGHT}{Fore.CYAN}{text}{Style.RESET_ALL}")


def fmt(task: Task) -> str:
    """One-line, emoji + color label for a task."""
    when = task.due_time.strftime("%H:%M") if task.due_time else "--:--"
    return f"{when}  {task_emoji(task)} {task.title}  [{color_priority(task.priority)}]"


def schedule_table(tasks: list[Task]) -> str:
    """Render tasks as a structured CLI table via tabulate."""
    rows = [
        [
            task.due_time.strftime("%H:%M") if task.due_time else "--:--",
            f"{task_emoji(task)} {task.title}",
            f"{task.duration_minutes} min",
            color_priority(task.priority),
            color_status(task.status),
            task.recurrence if task.recurrence != "none" else "-",
        ]
        for task in tasks
    ]
    headers = ["Time", "Task", "Duration", "Priority", "Status", "Repeat"]
    return tabulate(rows, headers=headers, tablefmt="fancy_grid")


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


def main() -> None:
    owner = build_world()
    scheduler = Scheduler()
    tasks = all_tasks(owner)

    print(f"\n{Style.BRIGHT}🐾 PawPal+ daily plan for {owner.name}{Style.RESET_ALL}")

    # 1. Sorted schedule as a structured table ----------------------------------
    header("📋 Today's schedule (sorted by time)")
    print(schedule_table(scheduler.sort_by_time(tasks)))

    # 2. Filter by pet ----------------------------------------------------------
    header("🐈 Luna's tasks only")
    for task in scheduler.sort_by_time(scheduler.filter_by_pet(owner, "Luna")):
        print("  " + fmt(task))

    # 3. Filter by status -------------------------------------------------------
    header("⏳ Still pending")
    for task in scheduler.sort_by_time(scheduler.filter_by_status(tasks, "pending")):
        print("  " + fmt(task))

    # 4. Recurring tasks --------------------------------------------------------
    header("🔁 Recurring tasks and their next occurrence")
    for task in scheduler.get_recurring_tasks(tasks):
        nxt = scheduler.next_occurrence(task)
        print(f"  {task_emoji(task)} {task.title} ({task.recurrence}) "
              f"-> next {nxt:%Y-%m-%d %H:%M}")

    # 5. Conflict detection -----------------------------------------------------
    header("⚠️  Scheduling conflicts")
    warnings = scheduler.conflict_warnings(tasks)
    if not warnings:
        print(f"  {Fore.GREEN}✓ No same-time clashes.{Style.RESET_ALL}")
    for message in warnings:
        print(f"  {Fore.RED}{message}{Style.RESET_ALL}")
    for a, b in scheduler.find_conflicts(tasks):
        print(f"  {Fore.MAGENTA}↔ '{a.title}' ({a.due_time:%H:%M}) overlaps "
              f"'{b.title}' ({b.due_time:%H:%M}){Style.RESET_ALL}")

    # 6. Completing a recurring task auto-creates the next occurrence ------------
    header("✅ Completing a recurring task")
    mochi = owner.pets[0]
    morning_walk = mochi.tasks[1]  # the daily 'Morning walk'
    print(f"  Before: Mochi has {len(mochi.tasks)} tasks.")
    follow_up = mochi.complete_task(morning_walk)
    print(f"  Marked '{morning_walk.title}' complete ({color_status(morning_walk.status)}).")
    if follow_up:
        print(f"  {Fore.GREEN}Auto-created next '{follow_up.title}' for "
              f"{follow_up.due_time:%Y-%m-%d %H:%M}{Style.RESET_ALL} "
              f"({color_status(follow_up.status)}).")
    print(f"  After:  Mochi has {len(mochi.tasks)} tasks.")

    print()


if __name__ == "__main__":
    main()
