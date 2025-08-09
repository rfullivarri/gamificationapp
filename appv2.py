import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import hashlib
import requests
from gspread.utils import rowcol_to_a1

# -------- util BOBO --------
def enviar_formulario_bobo():
    url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLScS9L8mDIa934tEhkmnq0O7LhVat-9mrL6O6GOec-7JlK7tXQ/formResponse"
    data = {"entry.1871872872": "Sí"}
    try:
        requests.post(url_formulario, data=data, timeout=10)
    except Exception:
        pass

# -------- UI --------
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🪄 Conf BBDD & Daily Quest")

st.markdown("""
> 🛠️ **Revisá tu tabla de tasks:**  
> Pulí tus misiones diarias. Editá, reemplazá o eliminá lo que no te sirva.  
> Solo vos sabés qué quests te acercan a tu mejor versión.  
> ¡Hacé que cada task valga XP real! 💪
""")

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

# -------- auth --------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

def generar_hash_bbdd(df):
    raw = df.astype(str).apply(lambda x: ''.join(x), axis=1).sum()
    return hashlib.md5(raw.encode()).hexdigest()

# catálogos
PILARES_OPTS = ["Body", "Mind", "Soul"]
DIFICULTAD_OPTS = ["Fácil", "Media", "Difícil"]

RASGOS_BODY = ["Energía","Nutrición","Sueño","Recuperación","Hidratación",
               "Higiene","Vitalidad","Postura","Movilidad","Moderación"]
RASGOS_MIND = ["Enfoque","Aprendizaje","Creatividad","Gestión","Autocontrol",
               "Resiliencia","Orden","Proyección","Finanzas","Agilidad"]
RASGOS_SOUL = ["Conexión","Espiritualidad","Propósito","Valores","Altruismo",
               "Insight","Gratitud","Naturaleza","Gozo","Autoestima"]

def rasgos_combo():
    return (
        [f"{r}, Body" for r in RASGOS_BODY] +
        [f"{r}, Mind" for r in RASGOS_MIND] +
        [f"{r}, Soul" for r in RASGOS_SOUL]
    )

def clean_rasgo(val: str) -> str:
    s = (val or "").strip()
    if "," in s:
        return s.split(",")[0].strip()
    return s

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

            # -------- leer BBDD --------
            values = bbdd_ws.get(f"A1:H{bbdd_ws.row_count}")
            headers, rows = values[0], values[1:]
            df_actual = pd.DataFrame(rows, columns=headers).fillna("")

            # subset visible
            df_visible = df_actual[["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]].copy()

            # opciones para Rasgo:
            #  - incluir TODOS los rasgos existentes (para que no aparezcan como None)
            #  - más las opciones "Rasgo, Pilar"
            rasgos_existentes = sorted(set(df_visible["Rasgo"].astype(str).str.strip()) - {""})
            RASGO_SELECT_OPTIONS = sorted(set(rasgos_existentes + rasgos_combo()))

            st.markdown("## 🧾 Tasks")
            st.caption("Revisa tus tasks y edítalas o elimínalas para que se ajusten a tus objetivos.")

            df_editado = st.data_editor(
                df_visible,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Pilares": st.column_config.SelectboxColumn(
                        "Pilares", options=PILARES_OPTS, help="Elegí Body / Mind / Soul"
                    ),
                    "Rasgo": st.column_config.SelectboxColumn(
                        "Rasgo",
                        options=RASGO_SELECT_OPTIONS,
                        help="Podés elegir un rasgo existente o una opción 'Rasgo, Pilar'. Al guardar, se guardará sólo el Rasgo."
                    ),
                    "Dificultad": st.column_config.SelectboxColumn(
                        "Dificultad", options=DIFICULTAD_OPTS
                    ),
                },
            )

            if st.button("✅ Confirmar cambios"):
                # limpiar valores: si eligieron "Rasgo, Pilar", guardamos sólo el rasgo
                df_guardar = df_editado.copy()
                df_guardar["Rasgo"] = df_guardar["Rasgo"].apply(clean_rasgo)
                df_guardar["Pilares"] = df_guardar["Pilares"].fillna("")
                df_guardar["Stats"] = df_guardar["Stats"].fillna("")
                df_guardar["Tasks"] = df_guardar["Tasks"].fillna("")
                df_guardar["Dificultad"] = df_guardar["Dificultad"].fillna("")

                hash_original = generar_hash_bbdd(df_actual[["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]])
                hash_nuevo = generar_hash_bbdd(df_guardar)

                if hash_original == hash_nuevo:
                    setup_ws.update_acell("E14", "constante")
                    st.success("✅ No hubo cambios. Tu base sigue igual.")
                else:
                    estado_actual = (setup_ws.acell("E14").value or "").strip()
                    nuevo_estado = "primera" if estado_actual == "" else "modificada"
                    setup_ws.update_acell("E14", nuevo_estado)

                    # hábitos logrados (tasks removidas)
                    tareas_anteriores = set(df_actual["Tasks"])
                    tareas_nuevas = set(df_guardar["Tasks"])
                    tareas_logradas = [t for t in tareas_anteriores - tareas_nuevas if t]

                    if tareas_logradas:
                        habitos_ws = ss.worksheet("Habitos Logrados")
                        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        columnas = df_actual.columns.tolist()
                        nuevas_filas = []
                        for tarea in tareas_logradas:
                            fila = df_actual[df_actual["Tasks"] == tarea]
                            if not fila.empty:
                                fila_data = fila.iloc[0]
                                xp = fila_data["EXP"] if "EXP" in columnas else 0
                                try:
                                    xp = int(float(xp))
                                except Exception:
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
                        if nuevas_filas:
                            habitos_ws.append_rows(nuevas_filas)

                    # -------- guardar BBDD (solo A:E) --------
                    df_guardar = df_guardar.fillna("")
                    num_filas = len(df_guardar)
                    if num_filas == 0:
                        # limpiar si quedó vacío
                        bbdd_ws.batch_clear([f"A2:E{bbdd_ws.row_count}"])
                    else:
                        bbdd_ws.batch_clear([f"A2:E{bbdd_ws.row_count}"])
                        bbdd_ws.update("A1:E1", [["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]])
                        bbdd_ws.update("A2", df_guardar.values.tolist())

                    # marcar en registros + webhook BOBO
                    for idx, fila in enumerate(registros, start=2):
                        if fila["Email"].strip().lower() == email.strip().lower():
                            registros_ws.update_cell(idx, 6, "SI")
                            registros_ws.update_cell(idx, 7, email)
                            break

                    enviar_formulario_bobo()
                    st.success("✅ Cambios confirmados. ¡Estamos configurando tu Daily Quest!")

            # botón volver
            dashboard_url = f"https://rfullivarri.github.io/gamificationweblanding/dashboardv3.html?email={email.strip()}"
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center;">
                    <a href="{dashboard_url}" target="_blank" style="
                        display: inline-block;
                        padding: 8px 18px;
                        background-color: #6c63ff;
                        color: white;
                        border-radius: 6px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: background-color 0.3s;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        font-size: 14px;">
                        🎮 Volver a tu Dashboard
                    </a>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al cargar o guardar los datos: {e}")
