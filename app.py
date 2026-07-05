import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

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
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize owner and pet objects in session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.pet = Pet(name=pet_name, species=species, age=3)
    st.session_state.owner.add_pet(st.session_state.pet)
else:
    # Update names if changed
    st.session_state.owner.name = owner_name
    st.session_state.pet.name = pet_name
    st.session_state.pet.species = species

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority
    )
    st.session_state.pet.add_task(new_task)
    st.rerun()

if st.session_state.pet.tasks:
    st.write("Current tasks:")
    task_data = [
        {
            "Title": task.title,
            "Duration (min)": task.duration_minutes,
            "Priority": task.priority
        }
        for task in st.session_state.pet.tasks
    ]
    st.table(task_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.pet.tasks:
        st.warning("Please add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler()
        try:
            # Build daily plan for the owner
            daily_plan = scheduler.build_daily_plan(st.session_state.owner)
            
            st.success("Schedule generated!")
            st.markdown("### Your Daily Plan")
            
            # Sort and display tasks
            sorted_tasks = scheduler.sort_tasks(st.session_state.pet.tasks)
            plan_data = [
                {
                    "Task": task.title,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority.upper()
                }
                for task in sorted_tasks
            ]
            st.table(plan_data)
            
            # Explain the plan
            st.markdown("### Schedule Explanation")
            explanation = scheduler.explain_plan(sorted_tasks)
            st.write(explanation)
            
        except NotImplementedError:
            st.info(
                "Scheduler methods need implementation. The system structure is ready—next step is to add the scheduling logic."
            )
