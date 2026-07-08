from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str = "dog"
    age_years: Optional[int] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        pass


@dataclass
class User:
    name: str
    available_minutes: int = 480
    preferred_start_hour: int = 8
    preferences: Dict[str, Any] = field(default_factory=dict)

    def can_schedule(self, duration_minutes: int) -> bool:
        pass

    def prefers_morning(self) -> bool:
        pass


@dataclass
class TodaysPlan:
    owner_name: str
    pet_name: str
    plan_date: date
    entries: List[Dict[str, Any]] = field(default_factory=list)
    total_minutes: int = 0

    def add_entry(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        priority: str,
        reason: str,
    ) -> None:
        pass

    def summary_text(self) -> str:
        pass

    def explain(self) -> str:
        pass


class Schedule:
    def __init__(self, max_minutes: int = 480) -> None:
        self.tasks: List[Task] = []
        self.max_minutes = max_minutes

    def add_task(self, task: Task) -> None:
        pass

    def _sorted_tasks(self) -> List[Task]:
        pass

    def generate_today_plan(
        self,
        user: User,
        pet: Pet,
        plan_date: Optional[date] = None,
    ) -> TodaysPlan:
        pass

    def _explain_reason(
        self,
        task: Task,
        remaining_minutes: int,
        user: User,
        pet: Pet,
    ) -> str:
        pass
