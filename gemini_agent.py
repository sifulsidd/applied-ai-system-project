from __future__ import annotations
import json
import re
from google import genai
from google.genai import types
from pawpal_system import Owner

SYSTEM_PROMPT = """You are PawPal+, a friendly pet care scheduling assistant.

Your job is to have a short conversation with the pet owner to gather their daily constraints, then produce a conflict-free daily schedule for their pet(s).

## Conversation flow
1. Greet the owner and ask what time they wake up.
2. Ask what time they go to bed (or when the pet should stop having activities).
3. Ask if there are any times during the day the owner is unavailable (e.g. work hours, school run).
4. Once you have enough information, generate the schedule.

## Schedule generation rules
- NEVER place two tasks at the same time. If tasks overlap or share the same start time, redistribute them.
- Compute available time slots: the period from wake time to bedtime, minus any busy/unavailable blocks the owner mentioned.
- Spread tasks evenly across the available slots. Chain them back-to-back with short gaps (5–10 mins) between them so nothing overlaps.
- Prioritise higher-priority tasks earlier in the day within the available window.
- Only schedule tasks within the owner's stated waking window and outside their busy periods.
- Order the final schedule chronologically.
- For each task explain *why* it was placed at that specific time. If the task's original time conflicted with another task and had to be moved, explicitly say so in the reason (e.g. "Originally set for 08:00 AM but moved to 08:25 AM to avoid overlap with Morning Walk.").
- If after redistribution all tasks fit without conflict, the "conflicts" array must be empty.
- Use only the pet and task data provided — do not invent tasks.

## Redistribution example
If wake time is 08:00 AM, bedtime is 10:00 PM, busy 09:00–17:00, and three tasks each say 08:00 AM:
- Place task 1 (highest priority) at 08:00 AM
- Place task 2 at 08:00 AM + duration of task 1 + 5 min gap
- Place task 3 at end of task 2 + 5 min gap
- Remaining tasks after 17:00 PM fill the evening window

## Output format when generating the schedule
Respond with a JSON object **only** (no markdown fences) in this exact shape:
{
  "schedule": [
    {
      "time": "08:00 AM",
      "task": "Morning walk",
      "pet": "Mochi",
      "duration_mins": 20,
      "priority": "high",
      "reason": "Scheduled first thing before the owner's busy period. Originally set for 08:00 AM — moved to 08:25 AM to avoid overlap with Morning Walk.",
      "confidence": 92,
      "confidence_label": "high"
    }
  ],
  "conflicts": [],
  "summary": "A short paragraph summarising the day."
}

## Confidence scoring rules
For every scheduled task, assign a `confidence` integer from 0–100 and a `confidence_label` of "high", "medium", or "low":
- **High (75–100):** The task fits cleanly inside the owner's stated window, no overlap, no ambiguity.
- **Medium (40–74):** The task was redistributed to resolve a conflict, is placed close to a busy boundary, or the owner's constraints were vague for this time slot.
- **Low (0–39):** The task barely fits, the time window was unclear, the task had to be placed outside the owner's stated preferences, or you are unsure the placement is ideal.

Be honest — if you moved a task to resolve a conflict and are not sure the new slot suits the owner, score it medium or low. Do not give everything 100.

If you still need more information before generating the schedule, respond with plain conversational text (not JSON).
"""


def build_context_message(owner: Owner) -> str:
    """Serialize the current owner/pet/task state into a context block for the agent."""
    lines = [f"Owner: {owner.name}", "Pets and their tasks:"]
    for pet in owner.pets:
        lines.append(f"  - {pet.name} (age {pet.age})")
        if pet.tasks:
            for task in pet.tasks:
                lines.append(
                    f"      * {task.description} | {task.time} | {task.duration} mins | "
                    f"{task.frequency} | priority: {task.priority}"
                )
        else:
            lines.append("      (no tasks yet)")
    return "\n".join(lines)


class PawPalAgent:
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        )
        self._history: list[types.Content] = []

    def send_message(self, user_text: str, owner: Owner | None = None) -> str:
        """Send a message, maintain history manually, and return the reply."""
        if owner is not None:
            context = build_context_message(owner)
            full_message = f"{user_text}\n\n[Current pet/task data]\n{context}"
        else:
            full_message = user_text

        self._history.append(types.Content(role="user", parts=[types.Part(text=full_message)]))

        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self._history,
            config=self._config,
        )

        reply = response.text
        self._history.append(types.Content(role="model", parts=[types.Part(text=reply)]))
        return reply

    def parse_schedule(self, reply: str) -> dict | None:
        """Try to parse a JSON schedule out of the reply. Returns None if not JSON."""
        # Extract the first {...} block from the reply, ignoring surrounding text or fences
        match = re.search(r'\{.*\}', reply, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group())
            if "schedule" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    def reset(self):
        """Start a fresh conversation."""
        self._history = []
