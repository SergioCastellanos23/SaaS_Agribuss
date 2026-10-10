import datetime
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="CrateCairn | Export Operations", page_icon="📦", layout="wide"
)

# Estilos visuales minimalistas oscuros (Estética CrateCairn)
st.markdown(
    """
    <style>
    .main { background-color: #121212; color: #E0E0E0; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Motor de categorización automática (Simula la lectura de APIs/Scraping de paqueterías)
def categorizar_estatus_envio(texto_rastreo, fecha_estimada):
  hoy = datetime.date.today()
  texto = texto_rastreo.lower()

  # 1. Detección de incidencias o aduana
  if any(
      palabra in texto
      for palabra in [
          "delay",
          "held",
          "customs",
          "retención",
          "excepción",
          "exception",
      ]
  ):
    return "🔴 ALERTA: Retenido / Aduana"

  # 2. Detección de entrega completada
  if any(palabra in texto for palabra in ["delivered", "entregado", "signed"]):
    return "🟢 ENTREGADO: Finalizado"

  # 3. Detección de retraso por comparación de fechas (ETA vencido)
  if hoy > fecha_estimada:
    dias = (hoy - fecha_estimada).days
    return f"🔴 ALERTA: Retrasado ({dias} día{'s' if dias > 1 else ''} tarde)"

  # 4. Tránsito normal
  return "🟡 OK: En Tránsito Normal"


# Base de datos simulada en memoria (Session State)
if "embarques" not in st.session_state:
  st.session_state.embarques = pd.DataFrame([
      {
          "ID": "CC-5001",
          "Producto": "Café Veracruz (Lote A)",
          "Transportista": "DHL",
          "Guía / BL": "DHL-98432109",
          "Origen": "Ramos Arizpe",
          "Destino": "Austin, TX",
          "ETD": datetime.date(2026, 10, 1),
          "ETA": datetime.date(2026, 10, 8),
          "Último Estatus Web": "In transit - Shipment departed facility",
      },
      {
          "ID": "CC-5002",
          "Producto": "Aguacate Hass (Tarimas)",
          "Transportista": "FedEx",
          "Guía / BL": "FDX-11223344",
          "Origen": "Apodaca",
          "Destino": "Laredo, TX",
          "ETD": datetime.date(2026, 10, 5),
          "ETA": datetime.date(2026, 10, 12),
          "Último Estatus Web": "Picked up by carrier",
      },
      {
          "ID": "CC-5003",
          "Producto": "Componentes Industriales",
          "Transportista": "Maersk",
          "Guía / BL": "MSK-77889900",
          "Origen": "Santa Catarina",
          "Destino": "Houston, TX",
          "ETD": datetime.date(2026, 9, 28),
          "ETA": datetime.date(2026, 10, 6),
          "Último Estatus Web": "Customs clearance delay / Held",
      },
  ])

# Interfaz Principal
st.title("📦 CrateCairn")
st.subheader("Vista Operativa y Rastreo Inteligente de Exportaciones")
st.markdown("---")

# Barra lateral para registrar nuevos envíos con guía de rastreo
with st.sidebar:
  st.header("➕ Registrar Nuevo Envío")
  with st.form("nuevo_envio"):
    prod = st.text_input("Producto / Lote")
    transportista = st.selectbox(
        "Paquetería / Naviera", ["DHL", "FedEx", "Maersk", "UPS", "Otro"]
    )
    guia = st.text_input("Número de Guía o BL")
    origen = st.text_input("Origen", value="Ramos Arizpe")
    destino = st.text_input("Destino")
    etd = st.date_input("Fecha de Salida (ETD)")
    eta = st.date_input("Fecha Estimada de Llegada (ETA)")
    estatus_web = st.text_input(
        "Estatus de la Paquetería (Simula Scraping/API)", value="In transit"
    )

    submit = st.form_submit_button("Añadir y Categorizar")
    if submit and prod and guia:
      nuevo_registro = {
          "ID": f"CC-500{len(st.session_state.embarques)+1}",
          "Producto": prod,
          "Transportista": transportista,
          "Guía / BL": guia,
          "Origen": origen,
          "Destino": destino,
          "ETD": etd,
          "ETA": eta,
          "Último Estatus Web": estatus_web,
      }
      st.session_state.embarques = pd.concat(
          [st.session_state.embarques, pd.DataFrame([nuevo_registro])],
          ignore_index=True,
      )
      st.success("¡Envío agregado correctamente!")

# Procesar y categorizar automáticamente todos los embarques
df = st.session_state.embarques.copy()
df["Estatus Operativo CrateCairn"] = df.apply(
    lambda row: categorizar_estatus_envio(row["Último Estatus Web"], row["ETA"]),
    axis=1,
)

# Métricas Generales
total_envios = len(df)
alertas = len(df[df["Estatus Operativo CrateCairn"].str.contains("ALERTA")])
completados = len(
    df[df["Estatus Operativo CrateCairn"].str.contains("ENTREGADO")]
)

col1, col2, col3 = st.columns(3)
col1.metric("Embarques en Monitoreo", total_envios)
col2.metric("Alertas / Retrasos Activos", alertas, delta=-alertas)
col3.metric("Entregas Exitosas", completados)

st.markdown("---")

# SECCIÓN: Reporte Diario de Acción (El valor central del producto)
if alertas > 0:
  st.error(
      "⚠️ **REPORTE DIARIO DE ACCIÓN:** Se detectaron retrasos o retenciones en"
      " aduana que requieren la atención inmediata de tu equipo:"
  )
  df_alertas = df[df["Estatus Operativo CrateCairn"].str.contains("ALERTA")]
  st.dataframe(
      df_alertas[
          [
              "ID",
              "Producto",
              "Transportista",
              "Guía / BL",
              "ETA",
              "Estatus Operativo CrateCairn",
          ]
      ],
      use_container_width=True,
  )
else:
  st.success(
      "✅ **REPORTE DIARIO DE ACCIÓN:** ¡Excelente inicio de día! No hay"
      " retrasos críticos registrados en las rutas."
  )

st.markdown("### 📋 Vista General y Detalle de Toda la Operación")
st.dataframe(df, use_container_width=True)
