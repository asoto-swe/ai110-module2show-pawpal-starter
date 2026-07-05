"""PawPal+ demo script.

Builds a small owner/pet/task world and prints today's care schedule
to the terminal, ordered by each task's scheduled time.
"""

from datetime import datetime, time

from pawpal_system import Owner, Pet, Task


def today_at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given time."""
    return datetime.combine(datetime.now().date(), time(hour, minute))


def build_world() -> Owner:
    """Create an owner with two pets and a handful of care tasks."""
    owner = Owner(name="Jordan", preferences={"quiet_hours": "22:00-07:00"})

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks with different times of day so the schedule has a clear order.
    mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high",
                         due_time=today_at(7, 30), notes="Around the block, then the park."))
    mochi.add_task(Task("Evening walk", duration_minutes=20, priority="medium",
                        due_time=today_at(18, 0)))
    luna.add_task(Task("Feed breakfast", duration_minutes=10, priority="high",
                       due_time=today_at(8, 15)))
    luna.add_task(Task("Clean litter box", duration_minutes=10, priority="medium",
                       due_time=today_at(12, 0)))

    return owner


def collect_tasks(owner: Owner) -> list[tuple[Pet, Task]]:
    """Flatten every (pet, task) pair across all of the owner's pets."""
    pairs: list[tuple[Pet, Task]] = []
    for pet in owner.pets:
        for task in pet.tasks:
            pairs.append((pet, task))
    return pairs


def print_schedule(owner: Owner) -> None:
    """Print today's schedule to the terminal as an aligned table, ordered by time."""
    pairs = collect_tasks(owner)

    # Order by scheduled time; tasks without a due_time sort to the end.
    pairs.sort(key=lambda pair: pair[1].due_time or datetime.max)

    print(f"\nToday's Schedule for {owner.name}\n")

    if not pairs:
        print("No tasks scheduled today.")
        return

    # Build each row's cells first, then size columns to their widest value.
    headers = ("TIME", "TASK", "PET", "DURATION", "PRIORITY")
    rows: list[tuple[str, str, str, str, str]] = []
    for pet, task in pairs:
        when = task.due_time.strftime("%H:%M") if task.due_time else "--"
        title = f"{task.title} (!)" if task.is_high_priority() else task.title
        rows.append((
            when,
            title,
            f"{pet.name} ({pet.species})",
            f"{task.duration_minutes} min",
            task.priority.upper(),
        ))

    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def format_row(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    separator = "-" * (sum(widths) + 2 * (len(widths) - 1))
    print(format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))


def main() -> None:
    owner = build_world()
    print_schedule(owner)


if __name__ == "__main__":
    main()
