import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de página
st.set_page_config(page_title="Gamification Dashboard", layout="wide")

# Título
st.title("🎮 Gamification Dashboard")

# Ingreso de correo
email_input = st.text_input("Ingresá tu correo electrónico")

# CSS para evitar scroll + filas alternadas
st.markdown("""
    <style>
        .stDataFrame div[role="table"] {
            max-height: none !important;
            overflow: visible !important;
        }
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

# Si hay email, buscar hoja correspondiente
if email_input:
    try:
        # Autenticación con Google
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
        client = gspread.authorize(credentials)

        # Buscar hoja de registros de usuario
        registro_sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        # Buscar el sheet del usuario
        user_data = df_registro[df_registro["Email"].str.lower() == email_input.strip().lower()]
        if not user_data.empty:
            url = user_data.iloc[0]["GoogleSheetID"]
            sheet_id = url.split("/d/")[1].split("/")[0]
            user_sheet = client.open_by_key(sheet_id).worksheet("BBDD")

            # Obtener datos y limitar columnas
            all_data = user_sheet.get_all_values()
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            df = df.iloc[:, :5]

            # Editor interactivo
            edited_df = st.experimental_data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")

            # Botón para confirmar edición
            if st.button("✅ Confirmar edición"):
                st.success("Cambios confirmados. Pronto se generará el formulario de seguimiento.")
        else:
            st.warning("❌ No se encontró ningún registro con ese correo.")
    except Exception as e:
        st.error("🚨 Ocurrió un error al conectar con tu base de datos. Verificá el correo o intentá más tarde.")
