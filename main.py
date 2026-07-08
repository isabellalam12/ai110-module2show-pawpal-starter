from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=180, preferred_start_hour=9)

    cocoa = Pet(name="Cocoa", species="dog", age_years=4)
    luna = Pet(name="Luna", species="cat", age_years=2)

    owner.add_pet(cocoa)
    owner.add_pet(luna)

    # Add tasks out of order with various preferred start times
    cocoa.add_task(Task(title="Play fetch", duration_minutes=20, priority="low", category="enrichment", preferred_start=time(17, 0)))
    cocoa.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", category="exercise", preferred_start=time(8, 0)))
    cocoa.add_task(Task(title="Medication", duration_minutes=10, priority="high", category="health", preferred_start=time(12, 0)))
    cocoa.add_task(Task(title="Afternoon nap", duration_minutes=45, priority="low", category="rest"))
    
    luna.add_task(Task(title="Play with feather toy", duration_minutes=20, priority="low", category="enrichment", preferred_start=time(18, 30)))
    luna.add_task(Task(title="Feed wet food", duration_minutes=15, priority="medium", category="feeding", preferred_start=time(18, 0)))
    luna.add_task(Task(title="Grooming", duration_minutes=25, priority="medium", category="health", preferred_start=time(10, 0)))

    # Intentional conflicts to demonstrate conflict detection:
    #   - same pet: Cocoa's "Brush teeth" clashes with "Morning walk" at 08:00
    #   - different pets: Luna's "Give medication" clashes with Cocoa's "Medication" at 12:00
    cocoa.add_task(Task(title="Brush teeth", duration_minutes=5, priority="medium", category="health", preferred_start=time(8, 0)))
    luna.add_task(Task(title="Give medication", duration_minutes=10, priority="high", category="health", preferred_start=time(12, 0)))

    scheduler = Scheduler(max_minutes=180)
    
    # Collect all tasks
    all_tasks = owner.get_all_tasks(include_completed=True)
    
    print("=" * 60)
    print("PawPal Task Manager - Sorting & Filtering Demo")
    print("=" * 60)
    
    print("\n1. ALL TASKS (Unsorted)")
    print("-" * 60)
    for task in all_tasks:
        time_str = task.preferred_start.strftime('%H:%M') if task.preferred_start else 'No time'
        print(f"  • {task.title} ({task.pet_name}) - {task.duration_minutes}min - {time_str}")
    
    print("\n2. SORTED BY TIME (using sort_by_time method)")
    print("-" * 60)
    sorted_by_time = scheduler.sort_by_time(all_tasks)
    for task in sorted_by_time:
        time_str = task.preferred_start.strftime('%H:%M') if task.preferred_start else '23:59 (no time)'
        print(f"  • {time_str} - {task.title} ({task.pet_name})")
    
    print("\n3. FILTER: Cocoa's Tasks Only")
    print("-" * 60)
    cocoa_tasks = scheduler.filter_tasks(all_tasks, pet_name='Cocoa')
    for task in cocoa_tasks:
        time_str = task.preferred_start.strftime('%H:%M') if task.preferred_start else 'No time'
        print(f"  • {task.title} - {time_str}")
    
    print("\n4. FILTER: Luna's Tasks Only")
    print("-" * 60)
    luna_tasks = scheduler.filter_tasks(all_tasks, pet_name='Luna')
    for task in luna_tasks:
        time_str = task.preferred_start.strftime('%H:%M') if task.preferred_start else 'No time'
        print(f"  • {task.title} - {time_str}")
    
    print("\n5. SORTED & FILTERED: Cocoa's Tasks By Time")
    print("-" * 60)
    cocoa_sorted = scheduler.sort_by_time(scheduler.filter_tasks(all_tasks, pet_name='Cocoa'))
    for task in cocoa_sorted:
        time_str = task.preferred_start.strftime('%H:%M') if task.preferred_start else '23:59'
        print(f"  • {time_str} - {task.title}")
    
    # Mark some tasks as completed for filtering demo
    all_tasks[0].mark_complete()
    all_tasks[2].mark_complete()
    
    print("\n6. FILTER: Pending Tasks Only")
    print("-" * 60)
    pending = scheduler.filter_tasks(all_tasks, completed=False)
    print(f"Total pending tasks: {len(pending)}")
    for task in pending:
        print(f"  • {task.title} ({task.pet_name})")
    
    print("\n7. FILTER: Completed Tasks Only")
    print("-" * 60)
    completed = scheduler.filter_tasks(all_tasks, completed=True)
    print(f"Total completed tasks: {len(completed)}")
    for task in completed:
        print(f"  ✓ {task.title} ({task.pet_name})")
    
    print("\n8. DAILY SCHEDULE (Using build_daily_plan)")
    print("=" * 60)
    plan = scheduler.build_daily_plan(owner=owner, plan_date=date.today())
    print(scheduler.get_schedule_summary(plan))
    print()

    print("\n9. CONFLICT DETECTION (Using warn_conflicts)")
    print("-" * 60)
    warnings = scheduler.warn_conflicts(all_tasks)
    if warnings:
        print(f"Found {len(warnings)} time conflict(s):")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  No time conflicts found.")
    print()


if __name__ == "__main__":
    main()
