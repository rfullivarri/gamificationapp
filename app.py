import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de página
st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este panel permite editar tu base de datos gamificada personalizada.")

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["google_service_account"], scope
)
client = gspread.authorize(credentials)

# 🔍 Paso 1: pedir correo
user_email = st.text_input("📧 Ingresá tu correo electrónico para continuar").strip().lower()

if user_email:
    try:
        # 🧾 Abrir archivo maestro de registros
        registro_sheet = client.open("FORMULARIO INTRO – SELF‑IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        if df_registro.empty:
            st.warning("⚠️ La hoja de registros está vacía.")
        else:
            # Limpieza y validación
            df_registro["Fecha"] = pd.to_datetime(df_registro["Fecha"], errors="coerce")
            df_registro = df_registro.dropna(subset=["Fecha"])

            # Filtrar por email
            df_usuario = df_registro[df_registro["Email"].str.strip().str.lower() == user_email]

            if df_usuario.empty:
                st.warning("❌ No se encontró ningún registro con ese correo.")
            else:
                # 🕒 Buscar el más reciente
                registro_actual = df_usuario.sort_values("Fecha", ascending=False).iloc[0]
                sheet_url = registro_actual["GoogleSheetID"]

                if not sheet_url or "docs.google.com" not in sheet_url:
                    st.error("⚠️ El campo 'GoogleSheetID' está vacío o mal formateado.")
                else:
                    try:
                        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                        sheet = client.open_by_key(sheet_id).worksheet("BBDD")

                        # Obtener datos y limitar hasta columna E
                        all_data = sheet.get_all_values()
                        df = pd.DataFrame(all_data[1:], columns=all_data[0])
                        df = df.iloc[:, :5]

                        st.subheader("📝 Editá tu base de datos (hasta columna E):")
                        edited_df = st.data_editor(
                            df,
                            use_container_width=True,
                            num_rows="dynamic",
                            hide_index=True,
                            key="editor"
                        )

                        # Botón de confirmación
                        if st.button("✅ Confirmar edición"):
                            st.success("✅ Edición confirmada. Próximo paso: generación del formulario de seguimiento diario.")
                            # 🔜 Aquí va la llamada al Apps Script externo

                    except Exception as e:
                        st.error("🚫 No se pudo acceder al archivo duplicado de Google Sheets. Verificá permisos y formato del ID.")
                        st.exception(e)

    except Exception as e:
        st.error("🚫 No se pudo acceder al archivo maestro de registros.")
        st.exception(e)
