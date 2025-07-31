import json
import streamlit as st
import pandas as pd
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

def enviar_formulario_bobo(email_usuario):
    url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLScS9L8mDIa934tEhkmnq0O7LhVat-9mrL6O6GOec-7JlK7tXQ/formResponse"
    
    data = {
        "entry.1871872872": "Sí"  # Marcamos el checkbox de forma automática
    }

    response = requests.post(url_formulario, data=data)
    
    if response.status_code in [200, 302]:
        print("✅ Formulario BOBO enviado correctamente.")
    else:
        print(f"❌ Error al enviar formulario BOBO: {response.status_code}")

# Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")

# ✨ Mensaje gamer motivador
st.markdown("""
> 🛠️ **Revisá tu tabla de tasks:**  
> Pulí tus misiones diarias. Editá, reemplazá o eliminá lo que no te sirva.  
> Solo vos sabés qué quests te acercan a tu mejor versión.  
> ¡Hacé que cada task valga XP real! 💪
""")

# 📝 Nota estilo Notion
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
            df = df.iloc[:, :5]  # Mostrar solo columnas A-E

            # Contenedor visual con fondo gris
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

            # Botón para guardar cambios
            if st.button("✅ Confirmar edición"):
                try:
                    # Guardar la nueva tabla sin romper columnas a la derecha
                    new_data = [edited_df.columns.tolist()] + edited_df.values.tolist()
                    num_filas_nuevas = len(new_data)
                    # 1. Limpiar SOLO A2:E sin afectar fórmulas
                    sheet.batch_update([{
                        "range": f"A2:E{sheet.row_count}",
                        "values": [[""] * 5 for _ in range(sheet.row_count - 1)]
                    }])
                    # 2. Pegar encabezado
                    sheet.update("A1:E1", [new_data[0]])
                    # 3. Pegar fila por fila a partir de A2
                    for i, fila in enumerate(new_data[1:], start=2):
                        rango_fila = f"A{i}:E{i}"
                        sheet.update(rango_fila, [fila])
                    st.success("✅ BBDD modificada y guardada.")

                    # ✅ Confirmar en el archivo de registros directamente
                    try:
                        registros_sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)").worksheet("Registros de Usuarios")
                        registros_data = registros_sheet.get_all_values()

                        encontrado = False
                        for idx, fila in enumerate(registros_data[1:], start=2):  # Saltear encabezado
                            correo_col_a = fila[0].strip().lower()
                            if correo_col_a == email_input.strip().lower():
                                # ✍️ Guardar el correo en columna G (índice 7)
                                registros_sheet.update_cell(idx, 7, email_input)

                                # ✅ Confirmar la BBDD en columna F (índice 6)
                                registros_sheet.update_cell(idx, 6, "SI")

                                enviar_formulario_bobo(email_input)
                                st.success("✅ Estamos configurando tu Daily Quest")
                                encontrado = True
                                break

                        if not encontrado:
                            st.warning("⚠️ No se encontró el correo en Registros de Usuarios.")

                    except Exception as e:
                        st.error(f"❌ Error al confirmar en Registros de Usuarios: {e}")

                except Exception as e:
                    st.error(f"❌ Error al guardar o confirmar: {e}")

    except Exception as e:
        st.error(f"⚠️ Error al cargar los datos: {e}")


