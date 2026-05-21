import streamlit as st
import requests

BASE_URL = "https://task-su-production.up.railway.app"

# SESSION STATE
if "token" not in st.session_state:
    st.session_state.token = None

# PAGE CONFIG
st.set_page_config(
    page_title="Team Task Manager",
    layout="wide"
)

st.title(" Team Task Manager")

# SIDEBAR MENU
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Signup",
        "Login",
        "Dashboard",
        "Create Project",
        "View Projects",
        "Create Task",
        "View Tasks",
        "Update Task Status"
    ]
)

# ---------------- SIGNUP ----------------

if menu == "Signup":

    st.subheader("Create Account")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name")

    with col2:
        email = st.text_input("Email")

    password = st.text_input("Password", type="password")

    if st.button("Signup"):

        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "name": name,
                "email": email,
                "password": password
            }
        )

        data = response.json()

        if response.status_code == 201:
            st.success(data["message"])
        else:
            st.error(data)

# ---------------- LOGIN ----------------

elif menu == "Login":

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        data = response.json()

        if "token" in data:

            st.session_state.token = data["token"]

            st.success("Login Successful")

            st.write("Your User ID:", data.get("user_id"))
        else:
            st.error(data)

# ---------------- DASHBOARD ----------------

elif menu == "Dashboard":

    st.subheader("Dashboard")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers=headers
        )

        data = response.json()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Projects", data.get("total_projects", 0))

        with col2:
            st.metric("Total Tasks", data.get("total_tasks", 0))

        col3, col4 = st.columns(2)

        with col3:
            st.metric("Completed Tasks", data.get("completed_tasks", 0))

        with col4:
            st.metric("Pending Tasks", data.get("pending_tasks", 0))

# ---------------- CREATE PROJECT ----------------

elif menu == "Create Project":

    st.subheader("Create Project")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        project_name = st.text_input("Project Name")

        if st.button("Create Project"):

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            response = requests.post(
                f"{BASE_URL}/projects/create",
                json={
                    "name": project_name
                },
                headers=headers
            )

            data = response.json()

            if response.status_code == 201:
                st.success(data["message"])
            else:
                st.error(data)

# ---------------- VIEW PROJECTS ----------------

elif menu == "View Projects":

    st.subheader("Projects")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.get(
            f"{BASE_URL}/projects/",
            headers=headers
        )

        projects = response.json()

        if not projects:
            st.info("No projects found")

        for project in projects:

            with st.container():

                st.write(f"###  {project['project_name']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("Project ID:", project["project_id"])

                with col2:
                    if project["role"] == "admin":
                        st.success("Role: Admin")
                    else:
                        st.info("Role: Member")

                st.divider()

# ---------------- CREATE TASK ----------------

elif menu == "Create Task":

    st.subheader("Create Task")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        title = st.text_input("Task Title")

        description = st.text_area("Description")

        col1, col2 = st.columns(2)

        with col1:
            project_id = st.number_input(
                "Project ID",
                min_value=1,
                step=1
            )

        with col2:
            assigned_to = st.number_input(
                "Assign To User ID",
                min_value=1,
                step=1
            )

        if st.button("Create Task"):

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            response = requests.post(
                f"{BASE_URL}/tasks/create",
                json={
                    "title": title,
                    "description": description,
                    "project_id": int(project_id),
                    "assigned_to": int(assigned_to)
                },
                headers=headers
            )

            data = response.json()

            if response.status_code == 201:
                st.success(data["message"])
            else:
                st.error(data)

# ---------------- VIEW TASKS ----------------

elif menu == "View Tasks":

    st.subheader("View Tasks")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        project_id = st.number_input(
            "Enter Project ID",
            min_value=1,
            step=1
        )

        if st.button("Load Tasks"):

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            response = requests.get(
                f"{BASE_URL}/tasks/project/{int(project_id)}",
                headers=headers
            )

            data = response.json()

            # HANDLE ERRORS CLEANLY
            if response.status_code != 200:

                st.error(data.get("error", "Something went wrong"))

            elif not data:

                st.info("No tasks found")

            else:

                for task in data:

                    with st.container():

                        st.write("### 📝", task["title"])

                        st.write("Task ID:", task["task_id"])

                        st.write("Description:", task["description"])

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("Status:", task["status"])

                        with col2:
                            st.write("Assigned To:", task["assigned_to"])

                        st.divider()
# ---------------- UPDATE TASK STATUS ----------------

elif menu == "Update Task Status":

    st.subheader("Update Task Status")

    if not st.session_state.token:

        st.warning("Please login first")

    else:

        task_id = st.number_input(
            "Task ID",
            min_value=1,
            step=1
        )

        status = st.selectbox(
            "Select Status",
            [
                "To Do",
                "In Progress",
                "Completed"
            ]
        )

        if st.button("Update Status"):

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            response = requests.put(
                f"{BASE_URL}/tasks/update-status/{int(task_id)}",
                json={
                    "status": status
                },
                headers=headers
            )

            data = response.json()

            if response.status_code == 200:
                st.success(data["message"])
            else:
                st.error(data)
