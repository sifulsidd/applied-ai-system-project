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

## Features

### Sorting by Time
`Scheduler.sort_by_time()` parses each task's time string (e.g. `"08:00 AM"`) into a `datetime` object and returns all tasks in chronological order. This powers both the task table display and the generated schedule view.

### Conflict Detection
`Scheduler.detect_conflicts()` checks every pair of tasks across all pets using a standard interval overlap formula: two tasks conflict when `start_a < end_b` and `start_b < end_a`. Each task's end time is computed by adding its `duration` (in minutes) to its start time. Conflicts are returned as human-readable warning strings.

### Daily and Weekly Recurrence
`Task.mark_complete()` marks a task as done and automatically creates the next occurrence. Daily tasks get a new `Task` scheduled for the next day (`date + 1 day`); weekly tasks recur 7 days later (`date + 7 days`). Monthly tasks return `None` — no auto-scheduling.

### Priority Levels
Each `Task` carries a `priority` field (`"low"`, `"medium"`, or `"high"`, defaulting to `"medium"`). Priority is displayed in the UI with color-coded icons (🔴 high, 🟡 medium, 🟢 low) and is preserved when a recurring task is auto-created by `mark_complete()`.

### Filtering by Status and Frequency
`Scheduler.filter_by_status()` returns only completed or only pending tasks from any list. `Scheduler.get_tasks_by_frequency()` filters tasks across all pets to a specific frequency (`"daily"`, `"weekly"`, or `"monthly"`). Both are available as standalone utilities on the `Scheduler`.

### Per-Pet Task Grouping
`Scheduler.get_tasks_by_pet()` returns a dictionary mapping each pet's name to its task list, making it easy to view or process tasks on a per-animal basis.


## Testing PawPal+
USE COMMAND:
```
pytest 
```

My tests cover:
1. Ensuring mark_complete marks a task as completed
2. Making sure tests are getting added
3. Verifying that the tasks get sort based on the time they provide 
4. Testing that after completing a task the recurs daily, it adds a new task 
5. If there are conflicts, it detects it

Currently I would give my system 3 stars. It is implementing everything correctly, but there could be more additions that make it complete. 


## 📸 Demo

<a href="images/streamlitapp.png" target="_blank">
  <img src='images/streamlitapp.png' alt='PawPal+ demo 1'>
</a>
<a href="images/streamlitapp1.png" target="_blank">
  <img src='images/streamlitapp1.png' alt='PawPal+ demo 2'>
</a>
<a href="images/uml-final.png" target="_blank">
  <img src='images/uml-final.png' alt='UML Final Diagram'>
</a>