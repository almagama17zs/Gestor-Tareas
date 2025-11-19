# frontend/app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, time
from dateutil import parser

st.set_page_config(page_title="Gestor de Tareas Inteligente", layout="wide")

# ------------------
# Config
# ------------------
st.title("🗂️ Gestor de Tareas Inteligente")
st.markdown("Frontend Streamlit que consume la API Java (Spring Boot).")

API_BASE = st.sidebar.text_input("Backend API base URL", value="http://localhost:8080/api/tasks")
if API_BASE.endswith("/"):
    API_BASE = API_BASE[:-1]

# Helper: perform requests safely
def safe_request(func, *args, **kwargs):
    try:
        r = func(*args, **kwargs)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión o API: {e}")
        return None

# API helpers
def api_list():
    r = safe_request(requests.get, API_BASE)
    return r.json() if r is not None else []

def api_get(task_id):
    r = safe_request(requests.get, f"{API_BASE}/{task_id}")
    return r.json() if r is not None else None

def api_create(payload):
    r = safe_request(requests.post, API_BASE, json=payload)
    return r.json() if r is not None else None

def api_update(task_id, payload):
    r = safe_request(requests.put, f"{API_BASE}/{task_id}", json=payload)
    return r.json() if r is not None else None

def api_delete(task_id):
    r = safe_request(requests.delete, f"{API_BASE}/{task_id}")
    return r is not None

def api_suggest():
    r = safe_request(requests.get, f"{API_BASE}/suggest")
    return r.json() if r is not None else []

def api_search(q):
    r = safe_request(requests.get, f"{API_BASE}/search", params={"q": q})
    return r.json() if r is not None else []

def api_pending():
    r = safe_request(requests.get, f"{API_BASE}/pending")
    return r.json() if r is not None else []

# Utilities
def to_iso(dt: date | datetime | None):
    if dt is None:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime.combine(dt, time.min).isoformat()
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt  # assume already string

def parse_iso(iso_str):
    if not iso_str:
        return None
    try:
        return parser.isoparse(iso_str)
    except Exception:
        return None

# ------------------
# Sidebar / Menu
# ------------------
menu = st.sidebar.radio("Menú", ["Ver tareas", "Crear tarea", "Sugerencias", "Buscar", "Tareas pendientes", "Acerca"])

# ------------------
# View: List all tasks (tabla + acciones)
# ------------------
if menu == "Ver tareas":
    st.header("Todas las tareas")
    tasks = api_list()
    if tasks is None:
        st.stop()

    if not tasks:
        st.info("No hay tareas en el sistema.")
    else:
        # Normalize to DataFrame for display
        df = pd.json_normalize(tasks)
        # pretty dates
        for col in ["dueDate", "createdAt", "updatedAt"]:
            if col in df.columns:
                df[col] = df[col].map(lambda x: parse_iso(x).strftime("%Y-%m-%d %H:%M") if pd.notna(x) and x else "")
        df_display = df[["id", "title", "description", "priority", "estimatedMinutes", "completed", "dueDate", "createdAt", "updatedAt"]] \
            if set(["id","title"]).issubset(df.columns) else df
        st.dataframe(df_display.sort_values(by=["completed","priority","dueDate"], ascending=[True, True, True]))

        st.markdown("---")
        st.subheader("Acciones rápidas")
        col1, col2, col3 = st.columns(3)

        with col1:
            cid = st.number_input("ID a marcar completada", min_value=1, step=1, key="complete_id")
            if st.button("Marcar completada"):
                t = api_get(int(cid))
                if t:
                    t["completed"] = True
                    updated = api_update(int(cid), t)
                    if updated:
                        st.success(f"Tarea {cid} marcada como completada.")
                    else:
                        st.error("Error marcando completada.")

        with col2:
            eid = st.number_input("ID a editar", min_value=1, step=1, key="edit_id")
            if st.button("Editar tarea (abrir formulario)"):
                task = api_get(int(eid))
                if task:
                    st.session_state["edit_task"] = task
                    st.success("Abierto en Crear/Editar (ve a 'Crear tarea' y verás el formulario con datos).")
                else:
                    st.error("No encontrada.")

        with col3:
            did = st.number_input("ID a eliminar", min_value=1, step=1, key="delete_id")
            if st.button("Eliminar tarea"):
                ok = api_delete(int(did))
                if ok:
                    st.success(f"Tarea {did} eliminada.")
                else:
                    st.error("Error eliminando tarea.")

# ------------------
# View: Create / Edit task
# ------------------
if menu == "Crear tarea":
    st.header("Crear / Editar tarea")

    # If we have an edit task in session, prefill form
    edit_task = st.session_state.get("edit_task", None)
    if edit_task:
        st.info(f"Editando tarea ID {edit_task.get('id')}. Para cancelar, pulsa el botón 'Cancelar edición'.")
        if st.button("Cancelar edición"):
            st.session_state.pop("edit_task", None)
            st.experimental_rerun()

    with st.form("task_form", clear_on_submit=False):
        title = st.text_input("Título", value=edit_task.get("title") if edit_task else "")
        description = st.text_area("Descripción", value=edit_task.get("description") if edit_task else "")
        priority = st.slider("Prioridad (1 = alta, 5 = baja)", 1, 5, value=edit_task.get("priority") if edit_task else 3)
        estimated = st.number_input("Tiempo estimado (min)", min_value=1, max_value=10000, value=edit_task.get("estimatedMinutes") if edit_task else 30)
        col_due1, col_due2 = st.columns(2)
        with col_due1:
            due_date = st.date_input("Fecha de vencimiento (opcional)", value=parse_iso(edit_task.get("dueDate")).date() if edit_task and edit_task.get("dueDate") else None)
        with col_due2:
            due_time = st.time_input("Hora de vencimiento (opcional)", value=parse_iso(edit_task.get("dueDate")).time() if edit_task and edit_task.get("dueDate") else time(0,0))
        completed = st.checkbox("Completada", value=edit_task.get("completed") if edit_task else False)

        submitted = st.form_submit_button("Guardar tarea")

        if submitted:
            if not title.strip():
                st.error("El título es obligatorio.")
            else:
                due_dt = None
                try:
                    if due_date:
                        due_dt = datetime.combine(due_date, due_time)
                except Exception:
                    due_dt = None

                payload = {
                    "title": title.strip(),
                    "description": description,
                    "priority": int(priority),
                    "estimatedMinutes": int(estimated),
                    "completed": bool(completed),
                    "dueDate": to_iso(due_dt)
                }

                if edit_task:
                    t_id = int(edit_task.get("id"))
                    result = api_update(t_id, payload)
                    if result:
                        st.success("Tarea actualizada correctamente.")
                        st.session_state.pop("edit_task", None)
                    else:
                        st.error("Error actualizando tarea.")
                else:
                    result = api_create(payload)
                    if result:
                        st.success("Tarea creada correctamente.")
                    else:
                        st.error("Error creando tarea.")

# ------------------
# View: Suggestions
# ------------------
if menu == "Sugerencias":
    st.header("Orden sugerido de tareas (inteligente)")
    suggested = api_suggest()
    if suggested is None:
        st.stop()
    if not suggested:
        st.info("No hay tareas pendientes.")
    else:
        for idx, t in enumerate(suggested, start=1):
            due = parse_iso(t.get("dueDate"))
            due_str = due.strftime("%Y-%m-%d %H:%M") if due else "—"
            cols = st.columns([1, 6, 2, 1])
            cols[0].markdown(f"**{idx}**")
            cols[1].markdown(f"**{t.get('title')}**\n\n{t.get('description') or ''}")
            cols[2].markdown(f"Prioridad: **{t.get('priority')}**  \nEstimado: **{t.get('estimatedMinutes')} min**  \nVencimiento: **{due_str}**")
            if cols[3].button(f"Marcar {t.get('id')}", key=f"mark_{t.get('id')}"):
                t['completed'] = True
                updated = api_update(t.get("id"), t)
                if updated:
                    st.experimental_rerun()

# ------------------
# View: Search
# ------------------
if menu == "Buscar":
    st.header("Buscar tareas por título")
    q = st.text_input("Cadena a buscar en títulos")
    if st.button("Buscar"):
        if not q.strip():
            st.warning("Introduce una cadena de búsqueda.")
        else:
            res = api_search(q.strip())
            if res:
                df = pd.json_normalize(res)
                for col in ["dueDate","createdAt","updatedAt"]:
                    if col in df.columns:
                        df[col] = df[col].map(lambda x: parse_iso(x).strftime("%Y-%m-%d %H:%M") if pd.notna(x) and x else "")
                st.dataframe(df)
            else:
                st.info("No se han encontrado coincidencias o error de API.")

# ------------------
# View: Pending
# ------------------
if menu == "Tareas pendientes":
    st.header("Tareas pendientes")
    pending = api_pending()
    if pending is None:
        st.stop()
    if not pending:
        st.info("No hay tareas pendientes.")
    else:
        for t in pending:
            due = parse_iso(t.get("dueDate"))
            due_str = due.strftime("%Y-%m-%d %H:%M") if due else "—"
            with st.expander(f"{t.get('title')}  — prioridad {t.get('priority')} — {due_str}"):
                st.write(t.get("description") or "")
                st.write(f"Estimado: {t.get('estimatedMinutes')} min")
                col1, col2 = st.columns(2)
                if col1.button("Marcar completada", key=f"pend_mark_{t.get('id')}"):
                    t['completed'] = True
                    updated = api_update(t.get("id"), t)
                    if updated:
                        st.success("Marcada como completada.")
                        st.experimental_rerun()
                if col2.button("Eliminar", key=f"pend_del_{t.get('id')}"):
                    ok = api_delete(t.get("id"))
                    if ok:
                        st.success("Eliminada.")
                        st.experimental_rerun()

# ------------------
# View: About
# ------------------
if menu == "Acerca":
    st.header("Acerca del proyecto")
    st.markdown("""
    - **Backend:** Java Spring Boot (API REST con H2 por defecto).
    - **Frontend:** Streamlit (este archivo).
    - **Endpoints esperados:** `/api/tasks`, `/api/tasks/{id}`, `/api/tasks/suggest`, `/api/tasks/search`, `/api/tasks/pending`
    - Ajusta la URL del backend en la barra lateral si tu backend no está en `localhost:8080`.
    """)
    st.markdown("**Comandos locales (terminal)**")
    st.code("""# Backend (desde carpeta backend)
./mvnw spring-boot:run
# o con maven instalado
mvn spring-boot:run

# Frontend (desde carpeta frontend)
pip install -r requirements.txt
streamlit run app.py
""")
