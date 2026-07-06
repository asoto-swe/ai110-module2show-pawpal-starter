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

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Initialize the owner in session state (the persistent "vault") once, and
# seed it with one pet so the demo isn't empty on first load.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.owner.add_pet(Pet(name="Mochi", species="dog", age=3))

owner = st.session_state.owner
owner.name = owner_name  # keep the owner's name in sync with the input

st.divider()

st.markdown("### Add a Pet")
st.caption("Submit this form to register a new pet with the owner.")

col1, col2, col3 = st.columns(3)
with col1:
    new_pet_name = st.text_input("Pet name", value="Luna")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    new_pet_age = st.number_input("Age", min_value=0, max_value=40, value=3)

if st.button("Add pet"):
    # The form only gathers data; Owner.add_pet() is the method that handles it.
    owner.add_pet(Pet(name=new_pet_name, species=new_pet_species, age=int(new_pet_age)))
    st.rerun()  # re-run so the new pet appears in the selector/list immediately

st.write("Current pets:")
st.table([{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)} for p in owner.pets])

st.divider()

st.markdown("### Tasks")
st.caption("Pick a pet, then add care tasks to it.")

# Choose which pet the new tasks attach to.
selected_index = st.selectbox(
    "Add tasks to",
    range(len(owner.pets)),
    format_func=lambda i: f"{owner.pets[i].name} ({owner.pets[i].species})",
)
current_pet = owner.pets[selected_index]

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
    current_pet.add_task(new_task)  # Pet.add_task() handles the submitted task
    st.rerun()

if current_pet.tasks:
    st.write(f"Tasks for {current_pet.name}:")
    task_data = [
        {
            "Title": task.title,
            "Duration (min)": task.duration_minutes,
            "Priority": task.priority
        }
        for task in current_pet.tasks
    ]
    st.table(task_data)
else:
    st.info(f"No tasks yet for {current_pet.name}. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a plan across all of the owner's pets using the Scheduler.")

if st.button("Generate schedule"):
    scheduler = Scheduler()

    # build_daily_plan gathers tasks across every pet and returns them ordered.
    daily_plan = scheduler.build_daily_plan(owner)

    if not daily_plan:
        st.warning("Please add at least one task before generating a schedule.")
    else:
        st.success("Schedule generated!")
        st.markdown("### Your Daily Plan")

        # Map each task back to the pet it belongs to, for display.
        pet_of = {id(task): pet for pet in owner.pets for task in pet.tasks}
        plan_data = [
            {
                "Task": task.title,
                "Pet": pet_of[id(task)].name,
                "Duration": f"{task.duration_minutes} min",
                "Priority": task.priority.upper()
            }
            for task in daily_plan
        ]
        st.table(plan_data)

        # Explain the plan.
        st.markdown("### Schedule Explanation")
        st.write(scheduler.explain_plan(daily_plan))
