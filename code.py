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


# Motor de categorización automática
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
          "detenido",
      ]
  ):
    return "🔴 ALERTA: Retenido / Incidencia en Aduana"

  # 2. Detección de entrega completada
  if any(palabra in texto for palabra in ["delivered", "entregado", "signed"]):
    return "🟢 ENTREGADO: Finalizado"

  # 3. Detección de retraso por comparación de fechas (ETA vencido)
  if hoy > fecha_estimada:
    dias = (hoy - fecha_estimada).days
    return f"🔴 ALERTA: Retrasado ({dias} día{'s' if dias > 1 else ''} tarde)"

  # 4. Tránsito normal
  return "🟡 OK: En Tránsito Normal"


# Base de datos simulada con un catálogo diverso de exportación
if "embarques" not in st.session_state:
  st.session_state.embarques = pd.DataFrame([
      {
          "ID": "CC-5001",
          "Producto": "Aguacate Hass (20 Tarimas - Refrigerado)",
          "Transportista": "FedEx Freight",
          "Guía / BL": "FDX-984321092",
          "Origen": "Uruapan, Michoacán",
          "Destino": "McAllen, TX",
          "ETD": datetime.date(2026, 10, 4),
          "ETA": datetime.date(2026, 10, 8),
          "Último Estatus Web": (
              "Customs clearance delay - Agriculture inspection"
          ),
      },
      {
          "ID": "CC-5002",
          "Producto": "Café Pluma Hidalgo (150 Sacos)",
          "Transportista": "DHL Express",
          "Guía / BL": "DHL-442299103",
          "Origen": "Oaxaca, Oax.",
          "Destino": "Hamburg, Alemania",
          "ETD": datetime.date(2026, 10, 1),
          "ETA": datetime.date(2026, 10, 12),
          "Último Estatus Web": "In transit - Arrived at DHL Sort Facility",
      },
      {
          "ID": "CC-5003",
          "Producto": "Tequila Reposado (1,200 Cajas de Cristal)",
          "Transportista": "UPS Supply Chain",
          "Guía / BL": "UPS-1Z99999901",
          "Origen": "Tequila, Jalisco",
          "Destino": "Los Angeles, CA",
          "ETD": datetime.date(2026, 9, 28),
          "ETA": datetime.date(2026, 10, 5),
          "Último Estatus Web": "In transit - Delayed due to border congestion",
      },
      {
          "ID": "CC-5004",
          "Producto": "Arnés Eléctrico Automotriz (Lote A4)",
          "Transportista": "Maersk Line",
          "Guía / BL": "MSK-708912341",
          "Origen": "Ramos Arizpe, Coah.",
          "Destino": "Detroit, MI",
          "ETD": datetime.date(2026, 10, 2),
          "ETA": datetime.date(2026, 10, 9),
          "Último Estatus Web": "Delivered - Received by Dock 3",
      },
      {
          "ID": "CC-5005",
          "Producto": "Mango Tomy Atkins (Contenedor Atmosférico)",
          "Transportista": "KCSM / Ferromex",
          "Guía / BL": "FXE-330012998",
          "Origen": "Escuinapa, Sinaloa",
          "Destino": "Chicago, IL",
          "ETD": datetime.date(2026, 10, 6),
          "ETA": datetime.date(2026, 10, 14),
          "Último Estatus Web": "In transit - Railcar passing San Luis Potosí",
      },
      {
          "ID": "CC-5006",
          "Producto": "Núcleos e Intercambiadores de Calor (Cores)",
          "Transportista": "DHL Freight",
          "Guía / BL": "DHL-881203948",
          "Origen": "Apodaca, N.L.",
          "Destino": "Laredo, TX",
          "ETD": datetime.date(2026, 10, 7),
          "ETA": datetime.date(2026, 10, 11),
          "Último Estatus Web": "Out for delivery to border broker",
      },
  ])

# Interfaz Principal
st.title("📦 CrateCairn")
st.subheader("Vista Operativa y Rastreo Inteligente de Exportaciones")
st.markdown("---")

# Barra lateral para registrar nuevos envíos
with st.sidebar:
  st.header("➕ Registrar Nuevo Envío")
  with st.form("nuevo_envio"):
    prod = st.text_input("Producto / Lote / Carga")
    transportista = st.selectbox(
        "Paquetería / Naviera",
        ["DHL", "FedEx", "Maersk", "UPS", "Ferromex / KCSM", "Otro"],
    )
    guia = st.text_input("Número de Guía o BL")
    origen = st.text_input("Origen", value="Apodaca, N.L.")
    destino = st.text_input("Destino", value="Laredo, TX")
    etd = st.date_input("Fecha de Salida (ETD)", datetime.date.today())
    eta = st.date_input(
        "Fecha Estimada de Llegada (ETA)",
        datetime.date.today() + datetime.timedelta(days=4),
    )
    estatus_web = st.text_input(
        "Estatus de la Paquetería (Simula API)", value="In transit"
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

# SECCIÓN: Reporte Diario de Acción
if alertas > 0:
  st.error(
      f"⚠️ **REPORTE DIARIO DE ACCIÓN:** Se detectaron **{alertas} embarque(s)**"
      " con retrasos o inspecciones de aduana que requieren atención:"
  )
  df_alertas = df[df["Estatus Operativo CrateCairn"].str.contains("ALERTA")]
  st.dataframe(
      df_alertas[
          [
              "ID",
              "Producto",
              "Transportista",
              "Guía / BL",
              "Origen",
              "Destino",
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

st.markdown("### 📋 Vista General de la Operación de Exportación")
st.dataframe(df, use_container_width=True)
