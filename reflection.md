# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ is built around three things a pet owner should always be able to do:

1. **Add a pet (and owner info).** The owner enters their name and registers one or more pets (name, species). This gives the app someone to plan for and a place to attach care tasks.
2. **Add / schedule a care task for a pet.** The owner records a task such as a walk, feeding, or medication, along with how long it takes (duration) and how important it is (priority). Tasks belong to a specific pet.
3. **Generate and view today's plan.** The owner asks PawPal+ to build a daily schedule. The system orders the pet's tasks based on constraints like priority and available time, then displays the plan clearly so the owner knows what to do and when.

**a. Initial design**

- My initial UML design focused on a small domain model with one class for the pet owner and pet, one class for each care task, one scheduler class, and one class for the generated daily plan.

- The main classes were:
  - `Pet`: stores the pet's name, species, age, and any pet-specific preferences.
  - `User`: stores the owner name, available time, preferred schedule start, and general preferences.
  - `Task`: represents a single pet care task with title, duration, priority, category, and optional metadata.
  - `Schedule`: holds the task list, sorts tasks by priority and duration, and builds the today's plan based on available minutes.
  - `TodaysPlan`: stores scheduled entries, tracks total planned time, and provides human-readable summary and explanation methods.

- Responsibilities were divided so that `Task` and `Pet` are simple data objects, `User` encapsulates owner constraints, `Schedule` performs the planning logic, and `TodaysPlan` holds the output and explains why tasks were chosen.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

*Describe one tradeoff your scheduler makes.*

My `Scheduler.warn_conflicts()` / `find_time_conflicts()` methods detect conflicts by **exact preferred-start-time matches**, not by **overlapping durations**. Tasks are bucketed by their `preferred_start` time, and any time slot holding more than one task is flagged as a conflict. This means two tasks that start at the same time (e.g., a 08:00 walk and an 08:00 tooth-brushing) are caught, but two tasks whose *durations* overlap are not — a 30-minute walk at 08:00 and a feeding at 08:15 fall in different buckets and raise no warning, even though they physically collide.

*Why is that tradeoff reasonable for this scenario?*

The exact-match approach is reasonable for a pet-care planner because it is simple, fast, and predictable. It runs in a single O(n) pass (group by time, flag buckets with more than one task) with no interval math, so the logic is easy to read, test, and trust. For a busy owner, the most common real mistake is scheduling two things at the *same* clock time, which is exactly what this catches. Full overlap detection would need every task to have both a start time and a reliable duration and would add O(n²)-style interval comparisons and more edge cases (back-to-back vs. truly overlapping). I chose to keep the core conflict check lightweight and readable, and I left the stronger interval-overlap check available separately in `detect_schedule_conflicts()`, which runs against an already-built daily plan when I do want to catch duration overlaps.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase, but for different jobs:

- **Design brainstorming** — turning my three core actions into a UML class diagram and a class skeleton.
- **Implementation** — fleshing out the Phase 4 algorithmic layer: `sort_by_time`, `filter_tasks`, recurrence (`create_next_occurrence`/`complete_recurring_task`), and conflict detection (`warn_conflicts`/`find_time_conflicts`).
- **Refactoring and review** — asking "how could this algorithm be simplified for better readability or performance?" on my conflict-detection code.
- **Debugging and integration** — wiring `pawpal_system.py` into `app.py` via `st.session_state`, and generating the test suite in `tests/test_pawpal.py`.
- **Documentation** — drafting docstrings, the README Features/Smarter Scheduling/Demo sections, and updating the UML to `uml_final.mmd`.

The most helpful prompts were **specific and file-anchored**: attaching `pawpal_system.py` and asking a narrow question (e.g., "how should the `Scheduler` retrieve all tasks from the `Owner`'s pets?" or "what edge cases should I test for sorting and recurring tasks?") gave far better answers than broad "build me a scheduler" requests. Asking for a *plan or a list of options* before code also helped me stay the decision-maker.

**b. Judgment and verification**

One clear moment: my conflict detector originally grouped **un-timed** tasks (no `preferred_start`) into a shared bucket and reported two of them as a "conflict." The AI-generated grouping looked reasonable, but I rejected that behavior — two tasks with no set time aren't scheduled at the same time, so it was a false positive. I changed `find_time_conflicts` to skip tasks with no `preferred_start` and added a regression test (`test_untimed_tasks_are_not_a_conflict`) so it can't come back.

I also **rejected a "more Pythonic" suggestion**: collapsing the grouping into a one-line `itertools.groupby`. It required pre-sorting the input and was harder to read for no real gain at this scale, so I kept the explicit dictionary grouping.

I verified AI suggestions three ways: (1) running `python main.py` and reading the actual schedule/conflict output, (2) running `python -m pytest` after each change, and (3) writing a small edge-case script (empty list, un-timed tasks, single task) to confirm `warn_conflicts` returns messages instead of crashing. I treated "it looks right" as a starting point, not proof.

---

## 4. Testing and Verification

**a. What you tested**

My suite in `tests/test_pawpal.py` covers the behaviors most likely to break:

- **Task completion** — `mark_complete()` flips `completed` to `True`.
- **Task addition** — adding a task to a `Pet` increases its task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order.
- **Un-timed sorting (edge case)** — a task with no `preferred_start` sorts *last*, not first.
- **Recurrence logic** — completing a daily task creates a new occurrence on the pet with `next_due_date == today + 1 day`.
- **Conflict detection** — two tasks sharing a start time produce exactly one warning.
- **Un-timed conflict regression** — two un-timed tasks are *not* flagged (locks in the bug fix from section 3b).

These matter because sorting, recurrence, and conflict detection are the "smart" parts of the app — the pieces a user actually relies on and the pieces most likely to regress when I refactor. The two edge-case tests specifically guard behavior that is easy to get subtly wrong.

**b. Confidence**

**Confidence: 3 / 5 stars.** All 7 tests pass and the CLI demo behaves correctly, so I'm confident in the core happy paths (sorting, filtering, single-day planning, exact-time conflicts, daily recurrence). I hold back the last two stars because my conflict detection only checks exact time matches (see 2b), and I haven't tested weekly/monthly recurrence boundaries, capacity overflow, or invalid input as thoroughly.

If I had more time I would test: **duration overlaps** (a 30-min task at 08:00 vs. one at 08:15), **weekly/monthly `next_due_date` math** around month boundaries, **capacity limits** (a task longer than the owner's remaining minutes is skipped), and **input validation** (empty title or `duration <= 0` raising `ValueError`).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the **algorithmic layer and the CLI-first workflow**. Building and verifying the logic in `main.py` and `pytest` *before* touching the Streamlit UI meant that when I connected `app.py`, the backend was already trustworthy and integration was mostly wiring, not debugging. I'm also happy that I caught and fixed a real bug (the un-timed-tasks false conflict) instead of just accepting generated code.

**b. What you would improve**

- **Stronger conflict detection** — promote interval-overlap checking (currently only in `detect_schedule_conflicts` on a built plan) into the core check so near-misses like 08:00 + 08:15 are caught.
- **Remove dead code** — `pawpal.py` is a leftover early design that `app.py` no longer uses; I'd delete it so the diagram and code have a single source of truth.
- **Richer UI** — editing/deleting tasks and marking them complete from the app, plus saving data so it survives a page reload (not just `st.session_state`).

**c. Key takeaway**

The biggest lesson was what it means to be the **lead architect** rather than a passenger. The AI could generate plausible code fast, but it didn't know that un-timed tasks shouldn't conflict, that a `groupby` one-liner wasn't worth the readability cost, or that `app.py` was importing a stale module. Those were *my* calls, made by reading the code, running it, and testing it. AI is a powerful accelerator for drafting and exploring options, but the responsibility for correctness, simplicity, and design coherence stayed with me — and keeping separate chat sessions per phase helped me hold that context without letting the assistant blur the boundaries between design, implementation, and testing.
