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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
