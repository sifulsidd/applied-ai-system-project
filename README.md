# PawPal+

A pet care scheduling system that combines rule-based task management with a conversational AI assistant powered by Google Gemini.

---

## Original Project (Modules 1–3): PawPal

The original project, **PawPal**, was a pure Python scheduling system for managing pet care tasks. Its goals were to model the relationship between owners, their pets, and recurring care tasks (feeding, walks, vet checkups), detect scheduling conflicts using interval overlap logic, and auto-schedule the next occurrence of a task when the current one was marked complete. It had no AI component — all logic was deterministic and rule-based, driven by the `Owner`, `Pet`, `Task`, and `Scheduler` classes in `pawpal_system.py`.

---

## Title and Summary

**PawPal+** extends the original project with a Streamlit web UI and a conversational AI scheduling assistant. Instead of only flagging conflicts after the fact, the AI agent gathers the owner's daily constraints (wake time, bedtime, unavailable blocks) through natural dialogue and then generates a conflict-free, chronologically ordered schedule — explaining why each task was placed where it was. The project matters because real pet care schedules are dynamic: owners have jobs, errands, and varying routines. A system that can reason about those constraints and redistribute tasks intelligently is far more useful than one that only reports problems.

---

## Architecture Overview

The system has two parallel scheduling paths that share the same core data model:

```
User Input (Streamlit UI)
        │
        ▼
Core Data Model (Owner → Pet → Task)
        │
   ┌────┴─────┐
   ▼          ▼
Rule-Based   AI Agent Path
Scheduler    (PawPalAgent + Gemini 2.5 Flash)
   │          │
   ▼          ▼
Sorted     Structured JSON Schedule
Schedule   {schedule[], conflicts[], summary}
+ Conflict
  Warnings
        │
        ▼
  Human Review (UI display)
        │
  Automated Tests (pytest)
```

- **Rule-based path** — instant, deterministic. Sorts tasks chronologically and flags overlapping time windows using interval algebra (`start_a < end_b AND start_b < end_a`).
- **AI path** — conversational. `PawPalAgent` serializes the current owner/pet/task state into a context block and sends it to Gemini along with the conversation history. The model gathers constraints over multiple turns, then outputs a JSON schedule that redistributes conflicting tasks.
- **Human checkpoint** — the AI-generated schedule is displayed in the UI for the owner to review before acting on it. No tasks are auto-applied from the AI output.

See [system_architecture.md](system_architecture.md) for the full Mermaid.js diagram.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd applied-ai-system-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

You can get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### 6. (Optional) Run the CLI demo

```bash
python main.py
```

### 7. Run the test suite

```bash
pytest tests/
```

---

## Sample Interactions

### Example 1 — Rule-Based Conflict Detection

**Input:** Owner "Alex" with two pets. Buddy has a Morning Walk at 07:00 AM (30 mins). Luna has Morning Grooming at 07:15 AM (15 mins). Click **Generate Schedule**.

**Output:**

| Time | Task | Duration | Frequency | Priority | Status |
|------|------|----------|-----------|----------|--------|
| 07:00 AM | Morning walk | 30 mins | daily | 🔴 high | ⏳ |
| 07:15 AM | Morning grooming | 15 mins | daily | 🟡 medium | ⏳ |
| 08:00 AM | Feed breakfast | 10 mins | daily | 🔴 high | ⏳ |

> ⚠️ WARNING: 'Morning walk' (Buddy, 07:00 AM, 30 mins) overlaps with 'Morning grooming' (Luna, 07:15 AM, 15 mins).

---

### Example 2 — AI Schedule Generation (Multi-Turn Dialogue)

**Turn 1 — AI greeting:**
> Hi! I'm PawPal+. To build a conflict-free schedule, what time do you usually wake up?

**Turn 2 — User:** `7am`

**AI:** Great! And what time should we stop scheduling activities for the day?

**Turn 3 — User:** `10pm`

**AI:** Got it. Are there any blocks during the day when you're unavailable — like work hours or a school run?

**Turn 4 — User:** `I'm at work 9am to 5pm`

**AI output (JSON rendered as table):**

| Time | Pet | Task | Duration | Priority | Confidence | Reason |
|------|-----|------|----------|----------|------------|--------|
| 07:00 AM | Buddy | Morning walk | 30 mins | 🔴 High | 🟢 95% (High) | First available slot after wake time. |
| 07:35 AM | Luna | Morning grooming | 15 mins | 🟡 Medium | 🟡 62% (Medium) | Originally 07:15 AM — moved to 07:35 AM to avoid overlap with Morning walk. |
| 07:55 AM | Buddy | Feed breakfast | 10 mins | 🔴 High | 🟢 88% (High) | Chained after grooming with a 5-min gap. |
| 05:05 PM | Luna | Evening walk | 20 mins | 🟡 Medium | 🟡 71% (Medium) | First slot after work block ends at 5:00 PM; tight window before bedtime. |

> Summary: All tasks fit within the 7 AM–10 PM window. Morning tasks are front-loaded before work. Evening task placed immediately after the work block.

**Confidence legend:** 🟢 High (75–100%) — clean fit · 🟡 Medium (40–74%) — redistributed or near a boundary · 🔴 Low (0–39%) — placement uncertain

---

### Example 3 — Task Completion and Auto-Recurrence (CLI)

**Input (`main.py`):** Mark Buddy's Morning Walk as complete.

**Output:**
```
Completing: [Pending] [HIGH] Morning walk at 07:00 AM (30 mins, daily)
Next occurrence scheduled: Morning walk on 2026-05-04
```

Monthly tasks return no next occurrence:
```
Completing: [Pending] [HIGH] Vet checkup at 10:00 AM (60 mins, monthly)
Monthly task — no auto-scheduling. Book next appointment manually.
```

---

## Design Decisions

### Dataclass-based data model
`Task`, `Pet`, and `Owner` are plain Python dataclasses. This keeps the model readable and avoids the overhead of an ORM or database for a project at this scope. The trade-off is that state lives only in memory — refreshing the page resets everything.

### Manual conversation history in `PawPalAgent`
The Gemini SDK does not automatically persist history between calls, so `PawPalAgent` maintains its own `_history` list of `Content` objects and passes the full list on every request. This keeps the agent stateful across turns without needing a session store, at the cost of growing token usage as the conversation lengthens.

### Two parallel scheduling modes
Rather than replacing the rule-based scheduler with AI, both paths coexist. The rule-based path is instant and deterministic — useful for quick checks. The AI path is conversational and adaptive — useful when the owner's real-world constraints matter. The trade-off is added UI complexity, but it lets users choose the right tool for their context.

### JSON output contract for the AI
The system prompt specifies an exact JSON schema (`schedule[]`, `conflicts[]`, `summary`). This makes `parse_schedule()` simple and reliable. The trade-off is that the model occasionally wraps the JSON in markdown fences, which the parser strips before decoding.

### Confidence scoring on AI output
Each scheduled task carries a `confidence` integer (0–100) and a `confidence_label` ("high", "medium", "low") set by the model. The scoring rules are encoded in the system prompt: a task that fits cleanly scores high; one that was redistributed to resolve a conflict, sits near a busy boundary, or had ambiguous constraints scores medium or low. This lets the owner immediately see which parts of the AI schedule are solid and which deserve a second look — without having to read every reasoning note. The trade-off is that the model self-reports confidence, so it is a reflection of its own uncertainty rather than a verified measure of correctness.

### No database persistence
All state is held in `st.session_state`. This was a deliberate choice to keep the setup frictionless (no migrations, no connection strings). The trade-off is that schedules are not saved between sessions.

---

## Testing Summary

Five pytest unit tests cover the core scheduling logic:

| Test | What it checks | Result |
|------|----------------|--------|
| `test_task_completion` | `mark_complete()` flags done and returns correct next date for daily, weekly, monthly | ✅ Pass |
| `test_task_addition` | `Pet.add_task()` grows the task list; recurrence adds a second entry | ✅ Pass |
| `test_sort_by_time` | Chronological ordering, empty list, single task, same-time stability, midnight vs noon | ✅ Pass |
| `test_daily_recurrence` | Chained completions advance date by 1 day each time; all properties inherited | ✅ Pass |
| `test_conflict_detection` | Overlaps detected, back-to-back tasks not flagged, empty/single-task edge cases | ✅ Pass |

**What worked well:** Conflict detection logic using interval algebra proved robust — the `start_a < end_b AND start_b < end_a` formula correctly handles all overlap and boundary cases including same-time tasks on different pets.

**What didn't work / limitations discovered:**
- The scheduler does not consider tasks on different dates. A daily task on Day 1 and Day 2 are treated as independent, even if they would logically conflict in a weekly view.
- The AI agent's schedule is not automatically written back to the data model — it requires manual re-entry by the user.
- Long conversations cause token counts to grow since the full history is passed on every turn.

**What was learned:** Writing tests before adding the AI layer made it easy to confirm the rule-based foundation was solid before layering non-deterministic behavior on top. Boundary conditions (midnight, back-to-back tasks, empty state) are where simple schedulers most often fail — testing them explicitly paid off.

---

## Reflection

Building PawPal+ taught me that AI is most useful when it handles the parts of a problem that are hard to express as rules — in this case, the owner's personal constraints. Writing a rule that says "schedule tasks only when the owner is awake and not at work" requires parsing natural language and applying contextual judgment. The Gemini model handles this naturally through conversation, while the rule-based scheduler handles the deterministic parts (sorting, overlap detection) more reliably and transparently.

The biggest lesson was about prompt engineering as system design. The system prompt in `gemini_agent.py` is not just instructions — it is the contract between the application and the model. Getting the redistribution logic, JSON output format, and conflict reasoning right in the prompt took iteration, and changes to it affected behavior in non-obvious ways. Treating the prompt as code — versioned, tested against expected outputs, and kept minimal — is the right approach.

Working on this project also reinforced that AI tools augment judgment rather than replace it. Every AI-generated schedule in this system is reviewed by a human before being acted on. That human checkpoint is not a limitation — it is the correct architecture for a system where the stakes (a pet's health routine) require the owner to stay in the loop.
