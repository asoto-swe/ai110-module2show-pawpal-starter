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

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
Today's Schedule for Jordan

TIME   TASK                PET          DURATION  PRIORITY
----------------------------------------------------------
07:30  Morning walk (!)    Mochi (dog)  30 min    HIGH
08:15  Feed breakfast (!)  Luna (cat)   10 min    HIGH
12:00  Clean litter box    Luna (cat)   10 min    MEDIUM
18:00  Evening walk        Mochi (dog)  20 min    MEDIUM

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest

# Optional: run with coverage
python -m pytest --cov
```

### What the tests cover

The suite lives in [`tests/`](tests/) and covers the core scheduling behaviors:

- **Sorting correctness** — tasks come back in chronological order (`sort_by_time`) and in
  priority order with proper tie-breaking (`sort_tasks`), including untimed tasks sorting last.
- **Recurrence logic** — completing a `daily` task creates a new task for the following day (and
  `weekly` advances a week), while one-off tasks and tasks without a `due_time` spawn nothing.
- **Conflict detection** — the scheduler flags tasks that share the same start time
  (`conflict_warnings`) and stays quiet when times differ.
- **Filtering** — tasks can be narrowed by completion status and by pet.
- **Data-model integrity** — pets and owners don't share mutable lists, and `build_daily_plan`
  gathers tasks across every pet.


## 📐 Smarter Scheduling

All scheduling logic lives in the `Scheduler` class in [`pawpal_system.py`](pawpal_system.py),
with recurrence helpers on `Task` and completion handling on `Pet`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | `sort_tasks` orders by priority → time → shortest duration; `sort_by_time` orders purely by scheduled time (untimed tasks last). |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter by completion status (e.g. only `"pending"`) or by a pet's name. Both are case-insensitive. |
| Conflict handling | `Scheduler.conflict_warnings()`, `Scheduler.find_conflicts()` | `conflict_warnings` is a lightweight, non-crashing check that returns warning strings for tasks sharing the exact same start time; `find_conflicts` is the deeper, duration-aware overlap check. |
| Recurring tasks | `Task.recurrence`, `Task.spawn_next()`, `Pet.complete_task()`, `Scheduler.get_recurring_tasks()`, `Scheduler.next_occurrence()` | Tasks carry a `recurrence` of `"none"`/`"daily"`/`"weekly"`. Completing a recurring task via `Pet.complete_task()` auto-creates the next occurrence. `get_recurring_tasks` lists repeating tasks; `next_occurrence` reports when one next falls due. |

### Feature details

- **Sorting** — `sort_tasks()` is the planner's default ordering (priority first, so a `high`
  task is never buried behind a `low` one). `sort_by_time()` gives a pure chronological view for
  displaying a timeline.
- **Filtering** — `filter_by_status()` powers "hide completed tasks"; `filter_by_pet()` narrows
  the view to a single pet's care tasks.
- **Conflict detection** — `conflict_warnings()` groups tasks by `due_time` and flags any slot with
  more than one task (same pet *or* different pets), returning messages rather than raising.
  `find_conflicts()` additionally catches partial overlaps using each task's `duration_minutes`.
- **Recurring tasks** — a `"daily"` or `"weekly"` task, when completed through
  `Pet.complete_task()`, spawns a fresh pending copy at its next occurrence (`Task.spawn_next()`),
  so the routine keeps rolling forward without manual re-entry.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->


### Successful test run

```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\alexa\OneDrive\Documents\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0, respx-0.23.1
collected 27 items

tests\test_pawpal.py .........                                           [ 33%]
tests\test_pawpal_system.py ..................                           [100%]

============================= 27 passed in 0.05s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4 / 5)

All 27 tests pass and cover the core sorting, recurrence, filtering, and conflict-detection
paths plus key edge cases. I held back the fifth star because a few edge cases are still
untested — recurrence that *chains* across multiple completions, duplicate/not-found pet lookups,
and the exact adjacency boundary in the duration-aware `find_conflicts` (a task ending exactly
when the next begins). Once those are covered I'd rate it 5/5.