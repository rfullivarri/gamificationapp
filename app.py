import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")

# ✨ Mensaje gamer motivador
st.markdown("""
> 🛠️ **Revisa tu tabla de tasks:**  
> Pulí tus misiones diarias. Editá, reemplazá o eliminá lo que no te sirva.  
> Solo vos sabés qué quests te acercan a tu mejor versión.  
> ¡Hacé que cada task valga XP real! 💪
""")

# 📝 Nota estilo Notion (disclaimer visual)
st.markdown("""
<div style="background-color:#f0f0f0; padding:15px; border-radius:8px; border-left:4px solid #999">
<b>📌 IMPORTANTE – Cómo deben ser tus Tasks</b><br>
✔️ Que puedas completarlas en un solo día.<br>
✔️ Deben ser claras, específicas y medibles.<br>
🚫 No uses frases vagas como “hacer algo saludable”.<br>
🎯 Mejor: “Preparar una comida saludable” o “Meditar 10 minutos”.<br>
♻️ Ideal si podés repetirlas cada semana.
</div>
""", unsafe_allow_html=True)

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# Ingreso del usuario
email_input = st.text_input("📧 Ingresá tu correo electrónico para acceder a tu base de datos personalizada:")

if email_input:
    try:
        # Acceso al registro de usuarios
        registro_sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
        registros = registro_sheet.get_all_records()
        df_registro = pd.DataFrame(registros)

        fila_usuario = df_registro[df_registro["Email"].str.strip().str.lower() == email_input.strip().lower()]

        if fila_usuario.empty:
            st.error("❌ No se encontró ninguna base de datos asociada a este correo.")
        else:
            # Cargar datos del usuario
            sheet_url = fila_usuario.iloc[0]["GoogleSheetID"]
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            sheet = client.open_by_key(sheet_id).worksheet("BBDD")

            all_data = sheet.get_all_values()
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            df = df.iloc[:, :5]  # Mostrar solo A-E

            # Editor interactivo para modificar (solo esta tabla se muestra)
            st.markdown("""
            <div style="background-color:#f7f7f7; padding:20px; border-radius:10px; border: 1px solid #e0e0e0; margin-top:20px; margin-bottom:20px;">
            <h4 style="margin-top: 0;">🧾 Tu tabla de tasks:</h4>
            """, unsafe_allow_html=True)

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                key="editor",
                hide_index=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("✅ Confirmar edición"):
                new_data = [edited_df.columns.tolist()] + edited_df.values.tolist()
                sheet.clear()
                sheet.update("A1", new_data)

                st.success("✅ Cambios guardados correctamente.")
                # (Aquí se disparará el script del Google Form)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
