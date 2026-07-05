from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

#Backend work
@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    due_time: Optional[datetime] = None
    notes: str = ""
    status: str = "pending"

    def is_high_priority(self) -> bool:
        """Return True if this task is high priority (case-insensitive)."""
        return self.priority.lower() == "high"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.status = "complete"


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
