from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

#Backend work
@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    due_time: Optional[datetime] = None
    notes: str = ""
    status: str = "pending"
    recurrence: str = "none"  # one of: "none", "daily", "weekly"

    def is_high_priority(self) -> bool:
        """Return True if this task is high priority (case-insensitive)."""
        return self.priority.lower() == "high"

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.recurrence.lower() in ("daily", "weekly")

    def recurrence_delta(self) -> Optional[timedelta]:
        """Return the gap until the next occurrence, or None if not recurring."""
        freq = self.recurrence.lower()
        if freq == "daily":
            return timedelta(days=1)
        if freq == "weekly":
            return timedelta(weeks=1)
        return None

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.status = "complete"

    def spawn_next(self) -> Optional["Task"]:
        """Return a fresh, pending Task for this task's next occurrence.

        Returns None if the task doesn't recur or has no due_time to advance.
        """
        delta = self.recurrence_delta()
        if delta is None or self.due_time is None:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_time=self.due_time + delta,
            notes=self.notes,
            recurrence=self.recurrence,
        )  # status defaults to "pending"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a care task from this pet."""
        self.tasks.remove(task)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete; if it recurs, add and return its next occurrence.

        Returns the newly created follow-up task, or None for one-off tasks.
        """
        task.mark_complete()
        follow_up = task.spawn_next()
        if follow_up is not None:
            self.add_task(follow_up)
        return follow_up


@dataclass
class Owner:
    name: str
    preferences: dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner."""
        self.pets.remove(pet)


class Scheduler:
    # Lower number = scheduled earlier. Unknown priorities fall to the end.
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def build_daily_plan(self, owner: Owner) -> List[Task]:
        """Collect every task across the owner's pets and return them ordered."""
        tasks = [task for pet in owner.pets for task in pet.tasks]
        return self.sort_tasks(tasks)

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks by priority, then scheduled time, then shortest duration.

        High priority comes first. Within the same priority, earlier due_time
        wins (tasks without a time sort last), and ties break on shorter tasks.
        """
        def key(task: Task):
            rank = self.PRIORITY_RANK.get(task.priority.lower(), len(self.PRIORITY_RANK))
            due = task.due_time or datetime.max
            return (rank, due, task.duration_minutes)

        return sorted(tasks, key=key)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered purely by their scheduled time (earliest first).

        Uses sorted() with a lambda key on due_time. Tasks with no due_time
        sort to the end via datetime.max. (Note: because due_time is stored as a
        datetime, this sorts chronologically; "HH:MM" strings would also sort
        correctly here since zero-padded 24-hour times sort lexicographically.)
        """
        return sorted(tasks, key=lambda task: task.due_time or datetime.max)

    def filter_by_status(self, tasks: List[Task], status: str = "pending") -> List[Task]:
        """Return only the tasks whose status matches (case-insensitive)."""
        return [task for task in tasks if task.status.lower() == status.lower()]

    def filter_by_pet(self, owner: Owner, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the owner's pet with the given name."""
        return [
            task
            for pet in owner.pets
            if pet.name.lower() == pet_name.lower()
            for task in pet.tasks
        ]

    def get_recurring_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return only the tasks that repeat (daily or weekly)."""
        return [task for task in tasks if task.is_recurring()]

    def next_occurrence(self, task: Task) -> Optional[datetime]:
        """Return when a recurring task next falls due, or None if it doesn't repeat."""
        delta = task.recurrence_delta()
        if delta is None or task.due_time is None:
            return None
        return task.due_time + delta

    def find_conflicts(self, tasks: List[Task]) -> List[Tuple[Task, Task]]:
        """Return pairs of timed tasks whose durations overlap in time.

        Two tasks conflict when both have a due_time and their intervals
        [start, start + duration) overlap. Tasks without a due_time are ignored.
        """
        timed = [task for task in tasks if task.due_time is not None]
        timed.sort(key=lambda task: task.due_time)

        def end_of(task: Task) -> datetime:
            return task.due_time + timedelta(minutes=task.duration_minutes)

        conflicts: List[Tuple[Task, Task]] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                # Sorted by start, so once a later task starts at/after this
                # one's end, no further task can overlap it.
                if timed[j].due_time >= end_of(timed[i]):
                    break
                conflicts.append((timed[i], timed[j]))
        return conflicts

    def conflict_warnings(self, tasks: List[Task]) -> List[str]:
        """Return warning strings for tasks that share the exact same start time.

        Lightweight strategy: group tasks by their due_time and flag any slot
        holding more than one task (whether for the same pet or different pets).
        Returns a list of messages (empty when there are no clashes) and never
        raises, so a caller can simply print the warnings and keep running.
        """
        by_time: dict[datetime, List[Task]] = {}
        for task in tasks:
            if task.due_time is not None:
                by_time.setdefault(task.due_time, []).append(task)

        warnings: List[str] = []
        for when in sorted(by_time):
            clashing = by_time[when]
            if len(clashing) > 1:
                titles = ", ".join(task.title for task in clashing)
                warnings.append(
                    f"WARNING: {len(clashing)} tasks scheduled at {when:%H:%M} ({titles})."
                )
        return warnings

    def explain_plan(self, tasks: List[Task]) -> str:
        """Return a human-readable explanation of the schedule."""
        if not tasks:
            return "No tasks to schedule today."

        lines = [f"Planned {len(tasks)} task(s), ordered by priority then time:"]
        for position, task in enumerate(tasks, start=1):
            when = task.due_time.strftime("%H:%M") if task.due_time else "no set time"
            reason = "high priority" if task.is_high_priority() else f"{task.priority} priority"
            lines.append(
                f"{position}. {task.title} at {when} "
                f"({task.duration_minutes} min, {reason})."
            )
        return "\n".join(lines)
