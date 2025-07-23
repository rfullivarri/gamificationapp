import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este es un prototipo editable conectado a tu Google Sheet.")

# Autenticación con Google
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# INPUT: correo del usuario
user_email = st.text_input("📧 Ingresá tu correo electrónico para ver tu tabla personalizada:")

if user_email:
    try:
        # Abrimos el archivo con los registros de usuarios
        registro_sheet = client.open("FORMULARIO INTRO – SELF‑IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        # Limpieza de datos
        df_registro["Email"] = df_registro["Email"].str.strip().str.lower()
        user_email = user_email.strip().lower()
        df_registro["Fecha"] = pd.to_datetime(df_registro["Fecha"], errors="coerce")

        # Mostrar tabla para debug
        st.subheader("📋 Registros cargados:")
        st.dataframe(df_registro)

        # Filtrar registros por email
        df_usuario = df_registro[df_registro["Email"] == user_email]

        if df_usuario.empty:
            st.warning(f"No se encontró ningún registro para el correo: {user_email}")
            st.info("Verificá que esté bien escrito, sin espacios ni mayúsculas.")
        else:
            registro_actual = df_usuario.sort_values("Fecha", ascending=False).iloc[0]
            sheet_url = registro_actual["GoogleSheetID"]

            if not sheet_url or "docs.google.com" not in sheet_url:
                st.error("⚠️ El campo 'GoogleSheetID' está vacío o mal formateado.")
            else:
                try:
                    # Extraer ID del Google Sheet
                    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                    sheet = client.open_by_key(sheet_id).worksheet("BBDD")

                    # Leer tabla hasta la columna E
                    all_data = sheet.get_all_values()
                    df = pd.DataFrame(all_data[1:], columns=all_data[0])
                    df = df.iloc[:, :5]  # Solo columnas A hasta E

                    # Interfaz editable completa
                    st.subheader("📝 Editá tu tabla personalizada:")
                    edited_df = st.data_editor(
                        df,
                        use_container_width=True,
                        num_rows="dynamic",
                        hide_index=True,
                        key="editor"
                    )

                    # Botón de confirmación
                    if st.button("✅ Confirmar edición"):
                        st.success("Datos confirmados. ¡Próximo paso: generación del formulario de seguimiento diario!")
                        # 🔜 Enviar señal a Google Sheets (script aún pendiente de integración)

                except Exception as e:
                    st.error("❌ No se pudo acceder al archivo vinculado.")
                    st.exception(e)

    except Exception as e:
        st.error("❌ No se pudo abrir la hoja de registros de usuarios.")
        st.exception(e)
