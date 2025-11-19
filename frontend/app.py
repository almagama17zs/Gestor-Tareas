# frontend/app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os

# ------------------
# Page configuration
# ------------------
st.set_page_config(page_title="Gestor de Tareas Inteligente", layout="wide")

# ------------------
# Apply CSS and logo
# ------------------
css_file = os.path.join("assets", "style.css")
if os.path.exists(css_file):
    # Read CSS file and inject it into the page
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Extra CSS for hover effects and priority colors
st.markdown("""
<style>
body {background-color: #e6f2ff;} /* Light background */
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
.priority-1 {background-color: #ffcccc;} /* Alta */
.priority-2 {background-color: #ffe5cc;} /* Media-alta */
.priority-3 {background-color: #ffffcc;} /* Media */
.priority-4 {background-color: #e6ffcc;} /* Media-baja */
.priority-5 {background-color: #ccffcc;} /* Baja */
div[data-testid="stSidebar"] {background-color: #cce6ff !important;} /* Sidebar azul */
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
st.title("🗂️ Gestor de Tareas Inteligente")
st.markdown("Frontend Streamlit con backend simulado en memoria (sin Java).")

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
# Sidebar menu with icons
# ------------------
menu_items = [("📋 Ver tareas","Ver tareas"),("✏️ Crear tarea","Crear tarea"),("💡 Sugerencias","Sugerencias"),
              ("🔍 Buscar","Buscar"),("📝 Tareas pendientes","Tareas pendientes"),("ℹ️ Acerca","Acerca")]

if "menu" not in st.session_state:
    st.session_state.menu = "Ver tareas"

st.sidebar.markdown("<h2 style='text-align:center'>Menú</h2>", unsafe_allow_html=True)
for icon_label, value in menu_items:
    if st.sidebar.button(icon_label, key=value.replace(' ','_')):
        st.session_state.menu = value
menu = st.session_state.menu

# ------------------
# View: Ver tareas
# ------------------
if menu == "Ver tareas":
    st.header("📋 Todas las tareas")
    tasks = api_list()
    if not tasks: st.info("No hay tareas en el sistema.")
    else:
        for t in sorted(tasks, key=lambda x: (x["completed"], x["priority"])):
            status = "✅ Completada" if t["completed"] else "⏳ Pendiente"
            st.markdown(f"""
                <div class='task-card {priority_class(t['priority'])}'>
                    <strong>ID {t['id']}: {t['title']}</strong><br>
                    {t.get('description','')}<br>
                    Prioridad: {t['priority']} — Estimado: {t['estimatedMinutes']} min — Vencimiento: {parse_due(t.get('dueDate'))} — {status}
                </div>
            """, unsafe_allow_html=True)

# ------------------
# View: Crear / Editar tarea
# ------------------
if menu == "Crear tarea":
    st.header("✏️ Crear / Editar tarea")
    edit_task = st.session_state.get("edit_task", None)
    if edit_task and st.button("Cancelar edición"): st.session_state.pop("edit_task", None); st.experimental_rerun()
    with st.form("task_form", clear_on_submit=False):
        title = st.text_input("Título", value=edit_task.get("title") if edit_task else "")
        description = st.text_area("Descripción", value=edit_task.get("description") if edit_task else "")
        priority = st.slider("Prioridad (1=alta,5=baja)",1,5,value=edit_task.get("priority") if edit_task else 3)
        estimated = st.number_input("Tiempo estimado (min)",1,10000,value=edit_task.get("estimatedMinutes") if edit_task else 30)
        col1,col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Fecha de vencimiento", value=edit_task.get("dueDate").date() if edit_task and edit_task.get("dueDate") else None)
        with col2:
            due_time = st.time_input("Hora de vencimiento", value=edit_task.get("dueDate").time() if edit_task and edit_task.get("dueDate") else time(0,0))
        completed = st.checkbox("Completada", value=edit_task.get("completed") if edit_task else False)
        if st.form_submit_button("Guardar tarea"):
            if not title.strip(): st.error("El título es obligatorio.")
            else:
                due_dt = datetime.combine(due_date, due_time) if due_date else None
                payload = {"title": title.strip(),"description": description,"priority": int(priority),
                           "estimatedMinutes": int(estimated),"completed": bool(completed),"dueDate": due_dt}
                if edit_task: api_update(edit_task.get("id"),payload); st.success("Tarea actualizada"); st.session_state.pop("edit_task", None)
                else: api_create(payload); st.success("Tarea creada")

# ------------------
# View: Sugerencias
# ------------------
if menu == "Sugerencias":
    st.header("💡 Orden sugerido de tareas")
    suggested = api_suggest()
    if not suggested: st.info("No hay tareas pendientes.")
    else:
        for t in suggested:
            st.markdown(f"""
                <div class='task-card {priority_class(t['priority'])}'>
                    <strong>{t['title']}</strong><br>
                    {t.get('description','')}<br>
                    Prioridad: {t['priority']} — Estimado: {t['estimatedMinutes']} min — Vencimiento: {parse_due(t.get('dueDate'))}
                </div>
            """, unsafe_allow_html=True)

# ------------------
# View: Buscar
# ------------------
if menu == "Buscar":
    st.header("🔍 Buscar tareas por título")
    q = st.text_input("Cadena a buscar")
    if st.button("Buscar"):
        if not q.strip(): st.warning("Introduce texto")
        else:
            res = api_search(q.strip())
            if res:
                for t in res:
                    st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']} — {t.get('description','')} — Prioridad {t['priority']} — {parse_due(t.get('dueDate'))}</div>", unsafe_allow_html=True)
            else: st.info("No se encontraron coincidencias")

# ------------------
# View: Tareas pendientes
# ------------------
if menu == "Tareas pendientes":
    st.header("📝 Tareas pendientes")
    pending = api_pending()
    if not pending: st.info("No hay tareas pendientes.")
    else:
        for t in pending:
            st.markdown(f"<div class='task-card {priority_class(t['priority'])}'>{t['title']} — Prioridad {t['priority']} — Vencimiento: {parse_due(t.get('dueDate'))}<br>{t.get('description','')}</div>", unsafe_allow_html=True)

# ------------------
# View: Acerca
# ------------------
if menu == "Acerca":
    st.header("ℹ️ Acerca del proyecto")
    st.markdown("""
    - **Backend:** Simulado en memoria (no necesita Java).
    - **Frontend:** Streamlit (este archivo).
    - Todas las operaciones CRUD funcionan directamente en Streamlit.
    - La app se reinicia al refrescar la página, porque los datos se guardan en memoria.
    """)
