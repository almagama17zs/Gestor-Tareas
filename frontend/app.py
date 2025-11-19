# frontend/app.py
import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="Gestor de Tareas Inteligente", layout="wide")

# ------------------ CSS ------------------
st.markdown("""
<style>
/* Body background */
body {background-color: #e6f2ff;}

/* Task cards */
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
.priority-1 {background-color: #ffcccc;}
.priority-2 {background-color: #ffe5cc;}
.priority-3 {background-color: #ffffcc;}
.priority-4 {background-color: #e6ffcc;}
.priority-5 {background-color: #ccffcc;}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #cce6ff !important;
    padding-top: 20px;
    width: 300px !important;
}
.sidebar-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    color: #0059b3;
    margin-bottom: 20px;
}

/* Sidebar HTML buttons */
.sidebar-button {
    display: block;
    width: 90%;
    height: 50px;       /* altura uniforme */
    line-height: 50px;  /* texto centrado verticalmente */
    margin: 5px auto;
    text-align: center;
    background-color: #99ccff;
    color: #003366;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    font-size: 16px;
    transition: background-color 0.2s, transform 0.2s;
}
.sidebar-button:hover {
    background-color: #80bfff;
    transform: translateY(-2px);
}

div[data-testid="stSidebar"] img {
    display: block;
    margin-left:auto;
    margin-right:auto;
    margin-top:5px;
    margin-bottom:10px;
    width:70%;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar logo ------------------
logo_file = os.path.join("assets", "logo.png")
if os.path.exists(logo_file):
    st.sidebar.image(logo_file, use_column_width=True)

# ------------------ Header ------------------
st.title("🗂️ Gestor de Tareas Inteligente")
st.markdown("Frontend Streamlit con backend simulado en memoria (sin Java).")

# ------------------ Backend simulado ------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

def api_list(): return st.session_state.tasks
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
def api_suggest():
    return sorted([t for t in st.session_state.tasks if not t.get("completed")],
                  key=lambda x: (x["priority"], x.get("dueDate") or datetime.max))
def api_search(q):
    return [t for t in st.session_state.tasks if q.lower() in t["title"].lower()]
def api_pending():
    return [t for t in st.session_state.tasks if not t.get("completed")]

def parse_due(dt): return dt.strftime("%Y-%m-%d %H:%M") if dt else "—"
def priority_class(p): return f"priority-{p}" if p in [1,2,3,4,5] else "priority-3"

# ------------------ Sidebar menu HTML ------------------
menu_items = [
    ("📋 Ver tareas","Ver tareas"),
    ("✏️ Crear tarea","Crear tarea"),
    ("💡 Sugerencias","Sugerencias"),
    ("🔍 Buscar","Buscar"),
    ("📝 Tareas pendientes","Tareas pendientes"),
    ("ℹ️ Acerca","Acerca")
]

if "menu" not in st.session_state:
    st.session_state.menu = "Ver tareas"

st.sidebar.markdown('<div class="sidebar-title">Gestor de Tareas</div>', unsafe_allow_html=True)

# Render HTML buttons
for icon_label, value in menu_items:
    if st.sidebar.button(icon_label, key=value):
        st.session_state.menu = value

menu = st.session_state.menu

# ------------------ Views ------------------
if menu == "Ver tareas":
    st.header("📋 Todas las tareas")
    tasks = api_list()
    if not tasks: st.info("No hay tareas en el sistema.")
    else:
        for t in tasks:
            status = "✅ Completada" if t.get("completed") else "⏳ Pendiente"
            st.markdown(f"<div class='task-card {priority_class(t['priority'])}'><strong>{t['title']}</strong> — {status}</div>", unsafe_allow_html=True)

if menu == "Crear tarea":
    st.header("✏️ Crear tarea")
    with st.form("task_form"):
        title = st.text_input("Título")
        priority = st.slider("Prioridad (1=alta,5=baja)",1,5,value=3)
        if st.form_submit_button("Guardar"):
            api_create({"title": title, "priority": priority, "completed": False})
            st.success("Tarea creada")

if menu == "Sugerencias":
    st.header("💡 Orden sugerido")
    for t in api_suggest():
        st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']}</div>", unsafe_allow_html=True)

if menu == "Buscar":
    st.header("🔍 Buscar tareas")
    q = st.text_input("Cadena a buscar")
    if st.button("Buscar"):
        for t in api_search(q):
            st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']}</div>", unsafe_allow_html=True)

if menu == "Tareas pendientes":
    st.header("📝 Pendientes")
    for t in api_pending():
        st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']}</div>", unsafe_allow_html=True)

if menu == "Acerca":
    st.header("ℹ️ Acerca")
    st.markdown("- Backend en memoria\n- Frontend Streamlit\n- CRUD funcional")
