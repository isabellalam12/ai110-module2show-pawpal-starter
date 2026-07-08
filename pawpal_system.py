from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional

PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: Optional[str] = None
    frequency: Optional[str] = None
    completed: bool = False
    notes: Optional[str] = None
    pet_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.priority = self.priority.lower().strip()
        if self.priority not in PRIORITY_ORDER:
            self.priority = "medium"

        if not self.title or not self.title.strip():
            raise ValueError("Task title must not be empty")

        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0")

    def describe(self) -> str:
        pet_label = f" for {self.pet_name}" if self.pet_name else ""
        status = "completed" if self.completed else "pending"
        frequency = f", every {self.frequency}" if self.frequency else ""
        return (
            f"{self.title} ({self.duration_minutes} min, priority={self.priority}, "
            f"status={status}{frequency}){pet_label}"
        )

    def mark_complete(self) -> None:
        self.completed = True

    def is_due(self) -> bool:
        return not self.completed


@dataclass
class Pet:
    name: str
    species: str = "dog"
    age_years: Optional[int] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)

    def describe(self) -> str:
        return f"{self.name} the {self.species}"

    def add_task(self, task: Task) -> None:
        if task.pet_name is None:
            task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        self.tasks = [task for task in self.tasks if task.title != title]

    def get_tasks(self, include_completed: bool = False) -> List[Task]:
        return [task for task in self.tasks if include_completed or not task.completed]

    def get_pending_tasks(self) -> List[Task]:
        return self.get_tasks(include_completed=False)


@dataclass
class Owner:
    name: str
    available_minutes: int = 480
    preferred_start_hour: int = 8
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def describe(self) -> str:
        pet_names = ", ".join(pet.name for pet in self.pets)
        return f"{self.name} owns {pet_names}" if pet_names else f"{self.name} has no pets yet"

    def can_schedule(self, duration_minutes: int) -> bool:
        return duration_minutes <= self.available_minutes

    def prefers_morning(self) -> bool:
        return self.preferences.get("preferred_time", "morning") == "morning"

    def get_preferred_start_time(self) -> time:
        hour = self.preferred_start_hour
        if self.prefers_morning() and hour > 10:
            hour = 8
        return time(hour=hour)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks

    def get_pending_tasks(self) -> List[Task]:
        return self.get_all_tasks(include_completed=False)


class Scheduler:
    def __init__(self, max_minutes: int = 480) -> None:
        self.max_minutes = max_minutes

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        return sorted(
            tasks,
            key=lambda task: (
                task.completed,
                -PRIORITY_ORDER.get(task.priority, 2),
                task.duration_minutes,
                task.title,
            ),
        )

    def retrieve_tasks(self, owner: Owner, include_completed: bool = False) -> List[Task]:
        return owner.get_all_tasks(include_completed=include_completed)

    def organize_tasks(self, owner: Owner) -> List[Task]:
        tasks = self.retrieve_tasks(owner, include_completed=False)
        return self._sort_tasks(tasks)

    def build_daily_plan(
        self,
        owner: Owner,
        plan_date: Optional[date] = None,
        max_minutes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        plan_date = plan_date or date.today()
        max_minutes = max_minutes if max_minutes is not None else self.max_minutes
        remaining_minutes = min(max_minutes, owner.available_minutes)
        start_time = datetime.combine(plan_date, owner.get_preferred_start_time())

        schedule: List[Dict[str, Any]] = []
        for task in self.organize_tasks(owner):
            if task.duration_minutes > remaining_minutes:
                continue

            schedule.append(
                {
                    "pet": task.pet_name,
                    "title": task.title,
                    "start_time": start_time,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "reason": self._explain_reason(task, remaining_minutes, owner),
                }
            )
            start_time += timedelta(minutes=task.duration_minutes)
            remaining_minutes -= task.duration_minutes

        return schedule

    def _explain_reason(self, task: Task, remaining_minutes: int, owner: Owner) -> str:
        if task.priority == "high":
            return "High-priority care is scheduled first so your pet stays healthy."

        if task.category and owner.preferences.get("favorite_category") == task.category:
            return "This task matches the owner's preferred care category."

        if remaining_minutes <= 30:
            return "This task fits the remaining time available today."

        return "This task was selected based on priority, duration, and available time."

    def complete_task(self, task: Task) -> None:
        task.mark_complete()

    def get_schedule_summary(self, plan: List[Dict[str, Any]]) -> str:
        if not plan:
            return "No tasks could be scheduled for today."

        lines = ["Daily plan:"]
        for entry in plan:
            lines.append(
                f"{entry['start_time'].strftime('%H:%M')} — {entry['title']} "
                f"({entry['duration_minutes']} min) [priority: {entry['priority']}]"
            )
        return "\n".join(lines)
