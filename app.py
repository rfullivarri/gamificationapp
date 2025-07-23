import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración general de la app
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.write("Este es tu panel inicial de edición de base de datos personalizada.")

# Conexión al Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# Ingreso de correo del usuario
email_input = st.text_input("📧 Ingresá tu correo electrónico para acceder a tu base de datos personalizada:")

if email_input:
    try:
        # Abrimos el archivo maestro de registros
        registro_sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()

        # Convertimos en DataFrame para filtrar
        df_registro = pd.DataFrame(registros)

        # Buscamos el GoogleSheetID correspondiente
        fila_usuario = df_registro[df_registro["Email"].str.strip().str.lower() == email_input.strip().lower()]

        if fila_usuario.empty:
            st.error("❌ No se encontró ninguna base de datos asociada a este correo.")
        else:
            # Obtenemos la URL desde la columna GoogleSheetID
            sheet_url = fila_usuario.iloc[0]["GoogleSheetID"]

            # Extraemos el ID del URL
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]

            # Accedemos al archivo de ese usuario y su hoja 'BBDD'
            sheet = client.open_by_key(sheet_id).worksheet("BBDD")

            # Obtenemos los datos
            all_data = sheet.get_all_values()
            df = pd.DataFrame(all_data[1:], columns=all_data[0])  # Ignora header
            df = df.iloc[:, :5]  # Solo columnas A a E (Pilar, Rasgo, Stat, Task, Dificultad)

            # Interfaz editable sin scroll vertical (usa altura automática)
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")

            # Botón de confirmación
            if st.button("✅ Confirmar edición"):
                st.success("¡Cambios confirmados! Tu camino de mejora ya está en marcha 💪")
                # (En el futuro: lanzar script para generar el Google Form de seguimiento diario)

    except Exception as e:
        st.error(f"Error: {e}")
