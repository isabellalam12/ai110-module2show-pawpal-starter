from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_marks_task_completed() -> None:
    task = Task(title="Feed", duration_minutes=10, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_to_pet_increases_task_count() -> None:
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0

    task = Task(title="Play", duration_minutes=20, priority="medium")
    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task


def test_sort_by_time_returns_chronological_order() -> None:
    """Sorting Correctness: tasks come back ordered by preferred start time."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Evening play", duration_minutes=20, preferred_start=time(17, 0)),
        Task(title="Morning walk", duration_minutes=30, preferred_start=time(8, 0)),
        Task(title="Midday meds", duration_minutes=10, preferred_start=time(12, 0)),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [t.title for t in ordered] == ["Morning walk", "Midday meds", "Evening play"]


def test_untimed_tasks_sort_last() -> None:
    """Edge case: a task with no preferred_start sorts after timed tasks, not first."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Anytime brushing", duration_minutes=10),  # no preferred_start
        Task(title="Morning walk", duration_minutes=30, preferred_start=time(8, 0)),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert ordered[0].title == "Morning walk"
    assert ordered[-1].title == "Anytime brushing"


def test_completing_daily_task_creates_next_days_occurrence() -> None:
    """Recurrence Logic: completing a daily task adds a fresh task due the next day."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Cocoa", species="dog")
    owner.add_pet(pet)
    task = Task(title="Morning walk", duration_minutes=30, frequency="daily")
    pet.add_task(task)
    assert len(pet.tasks) == 1

    scheduler = Scheduler()
    next_task = scheduler.complete_recurring_task(task, owner, pet_name="Cocoa")

    # A new occurrence was created and attached to the pet.
    assert next_task is not None
    assert len(pet.tasks) == 2
    assert next_task.completed is False
    assert next_task.title == "Morning walk"
    # The original was marked complete and its next due date is tomorrow.
    assert task.completed is True
    assert task.next_due_date == date.today() + timedelta(days=1)


def test_scheduler_flags_tasks_at_duplicate_times() -> None:
    """Conflict Detection: two tasks sharing a start time raise a warning."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Morning walk", duration_minutes=30, preferred_start=time(8, 0), pet_name="Cocoa"),
        Task(title="Feed", duration_minutes=10, preferred_start=time(8, 0), pet_name="Luna"),
    ]

    warnings = scheduler.warn_conflicts(tasks)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_untimed_tasks_are_not_a_conflict() -> None:
    """Edge case (regression): tasks with no set time must not be flagged as conflicting."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Brush", duration_minutes=5),   # no preferred_start
        Task(title="Cuddle", duration_minutes=5),  # no preferred_start
    ]

    assert scheduler.warn_conflicts(tasks) == []
