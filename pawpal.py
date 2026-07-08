from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Pet:
    name: str
    species: str = "dog"
    age_years: Optional[int] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        return f"{self.name} the {self.species}"


@dataclass
class User:
    name: str
    available_minutes: int = 480
    preferred_start_hour: int = 8
    preferences: Dict[str, Any] = field(default_factory=dict)

    def can_schedule(self, duration_minutes: int) -> bool:
        return duration_minutes <= self.available_minutes

    def prefers_morning(self) -> bool:
        return self.preferences.get("preferred_time", "morning") == "morning"


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
        self.entries.append(
            {
                "title": title,
                "start_time": start_time,
                "duration_minutes": duration_minutes,
                "priority": priority,
                "reason": reason,
            }
        )
        self.total_minutes += duration_minutes

    def summary_text(self) -> str:
        if not self.entries:
            return f"No tasks could be scheduled for {self.pet_name} on {self.plan_date.isoformat()}."

        lines = [
            f"Daily plan for {self.pet_name} ({self.owner_name}) on {self.plan_date.isoformat()}:"
        ]
        for entry in self.entries:
            lines.append(
                f"{entry['start_time'].strftime('%H:%M')} — {entry['title']} "
                f"({entry['duration_minutes']} min) [priority: {entry['priority']}]"
            )
        return "\n".join(lines)

    def explain(self) -> str:
        if not self.entries:
            return "No tasks were scheduled because there were no available time slots or tasks."

        lines = ["Why this plan was chosen:"]
        for entry in self.entries:
            lines.append(f"- {entry['title']}: {entry['reason']}")
        return "\n".join(lines)


@dataclass
class Schedule:
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    max_minutes: int = 480

    def add_task(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: Optional[str] = None,
    ) -> None:
        normalized_priority = priority.lower()
        if normalized_priority not in PRIORITY_ORDER:
            normalized_priority = "medium"

        self.tasks.append(
            {
                "title": title,
                "duration_minutes": duration_minutes,
                "priority": normalized_priority,
                "category": category or "care",
            }
        )

    def _sorted_tasks(self) -> List[Dict[str, Any]]:
        return sorted(
            self.tasks,
            key=lambda task: (
                -PRIORITY_ORDER[task["priority"]],
                task["duration_minutes"],
                task["title"],
            ),
        )

    def generate_today_plan(
        self,
        user: User,
        pet: Pet,
        plan_date: Optional[date] = None,
    ) -> TodaysPlan:
        plan_date = plan_date or date.today()
        plan = TodaysPlan(owner_name=user.name, pet_name=pet.name, plan_date=plan_date)

        current_time = datetime.combine(plan_date, datetime.min.time()).replace(
            hour=user.preferred_start_hour
        )
        remaining_minutes = min(self.max_minutes, user.available_minutes)

        for task in self._sorted_tasks():
            duration = task["duration_minutes"]
            if duration > remaining_minutes:
                continue
            if not user.can_schedule(duration):
                continue

            plan.add_entry(
                title=task["title"],
                start_time=current_time,
                duration_minutes=duration,
                priority=task["priority"],
                reason=self._explain_reason(task, remaining_minutes, user, pet),
            )
            current_time += timedelta(minutes=duration)
            remaining_minutes -= duration

        return plan

    def _explain_reason(
        self,
        task: Dict[str, Any],
        remaining_minutes: int,
        user: User,
        pet: Pet,
    ) -> str:
        if task["priority"] == "high":
            return "High-priority care to keep your pet healthy and happy."

        if task["category"] == "feeding":
            return "A feeding task is important for daily routine."

        if task["duration_minutes"] <= 15:
            return "A short task that fits well into the day."

        if remaining_minutes < 30:
            return "Only the most important remaining tasks fit into the available time."

        return "Selected based on priority, duration, and available time."
