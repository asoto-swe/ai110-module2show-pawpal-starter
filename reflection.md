# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design used four classes with a clear ownership hierarchy: an Owner owns one or more Pet objects, each Pet has zero or more Task objects, and a separate Scheduler class operates on those objects to produce a daily plan. I modeled the Owner→Pet and Pet→Task relationships as aggregation (the "has-a" collections), and made Scheduler a dependency that reads an Owner and orders Task objects rather than owning any data itself. This keeps the data model (who has what) separate from the behavior (how a plan is built). Owner holds the person's name, their preferences, and their list of pets. Pet holds a name, species, and age. Task has a title, duration, priority, and optional due times and notes. Scheduler is responsible for building the plan and organizing the tasks. 
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
 The four class strucutres stayed the same except a few details. My initial UML showed the associations as diagram lines, but I hadn't listed the actual fields that hold those collections. During implementation I realized the relationships had to be backed by real state, so I added pets: List[Pet] to Owner and tasks: List[Task] to Pet, both using field(default_factory=list). I used default_factory specifically to avoid the shared-mutable-default bug — if I'd written pets: List[Pet] = [], every Owner would silently share the same list. I also added a notes: str field to Task that wasn't in my first sketch. Once I thought about explain_plan() needing to justify why a task was scheduled.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers three constraints, applied in a strict order inside `sort_tasks()`: with priority first, then scheduled time , then duration. So a task's priority decides its place first. Ties are broken by whichever task is due earlier and any remaining ties go to the shorter task. Tasks with no `due_time` sort to the end so they never crowd out timed commits. I decided priority mattered most because a high-priority walk or medication should never be buried behind a low-priority enrichment task just only because the low one happens to be earlier on the clock. Time comes second because an owner naturally wants their day in chronological order. Duration is last as a gentle tiebreaker: when two tasks are otherwise equal, doing the shorter one first is an easy win. The `Owner.preferences` field exists as a place to grow toward richer constraints (like quiet hours), but I kept the core ordering to these three so the logic stays predictable and easy to explain.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is in how I warn about conflicts. My lightweight `conflict_warnings()` method only flags tasks that share the *exact* same start time (for example two tasks both at 12:00), rather than analyzing whether their durations overlap. This means a 12:00 task lasting 30 minutes and a 12:15 task would not be reported as a clash by the warning, even though they really overlap. I accepted this because exact-time matching is simple, fast, and predictable — it groups tasks by `due_time` and never produces confusing false positives, and it never crashes the program; it just returns warning messages the owner can act on. It is reasonable for a personal pet-care planner where most tasks are entered at round times and the goal is a helpful nudge, not strict calendar enforcement. I also kept a separate, more thorough `find_conflicts()` method that *is* duration-aware, so the deeper overlap check is still available when I want it — the tradeoff is really about keeping the everyday warning cheap and readable while leaving room for stricter checking later.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the AI coding assistant across every phase: brainstorming the class responsibilities, converting the UML into Python, implementing the scheduling logic, writing tests, and wiring the backend into the Streamlit UI. The features that were most effective were (1) multi-file edits — the assistant could change `pawpal_system.py`, `main.py`, and the test file together so a new method and its demo and its test all stayed in sync; (2) running the code to verify — instead of just claiming a change worked, it actually ran `python -m pytest` and a headless Streamlit test and showed me the real output, which caught problems immediately; and (3) explain-this-code, which I leaned on to understand things I didn't write myself, like why sorting with `key=lambda t: t.due_time or datetime.max` pushes untimed tasks to the end. The most helpful prompts were specific and outcome-focused ("add a lightweight conflict check that returns a warning instead of crashing") rather than vague ("make it better"), and asking "explain this before I save it" so I never committed logic I couldn't defend.

Using separate chat sessions for each phase kept me organized. A build session stayed focused on implementing features, and a fresh testing session started with a clean context so the assistant wasn't distracted by earlier code and could think purely about edge cases. It also made it easy to go back and find where a decision was made, because each session mapped to one part of the project instead of one giant conversation covering everything.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked how my `conflict_warnings()` method could be simplified, the assistant offered a "more Pythonic" one-line version using a `defaultdict` and a single list comprehension that packed the grouping, the length check, the sort, and the string join into one expression. It was shorter, but I rejected it and kept my explicit loop with a clear `if len(clashing) > 1:` line, because the compact version was harder to read and this is a learning project where I need to be able to explain every line. The performance was identical either way, so readability was the deciding factor. I also modified another suggestion about recurring tasks: rather than putting the "create the next occurrence" logic inside `Task.mark_complete()`, I moved it to `Pet.complete_task()`, because a `Task` doesn't know which `Pet` holds it and therefore can't correctly attach a new instance — the pet owns the list, so the pet should do the attaching. I verified suggestions by running the test suite (all 27 tests passing) and by exercising the real flow in the demo script and the app, not just trusting that the code looked correct.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 27 tests across two files covering the behaviors that matter most for a scheduler. For sorting, I verified that `sort_by_time()` returns tasks in chronological order and that `sort_tasks()` orders by priority with correct tie-breaking. For recurrence, I confirmed that completing a `daily` task creates a new pending task for the next day, that `weekly` advances by a week, and that one-off tasks — and recurring tasks with no `due_time` — spawn nothing. For conflict detection, I checked that `conflict_warnings()` flags two tasks at the same time and stays quiet when times differ. I also tested filtering (by status and by pet) and data-model integrity (that separate pets and owners don't share the same underlying list, and that `build_daily_plan()` gathers tasks across every pet). These tests were important because they cover the exact places where a scheduler quietly goes wrong: an ordering that looks right but isn't, a recurring task that silently fails to repeat, or a shared-list bug that corrupts one pet's tasks when you edit another's. Testing the sorting and recurrence logic gave me confidence that the core promise of the app — a correct, self-renewing daily plan — actually holds.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident — about 4 out of 5. All 27 tests pass, and they cover the main sorting, recurrence, filtering, and conflict paths plus several edge cases, so I trust the core behavior. I held back from full confidence because there are still edge cases I haven't tested. If I had more time I would test: recurrence that chains, duplicate or not-found pet names in `filter_by_pet()`, the exact adjacency boundary in the duration-aware `find_conflicts()`, mixed-case `priority` and `recurrence` values, and empty task lists passed to each method. Those are the spots most likely to hide an off-by-one bug.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the recurring-task feature and how cleanly it fit the design. When a `daily` or `weekly` task is marked complete, the system automatically creates the next occurrence, so the owner's routine keeps rolling forward without re-entering anything. What makes me happy about it isn't just that it works — it's where the logic lives: `Task` computes its own next occurrence (`spawn_next()`), and `Pet` owns the task list so it does the actual attaching (`complete_task()`). That separation of concerns felt like the design "clicking," and it was backed by tests for the daily, weekly, one-off, and no-`due_time` cases so I trust it. I'm also proud that the backend and the Streamlit UI share the exact same `Scheduler` methods, so what I tested is what the user actually sees.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I'd make conflict detection smarter and more visible. Right now the everyday warning only catches tasks at the *exact* same time, and while I do have a duration-aware `find_conflicts()` method, the UI leans on the lighter check. I'd surface true overlap detection in the app and let the scheduler suggest a fix (for example, nudging one task later) instead of just warning. I'd also actually use `Owner.preferences` — honoring quiet hours or a daily time budget so the plan flags when there simply isn't enough time for everything. Finally, I'd cover the edge cases I listed in the testing section (chained recurrence, not-found pet lookups, the `find_conflicts` boundary) to push my confidence from 4 to 5 out of 5.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest thing I learned is what it means to be the "lead architect" when working with a powerful AI tool. The assistant is extremely fast at producing code, tests, and options, but it will happily follow a bad instruction or hand me a clever solution that hurts the design if I let it. My job wasn't to type the most code — it was to own the decisions: where each responsibility lives (data in `Owner`/`Pet`/`Task`, behavior in `Scheduler`), which tradeoffs are acceptable (exact-time conflict warnings vs. full overlap detection), and which "improvements" to reject because they trade readability for cleverness. The AI is the fast builder; I'm the one who has to understand and defend the structure. Concretely, that meant giving specific, outcome-focused prompts, always asking it to explain code before I saved it, and verifying every change by running the tests and the app rather than assuming it was right. The AI made me much faster, but the quality of the final system came from staying the person who decides why the pieces fit together, not just that they run.
