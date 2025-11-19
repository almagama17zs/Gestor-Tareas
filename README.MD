# 🗂️ Gestor de Tareas Inteligente

Frontend desarrollado con **Streamlit** que permite gestionar tareas de manera interactiva, con **backend simulado en memoria** (no requiere Java ni base de datos). Ideal para pruebas rápidas o demos.

---
## 🔗 Enlace
https://gestor-tareas.streamlit.app/

---
## 🚀 Características

- CRUD completo de tareas (Crear, Leer, Actualizar, Eliminar)
- Gestión de prioridades (1 = alta, 5 = baja)
- Fechas de vencimiento y tiempo estimado
- Sugerencias de orden de tareas según prioridad y fecha
- Visualización de tareas pendientes
- Interfaz moderna con tarjetas animadas y colores según prioridad
- Sidebar con iconos intuitivos para cada sección
- Totalmente funcional sin backend real (datos en memoria)

---

## 🎨 Estilo y UI

- Colores dinámicos según prioridad de la tarea
- Hover animado en tarjetas para efecto “flotante”
- Sidebar estilizado con logo y espaciado personalizado
- Iconos grandes para las secciones del menú
- Archivos de estilo CSS en `assets/style.css`

---

## 🛠️ Requisitos

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- Pandas
- Dependencias del proyecto:  

```bash
pip install -r requirements.txt
