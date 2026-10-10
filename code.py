import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página (Modo Oscuro / Estética CrateCairn)
st.set_page_config(
    page_title="CrateCairn | Export Operations",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para simular la paleta oscura y dorada elegante
st.markdown("""
    <style>
    .main {
        background-color: #0f0e0d;
        color: #f4f1ea;
    }
    .stSidebar {
        background-color: #171614;
    }
    h1, h2, h3 {
        color: #f4f1ea !important;
        font-family: serif;
    }
    .highlight {
        color: #d4af37;
    }
    .metric-card {
        background-color: #1a1917;
        border: 1px solid #33312b;
        padding: 20px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Datos simulados iniciales (Mock Data para agronegocios y exportaciones)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"ID": "INV-001", "Producto": "Café Orgánico (Sacos)", "Origen": "Chiapas, MX", "Cantidad": 1200, "Estado": "En Almacén"},
        {"ID": "INV-002", "Producto": "Aguacate Hass (Ton)", "Origen": "Michoacán, MX", "Cantidad": 45, "Estado": "Listo para Carga"},
        {"ID": "INV-003", "Producto": "Mango Ataulfo (Ton)", "Origen": "Oaxaca, MX", "Cantidad": 30, "Estado": "En Revisión"}
    ])

if 'shipments' not in st.session_state:
    st.session_state.shipments = pd.DataFrame([
        {"Embarque": "SHP-101", "Destino": "Rotterdam, NL", "Producto": "Café Orgánico", "Progreso": "En Tránsito Marítimo", "ETA": "2026-10-25", "Estatus": "A tiempo"},
        {"Embarque": "SHP-102", "Destino": "Los Angeles, US", "Producto": "Aguacate Hass", "Progreso": "Retrasado en Aduana", "ETA": "2026-10-14", "Estatus": "⚠️ Discrepancia"},
        {"Embarque": "SHP-103", "Destino": "Madrid, ES", "Producto": "Mango Ataulfo", "Progreso": "Despacho Inicial", "ETA": "2026-10-18", "Estatus": "A tiempo"}
    ])

# Barra lateral de navegación
st.sidebar.markdown("<h2 class='highlight'>CrateCairn</h2>", unsafe_allow_html=True)
st.sidebar.caption("A clearer daily view of export operations.")
menu = st.sidebar.radio("Navegación", ["Panel General (Dashboard)", "Inventario en Origen", "Progreso de Embarques", "Reporte Diario de Acción"])

if menu == "Panel General (Dashboard)":
    st.markdown("# A clearer daily view of <span class='highlight'>export operations.</span>", unsafe_allow_html=True)
    st.write("CrateCairn reúne el inventario, el progreso de los envíos y los plazos de entrega, señalando retrasos y discrepancias para que tu equipo los revise.")
    
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📦 Inventario en Origen", value=f"{len(st.session_state.inventory)} lotes activos", delta="Estable")
    with col2:
        st.metric(label="🚢 Embarques en Tránsito", value=f"{len(st.session_state.shipments)} rutas", delta="1 Alerta crítica", delta_color="inverse")
    with col3:
        st.metric(label="📋 Entregas Programadas", value="3 esta semana", delta="A tiempo")
        
    st.markdown("### ⚠️ Señales que requieren atención inmediata")
    # Filtrar discrepancias
    discrepancias = st.session_state.shipments[st.session_state.shipments["Estatus"].str.contains("Discrepancia|Retrasado", na=False)]
    if not discrepancias.empty:
        st.error("Se detectó una discrepancia en el embarque SHP-102 (Aduana de destino). Se recomienda revisión del equipo.")
        st.dataframe(discrepancias, use_container_width=True)
    else:
        st.success("No hay retrasos críticos registrados en este momento.")

elif menu == "Inventario en Origen":
    st.markdown("# <span class='highlight'>Inventario</span> en Origen", unsafe_allow_html=True)
    st.write("Mantén a la vista el inventario junto con los envíos que respalda.")
    
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    with st.form("add_inventory"):
        st.subheader("Registrar Nuevo Lote en Origen")
        col1, col2 = st.columns(2)
        with col1:
            prod_name = st.text_input("Nombre del Producto / Cosecha")
            origin_loc = st.text_input("Origen (Ciudad, Estado)")
        with col2:
            qty = st.number_input("Cantidad", min_value=1, value=10)
            status = st.selectbox("Estado", ["En Almacén", "Listo para Carga", "En Revisión"])
            
        submitted = st.form_submit_button("Añadir al Inventario")
        if submitted and prod_name:
            nuevo_id = f"INV-00{len(st.session_state.inventory) + 1}"
            nueva_fila = {"ID": nuevo_id, "Producto": prod_name, "Origen": origin_loc, "Cantidad": qty, "Estado": status}
            st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"¡Lote {nuevo_id} registrado exitosamente!")
            st.rerun()

elif menu == "Progreso de Embarques":
    st.markdown("# <span class='highlight'>Progreso</span> de Embarques", unsafe_allow_html=True)
    st.write("Visualiza el movimiento y los tiempos estimados de entrega en una sola perspectiva operativa.")
    
    st.dataframe(st.session_state.shipments, use_container_width=True)
    
    with st.form("add_shipment"):
        st.subheader("Registrar Nuevo Embarque")
        col1, col2 = st.columns(2)
        with col1:
            shp_id = f"SHP-10{len(st.session_state.shipments) + 1}"
            dest = st.text_input("Destino (Ciudad, País)")
            prod = st.text_input("Producto Transportado")
        with col2:
            prog = st.text_input("Progreso Actual (ej. Puerto de salida)")
            eta_date = st.date_input("ETA (Fecha estimada de llegada)")
            est = st.selectbox("Estatus", ["A tiempo", "⚠️ Discrepancia", "Retrasado"])
            
        submitted_shp = st.form_submit_button("Guardar Embarque")
        if submitted_shp and dest:
            nueva_shp = {"Embarque": shp_id, "Destino": dest, "Producto": prod, "Progreso": prog, "ETA": str(eta_date), "Estatus": est}
            st.session_state.shipments = pd.concat([st.session_state.shipments, pd.DataFrame([nueva_shp])], ignore_index=True)
            st.success(f"Embarque {shp_id} añadido correctamente.")
            st.rerun()

elif menu == "Reporte Diario de Acción":
    st.markdown("# <span class='highlight'>The Daily Action Report</span>", unsafe_allow_html=True)
    st.write("Empieza el día con lo que necesita atención. Cada mañana, CrateCairn resume los retrasos y discrepancias para tu equipo.")
    
    st.info("💡 **Consejo de Operación:** Este reporte se envía automáticamente a las 08:00 AM vía correo electrónico a todos los coordinadores registrados.")
    
    if st.button("Simular Envío de Reporte Diario por Correo"):
        st.success("¡Reporte diario generado y enviado con éxito a los correos del equipo de operaciones!")
        
    st.markdown("### Vista Previa del Reporte de Hoy")
    st.markdown(f"""
    **Fecha:** {datetime.now().strftime('%Y-%m-%d')}
    - **Total Lotes en Origen:** {len(st.session_state.inventory)}
    - **Envíos en Tránsito:** {len(st.session_state.shipments)}
    - **Acción Requerida:** Revisar el estatus del embarque **SHP-102** (Retrasado en aduana de Los Angeles).
    """)

st.sidebar.markdown("---")
st.sidebar.caption("CrateCairn MVP v1.0 · Hecho para agronegocios y exportadores.")
