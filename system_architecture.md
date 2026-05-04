# PawPal+ System Architecture

```mermaid
flowchart TD
    %% User Entry Points
    USER([👤 User / Human])
    UI[🖥️ Streamlit UI\napp.py]

    USER -->|enters owner, pets, tasks\nor chat prompt| UI

    %% Core Data Model
    subgraph DATA_MODEL["📦 Core Data Model — pawpal_system.py"]
        OWNER[Owner]
        PET[Pet]
        TASK[Task\ntime · duration · frequency\npriority · completed · date]
        OWNER -->|has many| PET
        PET -->|has many| TASK
    end

    UI -->|creates / manages| DATA_MODEL

    %% Rule-Based Path
    subgraph RULE_PATH["⚙️ Rule-Based Scheduling Path"]
        SCHEDULER[Scheduler]
        GET_TASKS[get_all_tasks\nget_pending_tasks\nget_tasks_by_pet\nsort_by_time]
        CONFLICT[detect_conflicts\ninterval overlap check\nstart_a < end_b AND start_b < end_a]
        RECUR[Task.mark_complete\nauto-schedule next\ndaily +1d · weekly +7d · monthly → None]

        SCHEDULER --> GET_TASKS
        GET_TASKS --> CONFLICT
        CONFLICT --> RECUR
    end

    DATA_MODEL -->|owner passed in| SCHEDULER

    %% AI Agent Path
    subgraph AI_PATH["🤖 AI Agent Path — gemini_agent.py"]
        CTX[build_context_message\nserializes owner/pets/tasks\ninto text block]
        AGENT[PawPalAgent\nconversation history\nmulti-turn dialogue]
        GEMINI[☁️ Gemini 2.5 Flash API\nSystem Prompt:\nconstraint gathering\n+ schedule generation rules]
        PARSE[parse_schedule\nextract JSON from reply\nstrip markdown fences]

        CTX --> AGENT
        AGENT -->|contents + history| GEMINI
        GEMINI -->|raw reply string| PARSE
    end

    DATA_MODEL -->|owner context| CTX
    UI -->|user chat prompt| AGENT

    %% AI Output Schema
    subgraph AI_OUTPUT["📋 AI JSON Output Schema"]
        SCHED_JSON["schedule[]\n  time · task · pet\n  duration_mins\n  priority · reason"]
        CONF_JSON["conflicts[]\n  description of\n  unresolvable overlaps"]
        SUMM_JSON["summary\n  plain-text day overview"]
    end

    PARSE -->|structured dict| AI_OUTPUT

    %% Rule-Based Output
    subgraph RB_OUTPUT["📋 Rule-Based Output"]
        SORTED_TABLE[Sorted Schedule Table\ntime · task · duration\nfrequency · priority · status]
        WARN[⚠️ Conflict Warnings]
    end

    GET_TASKS --> SORTED_TABLE
    CONFLICT --> WARN

    %% Human Review / Testing Points
    subgraph HUMAN_CHECK["🧪 Human & Automated Checks"]
        H_REVIEW[👤 Human Reviews\nAI schedule in UI\nbefore acting on it]
        UNIT_TESTS["🧪 Unit Tests\ntests/test_pawpal.py\n\ntest_task_completion\ntest_task_addition\ntest_sort_by_time\ntest_daily_recurrence\ntest_conflict_detection"]
    end

    AI_OUTPUT --> H_REVIEW
    WARN --> H_REVIEW
    SORTED_TABLE --> H_REVIEW
    DATA_MODEL -.->|tested against| UNIT_TESTS
    SCHEDULER -.->|tested against| UNIT_TESTS

    %% Final Display back to user
    H_REVIEW -->|accepted schedule| USER
    SORTED_TABLE --> UI
    WARN --> UI
    AI_OUTPUT --> UI

    %% Styling
    classDef userNode fill:#4A90D9,color:#fff,stroke:#2c5f8a
    classDef uiNode fill:#7B68EE,color:#fff,stroke:#4B0082
    classDef dataNode fill:#20B2AA,color:#fff,stroke:#008080
    classDef aiNode fill:#FF8C00,color:#fff,stroke:#cc6600
    classDef outputNode fill:#3CB371,color:#fff,stroke:#2d7a52
    classDef checkNode fill:#DC143C,color:#fff,stroke:#8B0000

    class USER userNode
    class UI uiNode
    class OWNER,PET,TASK dataNode
    class CTX,AGENT,GEMINI,PARSE aiNode
    class SORTED_TABLE,WARN,SCHED_JSON,CONF_JSON,SUMM_JSON outputNode
    class H_REVIEW,UNIT_TESTS checkNode
```

## Component Breakdown

### Data Flow Summary

1. **User** enters owner, pets, tasks, or chat prompts via the **Streamlit UI**
2. The UI creates/manages the **Core Data Model** (`Owner → Pet → Task`)
3. The model feeds into either the **Rule-Based** or **AI Agent** path

### Rule-Based Path

- `Scheduler` retrieves and sorts tasks, then `detect_conflicts` runs an interval overlap check
- `Task.mark_complete()` auto-generates the next recurring task

### AI Agent Path

- `build_context_message` serializes all owner/pet/task state into text
- `PawPalAgent` maintains multi-turn history and sends it to **Gemini 2.5 Flash**
- The reply is parsed into a structured JSON schema (`schedule[]`, `conflicts[]`, `summary`)

### Human & Testing Checkpoints

- A human reviews the AI-generated schedule in the UI before acting on it
- Automated unit tests (`tests/test_pawpal.py`) validate the data model and scheduler independently

### Output Schemas

**Rule-Based Output**
| Column | Description |
|--------|-------------|
| Time | Scheduled time (12-hour format) |
| Task | Description |
| Duration | Minutes required |
| Frequency | daily / weekly / monthly |
| Priority | high / medium / low |
| Status | ✅ complete / ⏳ pending |

**AI JSON Output**
```json
{
  "schedule": [
    {
      "time": "08:00 AM",
      "task": "Morning walk",
      "pet": "Buddy",
      "duration_mins": 30,
      "priority": "high",
      "reason": "Moved from 7:00 AM to avoid overlap with feeding"
    }
  ],
  "conflicts": [],
  "summary": "Plain-text overview of the day"
}
```
