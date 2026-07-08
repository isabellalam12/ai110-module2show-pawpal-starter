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

## ✨ Features

PawPal+ implements the following scheduling algorithms (see [Smarter Scheduling](#-smarter-scheduling) for the exact methods):

- **Sorting by time** — orders tasks chronologically by their preferred start time, with un-timed tasks pushed to the end (`Scheduler.sort_by_time`). The daily planner uses a richer multi-key sort: time, then priority, then duration, then title (`Scheduler._sort_tasks`).
- **Filtering** — narrows a task list by pet name and/or completion status (`Scheduler.filter_tasks`).
- **Priority-aware daily planning** — builds a one-day schedule that places tasks in order, fits them within the owner's available minutes (skipping any that don't fit), and attaches a short "why" reason to each entry (`Scheduler.build_daily_plan`).
- **Conflict warnings** — flags when two or more tasks share the same start time, for the same pet **or** different pets, returning readable warning strings instead of crashing (`Scheduler.warn_conflicts` / `find_time_conflicts`). A built plan is additionally checked for duration overlaps (`Scheduler.detect_schedule_conflicts`).
- **Daily / weekly / monthly recurrence** — completing a recurring task computes its next due date with `timedelta` and auto-creates the next occurrence on the pet (`Task.mark_complete`, `Task.create_next_occurrence`, `Scheduler.complete_recurring_task`).
- **Explainable schedule** — every planned task carries a human-readable justification, and the whole plan renders as a readable summary (`Scheduler.get_schedule_summary`).

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

### What the app does

The Streamlit app (`app.py`) is a single page backed by the `Owner`, `Pet`, `Task`, and `Scheduler` classes in `pawpal_system.py`. Your pets and tasks are kept in `st.session_state`, so they persist as you interact with the page. From the UI a user can:

- **Set the owner name** and **add one or more pets** (name + species). Duplicate pet names are rejected with a warning.
- **Add tasks to a pet** — title, duration, priority, an optional preferred start time, and a frequency (one-time / daily / weekly / monthly).
- **View all current tasks** in a sorted, filterable table (filter by a specific pet or show all).
- **See conflict warnings** automatically whenever two tasks share a start time.
- **Generate today's plan** with one button, shown as a table with a plain-English reason for each task.

### Example workflow

1. **Add a pet** — type `Cocoa`, pick `dog`, and click **Add pet**. A success banner confirms it.
2. **Add tasks** — add `Morning walk` (30 min, high, 08:00), `Brush teeth` (5 min, medium, 08:00), and `Evening play` (20 min, low, 17:00) for Cocoa.
3. **Review the task table** — the tasks appear sorted by time (08:00 entries first, 17:00 last), with a caption showing how many tasks are displayed and the active filter.
4. **Notice the conflict warning** — because *Morning walk* and *Brush teeth* both start at 08:00, a `⚠️` warning appears; if there were no clashes, a green "No scheduling conflicts" message shows instead.
5. **Generate the schedule** — click **Generate schedule** to see today's plan in a table (Time / Pet / Task / Duration / Priority / **Why**), with the 08:00 clash resolved by shifting the second task later.

### Key Scheduler behaviors shown

- **Sorting by time** (`sort_by_time`) — the task table and plan are ordered chronologically; un-timed tasks sort last.
- **Filtering** (`filter_tasks`) — the "Filter by pet" selector narrows the table to one pet.
- **Conflict warnings** (`warn_conflicts`) — same-time tasks are flagged for the same or different pets, as `st.warning` banners.
- **Priority-aware planning** (`build_daily_plan`) — tasks are placed in order within the owner's available minutes, each with an explanation.
- **Recurrence** (`complete_recurring_task`) — completing a daily/weekly task creates its next occurrence.

### Sample CLI output

The same logic is exercised end-to-end by `main.py`. Running `python main.py` produces:

```text
============================================================
PawPal Task Manager - Sorting & Filtering Demo
============================================================

1. ALL TASKS (Unsorted)
------------------------------------------------------------
  • Play fetch (Cocoa) - 20min - 17:00
  • Morning walk (Cocoa) - 30min - 08:00
  • Medication (Cocoa) - 10min - 12:00
  • Afternoon nap (Cocoa) - 45min - No time
  • Brush teeth (Cocoa) - 5min - 08:00
  • Play with feather toy (Luna) - 20min - 18:30
  • Feed wet food (Luna) - 15min - 18:00
  • Grooming (Luna) - 25min - 10:00
  • Give medication (Luna) - 10min - 12:00

2. SORTED BY TIME (using sort_by_time method)
------------------------------------------------------------
  • 08:00 - Morning walk (Cocoa)
  • 08:00 - Brush teeth (Cocoa)
  • 10:00 - Grooming (Luna)
  • 12:00 - Medication (Cocoa)
  • 12:00 - Give medication (Luna)
  • 17:00 - Play fetch (Cocoa)
  • 18:00 - Feed wet food (Luna)
  • 18:30 - Play with feather toy (Luna)
  • 23:59 (no time) - Afternoon nap (Cocoa)

5. SORTED & FILTERED: Cocoa's Tasks By Time
------------------------------------------------------------
  • 08:00 - Morning walk
  • 08:00 - Brush teeth
  • 12:00 - Medication
  • 17:00 - Play fetch
  • 23:59 - Afternoon nap

8. DAILY SCHEDULE (Using build_daily_plan)
============================================================
Daily plan:
09:00 — Morning walk (30 min) [priority: high]
09:30 — Brush teeth (5 min) [priority: medium]
10:00 — Grooming (25 min) [priority: medium]
12:00 — Give medication (10 min) [priority: high]
18:00 — Feed wet food (15 min) [priority: medium]
18:30 — Play with feather toy (20 min) [priority: low]
18:50 — Afternoon nap (45 min) [priority: low]

9. CONFLICT DETECTION (Using warn_conflicts)
------------------------------------------------------------
Found 2 time conflict(s):
  ⚠️  Conflict at 08:00: 2 tasks are scheduled at the same time — 'Morning walk' (Cocoa), 'Brush teeth' (Cocoa).
  ⚠️  Conflict at 12:00: 2 tasks are scheduled at the same time — 'Medication' (Cocoa), 'Give medication' (Luna).
```

*(Sections 3, 4, 6, and 7 — the per-pet and completed/pending filters — are omitted above for brevity; run `python main.py` to see the full output.)*

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
