# frontend/app.py
import streamlit as st
import pandas as pd
from datetime import datetime, date, time

st.set_page_config(page_title="Gestor de Tareas Inteligente", layout="wide")

# ------------------
# Config
# ------------------
st.title("🗂️ Gestor de Tareas Inteligente")
st.markdown("Frontend Streamlit con backend simulado en memoria (sin Java).")

# ------------------
# Backend simulado
# ------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

def api_list():
    return st.session_state.tasks

def api_get(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            return t
    return None

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
    # Orden simple: prioridad ascendente, luego fecha vencimiento
    return sorted(
        [t for t in st.session_state.tasks if not t.get("completed")],
        key=lambda x: (x["priority"], x.get("dueDate") or datetime.max)
    )

def api_search(q):
    return [t for t in st.session_state.tasks if q.lower() in t["title"].lower()]

def api_pending():
    return [t for t in st.session_state.tasks if not t.get("completed")]

# ------------------
# Utilities
# ------------------
def to_iso(dt: date | datetime | None):
    if dt is None:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime.combine(dt, time.min)
    if isinstance(dt, datetime):
        return dt
    return dt

# ------------------
# Sidebar / Menu
# ------------------
menu = st.sidebar.radio(
    "Menú",
    ["Ver tareas", "Crear tarea", "Sugerencias", "Buscar", "Tareas pendientes", "Acerca"]
)

# ------------------
# View: Ver tareas
# ------------------
if menu == "Ver tareas":
    st.header("Todas las tareas")
    tasks = api_list()

    if not tasks:
        st.info("No hay tareas en el sistema.")
    else:
        df = pd.DataFrame(tasks)
        df_display = df[["id", "title", "description", "priority", "estimatedMinutes", "completed", "dueDate"]] \
            if set(["id","title"]).issubset(df.columns) else df
        st.dataframe(df_display.sort_values(by=["completed","priority"], ascending=[True, True]))

        st.markdown("---")
        st.subheader("Acciones rápidas")
        col1, col2, col3 = st.columns(3)

        with col1:
            cid = st.number_input("ID a marcar completada", min_value=1, step=1, key="complete_id")
            if st.button("Marcar completada"):
                t = api_get(int(cid))
                if t:
                    t["completed"] = True
                    api_update(int(cid), t)
                    st.success(f"Tarea {cid} marcada como completada.")

        with col2:
            eid = st.number_input("ID a editar", min_value=1, step=1, key="edit_id")
            if st.button("Editar tarea"):
                task = api_get(int(eid))
                if task:
                    st.session_state["edit_task"] = task
                    st.success("Abierto en 'Crear tarea' para editar.")

        with col3:
            did = st.number_input("ID a eliminar", min_value=1, step=1, key="delete_id")
            if st.button("Eliminar tarea"):
                ok = api_delete(int(did))
                if ok:
                    st.success(f"Tarea {did} eliminada.")

# ------------------
# View: Crear / Editar tarea
# ------------------
if menu == "Crear tarea":
    st.header("Crear / Editar tarea")
    edit_task = st.session_state.get("edit_task", None)
    if edit_task:
        st.info(f"Editando tarea ID {edit_task.get('id')}. Para cancelar, pulsa 'Cancelar edición'.")
        if st.button("Cancelar edición"):
            st.session_state.pop("edit_task", None)
            st.experimental_rerun()

    with st.form("task_form", clear_on_submit=False):
        title = st.text_input("Título", value=edit_task.get("title") if edit_task else "")
        description = st.text_area("Descripción", value=edit_task.get("description") if edit_task else "")
        priority = st.slider("Prioridad (1 = alta, 5 = baja)", 1, 5, value=edit_task.get("priority") if edit_task else 3)
        estimated = st.number_input("Tiempo estimado (min)", min_value=1, max_value=10000,
                                    value=edit_task.get("estimatedMinutes") if edit_task else 30)
        col_due1, col_due2 = st.columns(2)
        with col_due1:
            due_date = st.date_input("Fecha de vencimiento (opcional)",
                                     value=edit_task.get("dueDate").date() if edit_task and edit_task.get("dueDate") else None)
        with col_due2:
            due_time = st.time_input("Hora de vencimiento (opcional)",
                                     value=edit_task.get("dueDate").time() if edit_task and edit_task.get("dueDate") else time(0,0))
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
                    "dueDate": due_dt
                }

                if edit_task:
                    t_id = int(edit_task.get("id"))
                    api_update(t_id, payload)
                    st.success("Tarea actualizada correctamente.")
                    st.session_state.pop("edit_task", None)
                else:
                    api_create(payload)
                    st.success("Tarea creada correctamente.")

# ------------------
# View: Sugerencias
# ------------------
if menu == "Sugerencias":
    st.header("Orden sugerido de tareas (inteligente)")
    suggested = api_suggest()
    if not suggested:
        st.info("No hay tareas pendientes.")
    else:
        for idx, t in enumerate(suggested, start=1):
            due_str = t["dueDate"].strftime("%Y-%m-%d %H:%M") if t.get("dueDate") else "—"
            cols = st.columns([1, 6, 2, 1])
            cols[0].markdown(f"**{idx}**")
            cols[1].markdown(f"**{t.get('title')}**\n\n{t.get('description') or ''}")
            cols[2].markdown(f"Prioridad: **{t.get('priority')}**  \nEstimado: **{t.get('estimatedMinutes')} min**  \nVencimiento: **{due_str}**")
            if cols[3].button(f"Marcar {t.get('id')}", key=f"mark_{t.get('id')}"):
                t['completed'] = True
                api_update(t.get("id"), t)
                st.experimental_rerun()

# ------------------
# View: Buscar
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
                df = pd.DataFrame(res)
                st.dataframe(df)
            else:
                st.info("No se han encontrado coincidencias.")

# ------------------
# View: Tareas pendientes
# ------------------
if menu == "Tareas pendientes":
    st.header("Tareas pendientes")
    pending = api_pending()
    if not pending:
        st.info("No hay tareas pendientes.")
    else:
        for t in pending:
            due_str = t["dueDate"].strftime("%Y-%m-%d %H:%M") if t.get("dueDate") else "—"
            with st.expander(f"{t.get('title')} — prioridad {t.get('priority')} — {due_str}"):
                st.write(t.get("description") or "")
                st.write(f"Estimado: {t.get('estimatedMinutes')} min")
                col1, col2 = st.columns(2)
                if col1.button("Marcar completada", key=f"pend_mark_{t.get('id')}"):
                    t['completed'] = True
                    api_update(t.get("id"), t)
                    st.experimental_rerun()
                if col2.button("Eliminar", key=f"pend_del_{t.get('id')}"):
                    api_delete(t.get("id"))
                    st.experimental_rerun()

# ------------------
# View: Acerca
# ------------------
if menu == "Acerca":
    st.header("Acerca del proyecto")
    st.markdown("""
    - **Backend:** Simulado en memoria (no necesita Java).
    - **Frontend:** Streamlit (este archivo).
    - Todas las operaciones CRUD funcionan directamente en Streamlit.
    - La app se reinicia al refrescar la página, porque los datos se guardan en memoria.
    """)
