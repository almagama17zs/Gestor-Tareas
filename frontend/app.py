# frontend/app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os

# ------------------
# Page configuration
# ------------------
st.set_page_config(page_title="Intelligent Task Manager", layout="wide")

# ------------------
# Apply CSS and logo
# ------------------
css_file = os.path.join("assets", "style.css")
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Set general background color and task hover effect
st.markdown("""
<style>
body {background-color: #e6f2ff;}
.task-card {
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 12px;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
}
.task-card:hover {
    transform: translateY(-3px);
    box-shadow: 4px 4px 12px rgba(0,0,0,0.2);
}
.priority-1 {background-color: #ffcccc;} /* High */
.priority-2 {background-color: #ffe5cc;} /* Medium-high */
.priority-3 {background-color: #ffffcc;} /* Medium */
.priority-4 {background-color: #e6ffcc;} /* Medium-low */
.priority-5 {background-color: #ccffcc;} /* Low */
div[data-testid="stSidebar"] {background-color: #cce6ff !important;}
div[data-testid="stSidebarContent"] {padding-top: 5px !important; margin-top: 0 !important;}
div[data-testid="stSidebar"] img {display: block; margin-left:auto; margin-right:auto; margin-top:5px; margin-bottom:10px; width:70%;}
</style>
""", unsafe_allow_html=True)

# Sidebar logo
logo_file = os.path.join("assets", "logo.png")
if os.path.exists(logo_file):
    st.sidebar.image(logo_file, use_column_width=True)

# ------------------
# Page header
# ------------------
st.title("🗂️ Intelligent Task Manager")
st.markdown("Frontend Streamlit with simulated in-memory backend (no Java required).")

# ------------------
# Simulated backend
# ------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

def api_list(): return st.session_state.tasks
def api_get(task_id): return next((t for t in st.session_state.tasks if t["id"] == task_id), None)
def api_create(payload):
    payload["id"] = len(st.session_state.tasks) + 1
    st.session_state.tasks.append(payload)
    return payload
def api_update(task_id, payload):
    for i, t in enumerate(st.session_state.tasks):
        if t["id"] == task_id:
            payload["id"] = task_id
            st.session_state.tasks[i] = payload
            return payload
    return None
def api_delete(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    return True
def api_suggest():
    return sorted([t for t in st.session_state.tasks if not t.get("completed")], key=lambda x: (x["priority"], x.get("dueDate") or datetime.max))
def api_search(q):
    return [t for t in st.session_state.tasks if q.lower() in t["title"].lower()]
def api_pending():
    return [t for t in st.session_state.tasks if not t.get("completed")]

# ------------------
# Utilities
# ------------------
def parse_due(dt): return dt.strftime("%Y-%m-%d %H:%M") if dt else "—"
def priority_class(p): return f"priority-{p}" if p in [1,2,3,4,5] else "priority-3"

# ------------------
# Sidebar menu with big icons
# ------------------
menu_items = [("📋 View Tasks","Ver tareas"),("✏️ Create Task","Crear tarea"),("💡 Suggestions","Sugerencias"),
              ("🔍 Search","Buscar"),("📝 Pending Tasks","Tareas pendientes"),("ℹ️ About","Acerca")]

if "menu" not in st.session_state:
    st.session_state.menu = "Ver tareas"

st.sidebar.markdown("<h2 style='text-align:center'>Menu</h2>", unsafe_allow_html=True)
for icon_label, value in menu_items:
    if st.sidebar.button(icon_label, key=value.replace(' ','_')):
        st.session_state.menu = value
menu = st.session_state.menu

# ------------------
# View: View tasks
# ------------------
if menu == "Ver tareas":
    st.header("📋 All Tasks")
    tasks = api_list()
    if not tasks: st.info("No tasks in the system.")
    else:
        for t in sorted(tasks, key=lambda x: (x["completed"], x["priority"])):
            status = "✅ Completed" if t["completed"] else "⏳ Pending"
            st.markdown(f"""
                <div class='task-card {priority_class(t['priority'])}'>
                    <strong>ID {t['id']}: {t['title']}</strong><br>
                    {t.get('description','')}<br>
                    Priority: {t['priority']} — Estimated: {t['estimatedMinutes']} min — Due: {parse_due(t.get('dueDate'))} — {status}
                </div>
            """, unsafe_allow_html=True)

# ------------------
# View: Create / Edit task
# ------------------
if menu == "Crear tarea":
    st.header("✏️ Create / Edit Task")
    edit_task = st.session_state.get("edit_task", None)
    if edit_task and st.button("Cancel Edit"): st.session_state.pop("edit_task", None); st.experimental_rerun()
    with st.form("task_form", clear_on_submit=False):
        title = st.text_input("Title", value=edit_task.get("title") if edit_task else "")
        description = st.text_area("Description", value=edit_task.get("description") if edit_task else "")
        priority = st.slider("Priority (1=High,5=Low)",1,5,value=edit_task.get("priority") if edit_task else 3)
        estimated = st.number_input("Estimated Time (min)",1,10000,value=edit_task.get("estimatedMinutes") if edit_task else 30)
        col1,col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due Date", value=edit_task.get("dueDate").date() if edit_task and edit_task.get("dueDate") else None)
        with col2:
            due_time = st.time_input("Due Time", value=edit_task.get("dueDate").time() if edit_task and edit_task.get("dueDate") else time(0,0))
        completed = st.checkbox("Completed", value=edit_task.get("completed") if edit_task else False)
        if st.form_submit_button("Save Task"):
            if not title.strip(): st.error("Title is required.")
            else:
                due_dt = datetime.combine(due_date, due_time) if due_date else None
                payload = {"title": title.strip(),"description": description,"priority": int(priority),
                           "estimatedMinutes": int(estimated),"completed": bool(completed),"dueDate": due_dt}
                if edit_task: api_update(edit_task.get("id"),payload); st.success("Task updated"); st.session_state.pop("edit_task", None)
                else: api_create(payload); st.success("Task created")

# ------------------
# View: Suggestions
# ------------------
if menu == "Sugerencias":
    st.header("💡 Task Suggestions")
    suggested = api_suggest()
    if not suggested: st.info("No pending tasks.")
    else:
        for t in suggested:
            st.markdown(f"""
                <div class='task-card {priority_class(t['priority'])}'>
                    <strong>{t['title']}</strong><br>
                    {t.get('description','')}<br>
                    Priority: {t['priority']} — Estimated: {t['estimatedMinutes']} min — Due: {parse_due(t.get('dueDate'))}
                </div>
            """, unsafe_allow_html=True)

# ------------------
# View: Search
# ------------------
if menu == "Buscar":
    st.header("🔍 Search Tasks by Title")
    q = st.text_input("Search text")
    if st.button("Search"):
        if not q.strip(): st.warning("Enter search text")
        else:
            res = api_search(q.strip())
            if res:
                for t in res:
                    st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']} — {t.get('description','')} — Priority {t['priority']} — {parse_due(t.get('dueDate'))}</div>", unsafe_allow_html=True)
            else: st.info("No matches found")

# ------------------
# View: Pending Tasks
# ------------------
if menu == "Tareas pendientes":
    st.header("📝 Pending Tasks")
    pending = api_pending()
    if not pending: st.info("No pending tasks.")
    else:
        for t in pending:
            st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']} — Priority {t['priority']} — Due {parse_due(t.get('dueDate'))}<br>{t.get('description','')}</div>", unsafe_allow_html=True)

# ------------------
# View: About
# ------------------
if menu == "Acerca":
    st.header("ℹ️ About Project")
    st.markdown("""
    - **Backend:** Simulated in-memory (no Java required).
    - **Frontend:** Streamlit (this file).
    - All CRUD operations run directly in Streamlit.
    - Data resets on page refresh since stored in memory.
    """)
