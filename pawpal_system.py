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

    def is_high_priority(self) -> bool:
        return self.priority.lower() == "high"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    preferences: dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)


class Scheduler:
    def build_daily_plan(self, owner: Owner) -> List[Task]:
        """Generate a schedule from the owner's pet care tasks."""
        raise NotImplementedError

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority and duration."""
        raise NotImplementedError

    def explain_plan(self, tasks: List[Task]) -> str:
        """Return a human-readable explanation of the schedule."""
        raise NotImplementedError
