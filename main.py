from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=180, preferred_start_hour=9)

    cocoa = Pet(name="Cocoa", species="dog", age_years=4)
    luna = Pet(name="Luna", species="cat", age_years=2)

    owner.add_pet(cocoa)
    owner.add_pet(luna)

    cocoa.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", category="exercise"))
    cocoa.add_task(Task(title="Medication", duration_minutes=10, priority="high", category="health"))
    luna.add_task(Task(title="Feed wet food", duration_minutes=15, priority="medium", category="feeding"))
    luna.add_task(Task(title="Play with feather toy", duration_minutes=20, priority="low", category="enrichment"))

    scheduler = Scheduler(max_minutes=180)
    plan = scheduler.build_daily_plan(owner=owner, plan_date=date.today())

    print("Today's Schedule")
    print("=================")
    print(scheduler.get_schedule_summary(plan))


if __name__ == "__main__":
    main()
