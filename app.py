import os
import streamlit as st
from dotenv import load_dotenv
from pawpal_system import Task, Pet, Owner, Scheduler
from gemini_agent import PawPalAgent

load_dotenv()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

# ADDED: Button to explicitly create and store the Owner in session state.
# Using a button instead of auto-initializing ensures the owner is only created
# when the user confirms, so name changes in the text input are captured correctly.
if st.button("Set Owner"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.scheduler = Scheduler()
    st.success(f"Owner '{owner_name}' saved to session.")

# ADDED: Show the currently stored owner so the user knows what is in the session.
if "owner" in st.session_state:
    st.info(f"Current owner: {st.session_state.owner.name}")

st.markdown("### Add Pet")

# Pet inputs matching the Pet dataclass fields
pet_name = st.text_input("Pet name", value="Mochi")
pet_age = st.number_input("Pet age", min_value=0, max_value=50, value=2)

# ADDED: Uses owner.add_pet() from pawpal_system.py to create and store a Pet
# on the Owner object in session state.
if st.button("Add Pet"):
    if "owner" not in st.session_state:
        st.warning("Please set an owner first.")
    else:
        pet = Pet(name=pet_name, age=pet_age, owner=st.session_state.owner)
        st.session_state.owner.add_pet(pet)
        st.success(f"Pet '{pet_name}' added to {st.session_state.owner.name}.")

# Display all pets currently stored on the owner
if "owner" in st.session_state and st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([{"Name": p.name, "Age": p.age} for p in st.session_state.owner.pets])

st.markdown("### Add Task")
st.caption("Assign a task to one of the owner's pets.")

# Task inputs matching the Task dataclass fields
col1, col2, col3 = st.columns(3)
with col1:
    task_description = st.text_input("Task description", value="Morning walk")
    task_time = st.text_input("Time", value="08:00 AM")
with col2:
    task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
# ADDED: col3 holds the priority selectbox so the user can choose low, medium, or high when adding a task
with col3:
    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)

# ADDED: Uses owner.schedule_task() which calls pet.add_task() from pawpal_system.py.
# Requires an owner to be set in session state first.
if st.button("Add task"):
    if "owner" not in st.session_state:
        st.warning("Please set an owner first.")
    elif not st.session_state.owner.pets:
        st.warning("Please add a pet to the owner before scheduling tasks.")
    else:
        # Assign task to the first pet for now
        pet = st.session_state.owner.pets[0]
        task = Task(
            description=task_description,
            duration=task_duration,
            frequency=task_frequency,
            time=task_time,
            # ADDED: passes the selected priority from the UI into the Task object
            priority=task_priority,
        )
        # Calls pet.add_task() internally via Owner.schedule_task()
        st.session_state.owner.schedule_task(pet, task)
        st.success(f"Task '{task_description}' added to {pet.name}.")

# UPDATED: Replaced the raw task loop with Scheduler.get_all_tasks() and sort_by_time()
# so tasks always display in chronological order rather than insertion order.
if "owner" in st.session_state and "scheduler" in st.session_state:
    # Fetch every task across all pets via the Scheduler helper
    raw_tasks = st.session_state.scheduler.get_all_tasks(st.session_state.owner)

    if raw_tasks:
        # Sort tasks by their time field before building the table
        sorted_tasks = st.session_state.scheduler.sort_by_time(raw_tasks)

        st.markdown("### Current Tasks (sorted by time)")
        table_rows = []
        for task in sorted_tasks:
            # Show a checkmark for completed tasks and a clock for pending ones
            status_icon = "✅" if task.completed else "⏳"
            # Map each priority level to a color-coded dot for quick visual scanning
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
            table_rows.append({
                "Status": status_icon,
                "Time": task.time,
                "Task": task.description,
                # Combine icon and label so priority is readable at a glance
                "Priority": f"{priority_icon} {task.priority.capitalize()}",
                "Duration (mins)": task.duration,
                "Frequency": task.frequency,
            })
        st.table(table_rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Sorts all tasks chronologically and checks for scheduling conflicts.")

# Rule-based schedule (original behaviour)
if st.button("Generate schedule"):
    if "owner" not in st.session_state or "scheduler" not in st.session_state:
        st.warning("Please set an owner first.")
    else:
        owner = st.session_state.owner
        scheduler = st.session_state.scheduler
        all_tasks = scheduler.get_all_tasks(owner)

        if not all_tasks:
            st.warning("No tasks to schedule. Add tasks above.")
        else:
            st.markdown("#### Sorted Schedule")
            sorted_tasks = scheduler.sort_by_time(all_tasks)
            for task in sorted_tasks:
                status = "✅ Done" if task.completed else "⏳ Pending"
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
                st.markdown(
                    f"**{task.time}** — {task.description} "
                    f"({task.duration} mins, {task.frequency}) "
                    f"{priority_color} `{task.priority}` · {status}"
                )

            st.divider()

            st.markdown("#### Conflict Detection")
            conflicts = scheduler.detect_conflicts(owner)
            if conflicts:
                for warning in conflicts:
                    st.warning(warning)
            else:
                st.success("No scheduling conflicts found.")

st.divider()

# ---------------------------------------------------------------------------
# AI Schedule Assistant (Gemini)
# ---------------------------------------------------------------------------
st.subheader("AI Schedule Assistant")
st.caption(
    "Chat with PawPal+ to describe your day and let the AI build a personalised schedule for your pet(s)."
)

gemini_key = os.getenv("GEMINI_API_KEY") or st.text_input(
    "Gemini API key", type="password", help="Your Google AI Studio API key (or set GEMINI_API_KEY in .env)"
)

if gemini_key:
    # Initialise the agent once per session (or when the key changes)
    if "agent" not in st.session_state or st.session_state.get("agent_key") != gemini_key:
        st.session_state.agent = PawPalAgent(api_key=gemini_key)
        st.session_state.agent_key = gemini_key
        st.session_state.chat_history = []
        st.session_state.ai_schedule = None

    # Render conversation history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Kick off the conversation automatically if chat is empty
    if not st.session_state.chat_history:
        owner = st.session_state.get("owner")
        opening = st.session_state.agent.send_message(
            "Hello! Please start the conversation to build my pet schedule.",
            owner=owner,
        )
        st.session_state.chat_history.append({"role": "assistant", "content": opening})
        with st.chat_message("assistant"):
            st.markdown(opening)

    # User input
    user_input = st.chat_input("Type your reply…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        owner = st.session_state.get("owner")
        reply = st.session_state.agent.send_message(user_input, owner=owner)

        # Check whether the agent returned a JSON schedule
        parsed = st.session_state.agent.parse_schedule(reply)
        if parsed:
            st.session_state.ai_schedule = parsed
            display_reply = parsed.get("summary", "Here is your schedule!")
        else:
            display_reply = reply

        st.session_state.chat_history.append({"role": "assistant", "content": display_reply})
        with st.chat_message("assistant"):
            st.markdown(display_reply)

    # Render the AI-generated schedule if one exists
    if st.session_state.get("ai_schedule"):
        sched = st.session_state.ai_schedule
        st.divider()
        st.subheader("AI-Generated Schedule")

        if sched.get("summary"):
            st.info(sched["summary"])

        items = sched.get("schedule", [])
        if items:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            confidence_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}
            table_rows = []
            for item in items:
                p_icon = priority_icon.get(item.get("priority", "medium"), "🟡")
                conf_score = item.get("confidence", "?")
                conf_label = item.get("confidence_label", "").lower()
                c_icon = confidence_icon.get(conf_label, "⚪")
                table_rows.append({
                    "Time": item.get("time", ""),
                    "Pet": item.get("pet", ""),
                    "Task": item.get("task", ""),
                    "Priority": f"{p_icon} {item.get('priority', 'medium').capitalize()}",
                    "Duration (mins)": item.get("duration_mins", ""),
                    "Confidence": f"{c_icon} {conf_score}% ({conf_label.capitalize() if conf_label else '?'})",
                    "Why": item.get("reason", ""),
                })
            st.table(table_rows)
            st.caption(
                "🟢 High confidence (75–100%): clean fit · "
                "🟡 Medium (40–74%): redistributed or near a boundary · "
                "🔴 Low (0–39%): placement uncertain"
            )

        if sched.get("conflicts"):
            st.markdown("#### Conflicts")
            for c in sched["conflicts"]:
                st.warning(c)
        else:
            st.success("No scheduling conflicts.")

        if st.button("Reset AI chat"):
            st.session_state.agent.reset()
            st.session_state.chat_history = []
            st.session_state.ai_schedule = None
            st.rerun()
else:
    st.info("Enter your Gemini API key above to enable the AI assistant.")
