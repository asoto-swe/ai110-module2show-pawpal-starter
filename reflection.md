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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is in how I warn about conflicts. My lightweight `conflict_warnings()` method only flags tasks that share the *exact* same start time (for example two tasks both at 12:00), rather than analyzing whether their durations overlap. This means a 12:00 task lasting 30 minutes and a 12:15 task would not be reported as a clash by the warning, even though they really overlap. I accepted this because exact-time matching is simple, fast, and predictable — it groups tasks by `due_time` and never produces confusing false positives, and it never crashes the program; it just returns warning messages the owner can act on. It is reasonable for a personal pet-care planner where most tasks are entered at round times and the goal is a helpful nudge, not strict calendar enforcement. I also kept a separate, more thorough `find_conflicts()` method that *is* duration-aware, so the deeper overlap check is still available when I want it — the tradeoff is really about keeping the everyday warning cheap and readable while leaving room for stricter checking later.

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
