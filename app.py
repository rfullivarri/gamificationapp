import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este es tu panel editable de inicio. Editá, eliminá o confirmá tu tabla gamificada.")

# Configuración de credenciales
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

### 1. LEEMOS EL ARCHIVO DE REGISTROS DE USUARIOS
registro_sheet = client.open("FORMULARIO INTRO – SELF‑IMPROVEMENT JOURNEY (respuestas)")
registro_data = registro_sheet.worksheet("Registros de Usuarios").get_all_records()

if not registro_data:
    st.warning("Aún no hay registros disponibles.")
    st.stop()

df_registro = pd.DataFrame(registro_data)

# Pedimos al usuario su email
email_usuario = st.text_input("📧 Ingresá tu correo electrónico registrado para continuar:")

if not email_usuario:
    st.stop()

# Filtramos los registros por email y tomamos el más reciente por fecha
df_registro["Fecha"] = pd.to_datetime(df_registro["Fecha"])
filtro_usuario = df_registro[df_registro["Email"] == email_usuario]

if filtro_usuario.empty:
    st.error("No se encontraron registros para ese email.")
    st.stop()

registro_reciente = filtro_usuario.sort_values("Fecha", ascending=False).iloc[0]
sheet_id_usuario = registro_reciente["GoogleSheetID"]

### 2. ACCEDEMOS AL SHEET PERSONALIZADO
try:
    sheet_usuario = client.open_by_key(sheet_id_usuario).worksheet("BBDD")
except Exception as e:
    st.error(f"No se pudo acceder al Sheet del usuario: {e}")
    st.stop()

# Cargamos los datos y mostramos solo hasta columna E
raw_data = sheet_usuario.get_all_values()
df = pd.DataFrame(raw_data[1:], columns=raw_data[0])  # Encabezados en la fila 1
df = df.iloc[:, :5]  # Solo columnas A-E

# Mostramos tabla completa sin scroll
st.markdown("### 📋 Tabla de Base de Datos (editable)")
edited_df = st.experimental_data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")

# Botón de confirmación
if st.button("✅ Confirmar edición"):
    st.success("Datos confirmados. Próximamente se generará tu formulario de seguimiento diario.")
    # 🚀 En el siguiente paso, se disparará un Apps Script en Google Sheets
