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
    preferred_start: Optional[time] = None
    completed: bool = False
    last_completed: Optional[date] = None
    next_due_date: Optional[date] = None
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
        preferred = f", preferred {self.preferred_start.strftime('%H:%M')}" if self.preferred_start else ""
        return (
            f"{self.title} ({self.duration_minutes} min, priority={self.priority}, "
            f"status={status}{frequency}{preferred}){pet_label}"
        )

    def mark_complete(self) -> None:
        """Mark task as complete and calculate next due date if recurring."""
        self.completed = True
        self.last_completed = date.today()
        
        # Calculate next due date based on frequency using timedelta
        if self.frequency == "daily":
            self.next_due_date = date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_due_date = date.today() + timedelta(weeks=1)
        elif self.frequency == "monthly":
            # For monthly, add approximately 28 days to account for varying month lengths
            self.next_due_date = date.today() + timedelta(days=28)
        else:
            self.next_due_date = None

    def create_next_occurrence(self) -> Optional[Task]:
        """Create a new Task instance for the next occurrence if this is a recurring task."""
        if self.frequency not in ("daily", "weekly"):
            return None
        
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            preferred_start=self.preferred_start,
            completed=False,
            last_completed=None,
            notes=self.notes,
            pet_name=self.pet_name,
            metadata=self.metadata.copy() if self.metadata else {}
        )

    def is_due(self, today: Optional[date] = None) -> bool:
        today = today or date.today()
        if not self.completed:
            return True
        if not self.frequency:
            return False
        if self.last_completed is None:
            return True

        days_since = (today - self.last_completed).days
        if self.frequency == "daily":
            return days_since >= 1
        if self.frequency == "weekly":
            return days_since >= 7
        if self.frequency == "monthly":
            return today.month != self.last_completed.month or days_since >= 28
        return days_since >= 1


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
        return [task for task in self.tasks if include_completed or task.is_due()]

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.is_due()]


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

    def get_all_tasks(self, include_completed: bool = False, pet_name: Optional[str] = None) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            if pet_name and pet.name != pet_name:
                continue
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks

    def get_pending_tasks(self, pet_name: Optional[str] = None) -> List[Task]:
        return self.get_all_tasks(include_completed=False, pet_name=pet_name)


class Scheduler:
    def __init__(self, max_minutes: int = 480) -> None:
        self.max_minutes = max_minutes

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks by preferred time, then priority (high first), duration, and title."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_start or time(23, 59),
                -PRIORITY_ORDER.get(task.priority, 2),
                task.duration_minutes,
                task.title,
            ),
        )

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by their preferred start time in HH:MM format."""
        return sorted(
            tasks,
            key=lambda task: task.preferred_start.strftime('%H:%M') if task.preferred_start else '23:59'
        )

    def filter_tasks(self, tasks: List[Task], completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name."""
        result = tasks
        if completed is not None:
            result = [task for task in result if task.completed == completed]
        if pet_name is not None:
            result = [task for task in result if task.pet_name == pet_name]
        return result

    def _has_conflict(self, start: datetime, end: datetime, schedule: List[Dict[str, Any]]) -> bool:
        """Return True if [start, end) overlaps any already-scheduled time slot."""
        for entry in schedule:
            if entry["start_time"] < end and start < entry["end_time"]:
                return True
        return False

    def retrieve_tasks(
        self,
        owner: Owner,
        include_completed: bool = False,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        return owner.get_all_tasks(include_completed=include_completed, pet_name=pet_name)

    def organize_tasks(self, owner: Owner, pet_name: Optional[str] = None) -> List[Task]:
        tasks = self.retrieve_tasks(owner, include_completed=False, pet_name=pet_name)
        return [task for task in self._sort_tasks(tasks) if task.is_due()]

    def build_daily_plan(
        self,
        owner: Owner,
        plan_date: Optional[date] = None,
        max_minutes: Optional[int] = None,
        pet_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        plan_date = plan_date or date.today()
        max_minutes = max_minutes if max_minutes is not None else self.max_minutes
        remaining_minutes = min(max_minutes, owner.available_minutes)
        current_time = datetime.combine(plan_date, owner.get_preferred_start_time())
        schedule: List[Dict[str, Any]] = []

        for task in self.organize_tasks(owner, pet_name=pet_name):
            task_start = datetime.combine(plan_date, task.preferred_start) if task.preferred_start else current_time
            if task_start < current_time:
                task_start = current_time

            task_end = task_start + timedelta(minutes=task.duration_minutes)
            if task.duration_minutes > remaining_minutes:
                continue

            conflict = self._has_conflict(task_start, task_end, schedule)
            if conflict:
                task_start = current_time
                task_end = task_start + timedelta(minutes=task.duration_minutes)
                conflict = self._has_conflict(task_start, task_end, schedule)
                if conflict:
                    continue

            schedule.append(
                {
                    "pet": task.pet_name,
                    "title": task.title,
                    "start_time": task_start,
                    "end_time": task_end,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "reason": self._explain_reason(task, remaining_minutes, owner),
                    "conflict": conflict,
                }
            )
            current_time = task_end
            remaining_minutes -= task.duration_minutes

        return schedule

    def _explain_reason(self, task: Task, remaining_minutes: int, owner: Owner) -> str:
        if task.priority == "high":
            return "High-priority care is scheduled first so your pet stays healthy."

        if task.category and owner.preferences.get("favorite_category") == task.category:
            return "This task matches the owner's preferred care category."

        if task.preferred_start:
            return "This task has a preferred time and is scheduled accordingly."

        if remaining_minutes <= 30:
            return "This task fits the remaining time available today."

        return "This task was selected based on preferred time, priority, and available time."

    def find_time_conflicts(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Detect if two or more tasks for same/different pets share a preferred start time."""
        conflicts = []
        task_times: Dict[str, List[Task]] = {}

        # Group tasks by preferred_start time. Tasks without a set time have no
        # scheduled slot, so they cannot conflict on time and are skipped.
        for task in tasks:
            if task.preferred_start is None:
                continue
            time_key = task.preferred_start.strftime('%H:%M')
            task_times.setdefault(time_key, []).append(task)

        # A time slot with more than one task is a conflict (same or different pets).
        for time_key, tasks_at_time in task_times.items():
            if len(tasks_at_time) > 1:
                conflicts.append({
                    'time': time_key,
                    'task_count': len(tasks_at_time),
                    'tasks': [
                        {
                            'title': t.title,
                            'pet': t.pet_name,
                            'duration': t.duration_minutes,
                            'priority': t.priority
                        }
                        for t in tasks_at_time
                    ]
                })

        return conflicts

    def warn_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return human-readable warning strings for tasks that share a start time."""
        warnings = []
        for conflict in self.find_time_conflicts(tasks):
            labels = ", ".join(
                f"'{t['title']}' ({t['pet'] or 'unassigned'})" for t in conflict['tasks']
            )
            warnings.append(
                f"⚠️  Conflict at {conflict['time']}: {conflict['task_count']} tasks "
                f"are scheduled at the same time — {labels}."
            )
        return warnings

    def detect_schedule_conflicts(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect overlapping tasks in a daily schedule (same or different pets)."""
        conflicts = []
        
        for i, task1 in enumerate(plan):
            for task2 in plan[i+1:]:
                # Check if task2 starts before task1 ends (overlap)
                if task2['start_time'] < task1['end_time'] and task1['start_time'] < task2['end_time']:
                    conflicts.append({
                        'task_1': task1['title'],
                        'pet_1': task1['pet'],
                        'time_1': f"{task1['start_time'].strftime('%H:%M')}-{task1['end_time'].strftime('%H:%M')}",
                        'task_2': task2['title'],
                        'pet_2': task2['pet'],
                        'time_2': f"{task2['start_time'].strftime('%H:%M')}-{task2['end_time'].strftime('%H:%M')}",
                        'overlap_minutes': int(min(
                            (task1['end_time'] - task2['start_time']).total_seconds(),
                            (task2['end_time'] - task1['start_time']).total_seconds()
                        ) // 60)
                    })
        
        return conflicts

    def complete_task(self, task: Task) -> None:
        """Mark a single task complete (no recurrence handling)."""
        task.mark_complete()

    def complete_recurring_task(self, task: Task, owner: Owner, pet_name: str) -> Optional[Task]:
        """Mark task complete and auto-create next occurrence if it's daily or weekly."""
        task.mark_complete()
        next_task = task.create_next_occurrence()
        
        if next_task:
            pet = owner.get_pet(pet_name)
            if pet:
                pet.add_task(next_task)
                return next_task
        return None

    def get_schedule_summary(self, plan: List[Dict[str, Any]]) -> str:
        if not plan:
            return "No tasks could be scheduled for today."

        lines = ["Daily plan:"]
        for entry in plan:
            conflict_note = " (conflict resolved)" if entry.get("conflict") else ""
            lines.append(
                f"{entry['start_time'].strftime('%H:%M')} — {entry['title']} "
                f"({entry['duration_minutes']} min) [priority: {entry['priority']}]" + conflict_note
            )
        return "\n".join(lines)
