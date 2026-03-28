"""PawPal+ Streamlit UI -- wired to pawpal_system.py backend."""

import os
import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session state init ──────────────────────────────────────────────────────
if "owner" not in st.session_state:
    if os.path.exists("data.json"):
        st.session_state.owner = Owner.load_from_json()
    else:
        st.session_state.owner = Owner("PawPal Owner")
        biscuit = Pet("Biscuit", "Dog")
        biscuit.add_task(Task("Morning feeding", "07:30", "daily", priority="high"))
        biscuit.add_task(Task("Evening walk", "18:00", "daily", priority="medium"))
        mochi = Pet("Mochi", "Cat")
        mochi.add_task(Task("Medication", "08:00", "daily", priority="high"))
        mochi.add_task(Task("Playtime", "14:00", "once", priority="low"))
        st.session_state.owner.add_pet(biscuit)
        st.session_state.owner.add_pet(mochi)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)


def owner() -> Owner:
    return st.session_state.owner


def scheduler() -> Scheduler:
    return st.session_state.scheduler


# ── Header ──────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — sorting, conflict detection, and recurrence built in.")

# ── Sidebar: Add Pet ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet name")
        new_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Hamster", "Other"])
        submitted_pet = st.form_submit_button("Add Pet")
        if submitted_pet and new_pet_name.strip():
            owner().add_pet(Pet(new_pet_name.strip(), new_species))
            st.success(f"Added {new_pet_name}!")
            st.rerun()

    st.divider()

    st.header("Add a Task")
    pet_names = [p.name for p in owner().get_pets()]
    if pet_names:
        with st.form("add_task_form", clear_on_submit=True):
            selected_pet = st.selectbox("For pet", pet_names)
            task_desc = st.text_input("Task description")
            task_time = st.text_input("Time (HH:MM)", value="09:00")
            task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
            task_priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
            submitted_task = st.form_submit_button("Add Task")
            if submitted_task and task_desc.strip():
                for pet in owner().get_pets():
                    if pet.name == selected_pet:
                        pet.add_task(Task(task_desc.strip(), task_time, task_freq, priority=task_priority))
                        st.success(f"Task added for {selected_pet}!")
                        st.rerun()
    else:
        st.info("Add a pet first to schedule tasks.")

    st.divider()

    # Save / Load
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save", use_container_width=True):
            owner().save_to_json()
            st.success("Saved!")
    with col2:
        if st.button("📂 Load", use_container_width=True):
            if os.path.exists("data.json"):
                st.session_state.owner = Owner.load_from_json()
                st.session_state.scheduler = Scheduler(st.session_state.owner)
                st.rerun()
            else:
                st.warning("No saved data found.")

# ── Main area ────────────────────────────────────────────────────────────────
tab_schedule, tab_priority, tab_filter, tab_pets = st.tabs(
    ["Today's Schedule", "Priority View", "Filter Tasks", "Pet Roster"]
)

# ── Tab 1: Today's Schedule ──────────────────────────────────────────────────
with tab_schedule:
    st.subheader("Today's Schedule")

    conflicts = scheduler().detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts today.")

    tasks = scheduler().sort_by_time()
    if not tasks:
        st.info("No tasks scheduled. Add pets and tasks in the sidebar.")
    else:
        for pet_name, task in tasks:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            status_icon = "✅" if task.completed else "⬜"
            col_status, col_info, col_action = st.columns([1, 7, 2])
            with col_status:
                st.write(f"{status_icon} {priority_icon}")
            with col_info:
                label = f"**{task.time}** — {pet_name}: {task.description}"
                label += f"  `{task.frequency}` | Due: {task.due_date}"
                if task.completed:
                    st.success(label)
                else:
                    st.info(label)
            with col_action:
                if not task.completed:
                    btn_key = f"complete_{pet_name}_{task.description}_{task.due_date}"
                    if st.button("Mark done", key=btn_key):
                        scheduler().mark_task_complete(pet_name, task.description)
                        owner().save_to_json()
                        st.rerun()

    st.divider()
    slot_pet = st.selectbox("Find next free slot for:", pet_names if pet_names else ["(no pets)"], key="slot_pet")
    if pet_names and st.button("Find next available slot"):
        slot = scheduler().find_next_available_slot(slot_pet)
        st.info(f"Next available slot for **{slot_pet}**: `{slot}`")

# ── Tab 2: Priority View ─────────────────────────────────────────────────────
with tab_priority:
    st.subheader("Priority-Sorted Schedule")
    st.caption("Tasks sorted: High → Medium → Low, then by time within each group.")

    priority_tasks = scheduler().sort_by_priority_then_time()
    if not priority_tasks:
        st.info("No tasks yet.")
    else:
        for pet_name, task in priority_tasks:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            status = "✅ done" if task.completed else "○ todo"
            label = f"{priority_icon} **{task.priority.upper()}** | {task.time} — {pet_name}: {task.description} [{status}]"
            if task.priority == "high":
                st.error(label)
            elif task.priority == "medium":
                st.warning(label)
            else:
                st.info(label)

# ── Tab 3: Filter Tasks ───────────────────────────────────────────────────────
with tab_filter:
    st.subheader("Filter Tasks")

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        filter_pet = st.selectbox("By pet", ["All"] + pet_names, key="filter_pet")
    with f_col2:
        filter_status = st.selectbox("By status", ["All", "Incomplete", "Complete"], key="filter_status")

    fn_pet = None if filter_pet == "All" else filter_pet
    fn_completed = None
    if filter_status == "Incomplete":
        fn_completed = False
    elif filter_status == "Complete":
        fn_completed = True

    filtered = scheduler().filter_tasks(pet_name=fn_pet, completed=fn_completed)
    st.write(f"**{len(filtered)} task(s) found.**")
    if filtered:
        rows = [
            {
                "Pet": pet_name,
                "Time": task.time,
                "Task": task.description,
                "Frequency": task.frequency,
                "Priority": task.priority,
                "Status": "Done" if task.completed else "Todo",
                "Due": str(task.due_date),
            }
            for pet_name, task in filtered
        ]
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No tasks match the selected filters.")

# ── Tab 4: Pet Roster ─────────────────────────────────────────────────────────
with tab_pets:
    st.subheader("Pet Roster")
    if not owner().get_pets():
        st.info("No pets added yet.")
    else:
        for pet in owner().get_pets():
            with st.expander(f"🐾 {pet.name} ({pet.species}) — {pet.task_count()} tasks"):
                if pet.tasks:
                    for task in pet.tasks:
                        status = "✅" if task.completed else "○"
                        st.write(f"{status} `{task.time}` {task.description} [{task.frequency}, {task.priority}]")
                else:
                    st.write("No tasks yet.")
