from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant. Add your pets and tasks, then generate a smart daily plan.")

# --- Application "memory" ------------------------------------------------
# Streamlit reruns this script top-to-bottom on every interaction, so we keep
# the Owner (with its pets and tasks) and the Scheduler in session_state so the
# data persists across reruns instead of being rebuilt empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# --- Owner + pets --------------------------------------------------------
st.subheader("Owner & pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        new_pet_name = st.text_input("Pet name", placeholder="e.g. Cocoa")
    with col2:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not new_pet_name.strip():
            st.warning("Please enter a pet name.")
        elif owner.get_pet(new_pet_name):
            st.warning(f"{new_pet_name} is already registered.")
        else:
            owner.add_pet(Pet(name=new_pet_name, species=new_species))
            st.success(f"Added {new_pet_name} the {new_species}.")

if not owner.pets:
    st.info("Add a pet above to get started.")
    st.stop()

st.write("**Pets:** " + ", ".join(pet.describe() for pet in owner.pets))

st.divider()

# --- Add a task ----------------------------------------------------------
st.subheader("Add a task")
pet_names = [pet.name for pet in owner.pets]

with st.form("add_task", clear_on_submit=True):
    target_pet = st.selectbox("Pet", pet_names)
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        use_time = st.checkbox("Set a preferred start time", value=True)
        preferred = st.time_input("Preferred start", value=time(8, 0), disabled=not use_time)
    with col5:
        frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly", "monthly"])

    if st.form_submit_button("Add task"):
        if not task_title.strip():
            st.warning("Please enter a task title.")
        else:
            pet = owner.get_pet(target_pet)
            pet.add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=None if frequency == "one-time" else frequency,
                    preferred_start=preferred if use_time else None,
                )
            )
            st.success(f"Added '{task_title}' for {target_pet}.")

# --- Current tasks (sorted + filterable) ---------------------------------
st.subheader("Current tasks")
filter_choice = st.selectbox("Filter by pet", ["All pets"] + pet_names)

all_tasks = owner.get_all_tasks(include_completed=True)
if filter_choice != "All pets":
    all_tasks = scheduler.filter_tasks(all_tasks, pet_name=filter_choice)

sorted_tasks = scheduler.sort_by_time(all_tasks)  # Scheduler sorting logic

if sorted_tasks:
    scope = "all pets" if filter_choice == "All pets" else filter_choice
    st.caption(f"Showing {len(sorted_tasks)} task(s) for {scope}, sorted by start time.")
    st.table(
        [
            {
                "Time": t.preferred_start.strftime("%H:%M") if t.preferred_start else "—",
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency or "one-time",
                "Done": "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

# Conflict warnings straight from the Scheduler: warn on clashes, reassure when clear.
conflict_warnings = scheduler.warn_conflicts(owner.get_all_tasks(include_completed=True))
if conflict_warnings:
    st.warning(f"⚠️ {len(conflict_warnings)} scheduling conflict(s) detected:")
    for warning in conflict_warnings:
        st.warning(warning)
elif sorted_tasks:
    st.success("✅ No scheduling conflicts — every task has its own time slot.")

st.divider()

# --- Generate today's plan -----------------------------------------------
st.subheader("Today's plan")
if st.button("Generate schedule", type="primary"):
    plan = scheduler.build_daily_plan(owner=owner)
    if plan:
        st.success(f"Planned {len(plan)} task(s) for today.")
        st.table(
            [
                {
                    "Time": entry["start_time"].strftime("%H:%M"),
                    "Pet": entry["pet"],
                    "Task": entry["title"],
                    "Duration (min)": entry["duration_minutes"],
                    "Priority": entry["priority"],
                    "Why": entry["reason"],
                }
                for entry in plan
            ]
        )
        # Re-check the built plan for any duration overlaps the exact-time
        # check can't see, and surface them as warnings.
        for overlap in scheduler.detect_schedule_conflicts(plan):
            st.warning(
                f"Overlap: '{overlap['task_1']}' ({overlap['time_1']}) and "
                f"'{overlap['task_2']}' ({overlap['time_2']}) — "
                f"{overlap['overlap_minutes']} min."
            )
    else:
        st.info(scheduler.get_schedule_summary(plan))
