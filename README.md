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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```
..................                                                       [100%]
18 passed in 0.06s
=== app still runs ===
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
