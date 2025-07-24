import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración general de la app
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.markdown("""
📌 **IMPORTANTE – Cómo deben ser tus Tasks**  
- Deben poder completarse en un día.  
- Que sean concretas, claras y medibles.  
- No uses tareas vagas como "cuidarme más" → Mejor: "Preparar una comida saludable".  
- Ideal que puedan repetirse cada semana.

✍️ **Ejemplos correctos:**  
- Leer 5 páginas de un libro  
- Meditar 10 minutos  
- Preparar vianda para mañana  
""")

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# Ingreso del usuario
email_input = st.text_input("📧 Ingresá tu correo electrónico para acceder a tu base de datos personalizada:")

if email_input:
    try:
        # Accedemos al registro de usuarios
        registro_sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        # Buscamos el mail
        fila_usuario = df_registro[df_registro["Email"].str.strip().str.lower() == email_input.strip().lower()]

        if fila_usuario.empty:
            st.error("❌ No se encontró ninguna base de datos asociada a este correo.")
        else:
            # URL del Sheet
            sheet_url = fila_usuario.iloc[0]["GoogleSheetID"]
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            sheet = client.open_by_key(sheet_id).worksheet("BBDD")

            # Datos de la BBDD
            all_data = sheet.get_all_values()
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            df = df.iloc[:, :5]  # A-E: Pilar, Rasgo, Stat, Task, Dificultad

            # Mostrar tabla editable
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                key="editor",
                hide_index=True
            )

            # Botón para guardar cambios y lanzar script
            if st.button("✅ Confirmar edición"):
                # Guardar cambios en la hoja
                new_data = [edited_df.columns.tolist()] + edited_df.values.tolist()
                sheet.clear()
                sheet.update("A1", new_data)

                st.success("✅ Cambios guardados correctamente.")
                # 🔜 Aquí vamos a ejecutar el script de creación de Google Form
                # (Lo agregamos en el próximo paso)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
