
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import hashlib
import requests
from gspread.utils import rowcol_to_a1

# Función para simular envío al formulario BOBO
def enviar_formulario_bobo():
    url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLScS9L8mDIa934tEhkmnq0O7LhVat-9mrL6O6GOec-7JlK7tXQ/formResponse"
    data = {
        "entry.1871872872": "Sí"
    }
    response = requests.post(url_formulario, data=data)
    if response.status_code in [200, 302]:
        print("✅ Formulario BOBO enviado correctamente.")
    else:
        print(f"❌ Error al enviar formulario BOBO: {response.status_code}")

# Configuración
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🪄 Conf BBDD & Daily Quest")

# Mensaje motivador
st.markdown("""
> 🛠️ **Revisá tu tabla de tasks:**  
> Pulí tus misiones diarias. Editá, reemplazá o eliminá lo que no te sirva.  
> Solo vos sabés qué quests te acercan a tu mejor versión.  
> ¡Hacé que cada task valga XP real! 💪
""")

# Nota Notion
st.markdown('''
<div style="background-color:#f0f0f0; padding:15px; border-radius:8px; border-left:4px solid #999">
<b>📌 IMPORTANTE – Cómo deben ser tus Tasks</b><br>
✔️ Que puedas completarlas en un solo día.<br>
✔️ Deben ser claras, específicas y medibles.<br>
🚫 No uses frases vagas como “hacer algo saludable”.<br>
🎯 Mejor: “Preparar una comida saludable” o “Meditar 10 minutos”.<br>
♻️ Ideal si podés repetirlas cada semana.
</div>
''', unsafe_allow_html=True)

# Autenticación
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# Función hash para detectar cambios
def generar_hash_bbdd(df):
    raw = df.astype(str).apply(lambda x: ''.join(x), axis=1).sum()
    return hashlib.md5(raw.encode()).hexdigest()

# Ingreso
email = st.text_input("📧 Ingresá tu correo electrónico para acceder a tu base de datos personalizada:")

if email:
    try:
        form_intro = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
        registros_ws = form_intro.worksheet("Registros de Usuarios")
        registros = registros_ws.get_all_records()
        fila_usuario = next((r for r in registros if r["Email"].strip().lower() == email.strip().lower()), None)

        if not fila_usuario:
            st.error("❌ No se encontró ninguna base de datos asociada a este correo.")
        else:
            sheet_id = fila_usuario["GoogleSheetID"].split("/d/")[1].split("/")[0]
            ss = client.open_by_key(sheet_id)
            bbdd_ws = ss.worksheet("BBDD")
            setup_ws = ss.worksheet("Setup")

            # Cargar BBDD
            values = bbdd_ws.get(f"A1:H{bbdd_ws.row_count}")
            headers, rows = values[0], values[1:]
            df_actual = pd.DataFrame(rows, columns=headers)
            df_visible = df_actual[["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]]

            st.markdown("## 🧾 Tasks")
            st.markdown("> Revisa tus tasks y edítalas o elimínalas para que se ajusten a tus objetivos.")

            df_editado = st.data_editor(df_visible, num_rows="dynamic", use_container_width=True)

            if st.button("✅ Confirmar cambios"):
                hash_original = generar_hash_bbdd(df_actual[["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]])
                hash_nuevo = generar_hash_bbdd(df_editado)

                if hash_original == hash_nuevo:
                    setup_ws.update_acell("E14", "constante")
                    st.success("✅ No hubo cambios. Tu base sigue igual.")
                else:
                    setup_ws.update_acell("E14", "modificada")
                    tareas_anteriores = set(df_actual["Tasks"])
                    tareas_nuevas = set(df_editado["Tasks"])
                    tareas_logradas = tareas_anteriores - tareas_nuevas

                    if tareas_logradas:
                        habitos_ws = ss.worksheet("Habitos Logrados")
                        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        columnas = df_actual.columns.tolist()
                        nuevas_filas = []
                        for tarea in tareas_logradas:
                            fila = df_actual[df_actual["Tasks"] == tarea]
                            if not fila.empty:
                                fila_data = fila.iloc[0]
                    
                                # ✅ Asegurar que XP es número entero, sin comillas
                                xp = fila_data["EXP"] if "EXP" in columnas else 0
                                try:
                                    xp = int(float(xp))  # Convierte incluso si viene como "11.0"
                                except:
                                    xp = 0
                    
                                nuevas_filas.append([
                                    timestamp,
                                    fila_data["Pilares"],
                                    fila_data["Rasgo"],
                                    fila_data["Stats"],
                                    fila_data["Tasks"],
                                    fila_data["Dificultad"],
                                    xp
                                ])
                        habitos_ws.append_rows(nuevas_filas)

                    # Reemplazar SOLO columnas A a E en la hoja BBDD
                    num_filas = bbdd_ws.row_count
                    rango_a_e = f"A2:E{num_filas}"
                    bbdd_ws.batch_clear([rango_a_e])
                    bbdd_ws.update("A1:E1", [["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]])
                    bbdd_ws.update("A2", df_editado.values.tolist())

                    # Confirmar en registros y lanzar BOBO
                    for idx, fila in enumerate(registros, start=2):
                        if fila["Email"].strip().lower() == email.strip().lower():
                            registros_ws.update_cell(idx, 6, "SI")
                            registros_ws.update_cell(idx, 7, email)
                            break

                    enviar_formulario_bobo()
                    st.success("✅ Cambios confirmados. ¡Estamos configurando tu Daily Quest!")
            # Botón "Volver al Dashboard" centrado como el de Confirmar edición
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <a href="{dashboard_url}" target="_blank" style="
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #6c63ff;
                        color: white;
                        border-radius: 6px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: background-color 0.3s;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        🎮 Volver a tu Dashboard
                    </a>
                </div>
                """, unsafe_allow_html=True)       
    except Exception as e:
        st.error(f"❌ Error al cargar o guardar los datos: {e}")
