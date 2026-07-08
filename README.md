# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Today's Schedule
=================
Daily plan:
09:00 — Medication (10 min) [priority: high]
09:10 — Morning walk (30 min) [priority: high]
09:40 — Feed wet food (15 min) [priority: medium]
09:55 — Play with feather toy (20 min) [priority: low]

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================================================ test session starts ============================================================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/bella/Desktop/AI110/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 7 items                                                                                                                           

tests/test_pawpal.py .......                                                                                                          [100%]

============================================================= 7 passed in 0.03s ============================================================
```
Confidence Level: 3 stars

## 📐 Smarter Scheduling

PawPal+ adds a layer of scheduling intelligence on top of the core classes. Each feature below is implemented in [`pawpal_system.py`](pawpal_system.py).

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by `preferred_start` (HH:MM); un-timed tasks sort last. `Scheduler._sort_tasks()` is the richer sort the planner uses (time → priority → duration → title). |
| Filtering | `Scheduler.filter_tasks()` | Filters a task list by pet name and/or completion status. |
| Conflict detection | `Scheduler.warn_conflicts()`, `Scheduler.find_time_conflicts()` | Flags tasks sharing the same start time for the same **or** different pets. `find_time_conflicts()` returns structured data; `warn_conflicts()` wraps it into human-readable warnings and never crashes. `Scheduler.detect_schedule_conflicts()` additionally catches duration **overlaps** in an already-built daily plan. |
| Recurring tasks | `Task.mark_complete()`, `Task.create_next_occurrence()`, `Scheduler.complete_recurring_task()` | Completing a daily/weekly task computes the next due date with `timedelta` and auto-creates the next occurrence on the pet. |

### Building a daily plan

`Scheduler.build_daily_plan()` ties these together: it retrieves and sorts each pet's due tasks, fits them within the owner's available minutes, resolves time collisions via `_has_conflict()`, and returns a plan with a short reason for each choice (`_explain_reason()`). Use `Scheduler.get_schedule_summary()` for a readable summary.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
