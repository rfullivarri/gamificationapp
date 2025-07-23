import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurar la página
st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este es tu panel editable. Ingresá tu correo para acceder a tu base de datos personalizada.")

# CSS para zebra striping
st.markdown("""
    <style>
        thead tr th {
            background-color: #f0f2f6 !important;
        }
        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tbody tr:nth-child(odd) {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Input de email
email_input = st.text_input("📧 Ingresá tu correo electrónico")

# Si se ingresó el correo
if email_input:
    try:
        # Conectarse a Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
        client = gspread.authorize(credentials)

        # Abrir hoja de registros de usuario
        registro_sheet = client.open("FORMULARIO INTRO – SELF‑IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        # Buscar la fila con el correo ingresado (ignorando mayúsculas/minúsculas y espacios)
        user_data = df_registro[df_registro["Email"].str.strip().str.lower() == email_input.strip().lower()]

        if not user_data.empty:
            url = user_data.iloc[0]["GoogleSheetID"]
            if pd.isna(url) or not isinstance(url, str) or "/d/" not in url:
                st.error("⚠️ El enlace de Google Sheet no está bien formateado.")
            else:
                sheet_id = url.split("/d/")[1].split("/")[0]
                user_sheet = client.open_by_key(sheet_id).worksheet("BBDD")

                # Cargar datos desde la hoja "BBDD"
                all_data = user_sheet.get_all_values()
                df = pd.DataFrame(all_data[1:], columns=all_data[0])
                df = df.iloc[:, :5]  # Solo columnas A-E

                # Mostrar tabla editable
                edited_df = st.experimental_data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")

                # Botón para confirmar
                if st.button("✅ Confirmar edición"):
                    st.success("¡Cambios confirmados! Pronto se generará tu formulario de seguimiento diario.")
        else:
            st.warning("❌ No se encontró ningún registro con ese correo.")
    except Exception as e:
        st.error("🚨 Ocurrió un error al conectar con tu base de datos.")
        st.exception(e)
