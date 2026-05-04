from __future__ import annotations
import json
from google import genai
from google.genai import types
from pawpal_system import Owner

SYSTEM_PROMPT = """You are PawPal+, a friendly pet care scheduling assistant.

Your job is to have a short conversation with the pet owner to gather the constraints you need, then produce a daily schedule for their pet(s).

## Conversation flow
1. Greet the owner and ask what time they wake up.
2. Ask what time they go to bed (or when the pet should stop having activities).
3. Ask if there are any times during the day the owner is unavailable (e.g. work hours, school run).
4. Once you have enough information, generate the schedule.

## Schedule generation rules
- Only schedule tasks within the owner's stated waking window.
- Respect any blocked-out periods they mention.
- Order tasks chronologically.
- For each task explain *why* it was placed at that time (e.g. "Walking before breakfast helps digestion").
- Detect and flag any conflicts (overlapping tasks).
- Use the pet and task data provided in the user message — do not invent tasks.

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
      "reason": "Walking first thing boosts energy and prevents restlessness later."
    }
  ],
  "conflicts": ["Optional warning strings if any tasks overlap"],
  "summary": "A short paragraph summarising the day."
}

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
        text = reply.strip()
        # Strip markdown code fences if the model wrapped the JSON
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            data = json.loads(text)
            if "schedule" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    def reset(self):
        """Start a fresh conversation."""
        self._history = []
