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

# --- Estilos mínimos alineados al dashboard (morado + panel oscuro)
st.markdown("""
<style>
:root { --brand:#7d3cff; --ink:#e8e6ff; --panel:#101426; --soft:#1a2036; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; }
.gj-info{
  background: var(--panel);
  border-left:4px solid var(--brand);
  padding:16px;border-radius:10px;color:var(--ink);
  box-shadow:0 2px 10px rgba(0,0,0,.18)
}
.gj-btn{
  display:inline-block;padding:10px 18px;background:var(--brand);color:white;
  border-radius:8px;text-decoration:none;font-weight:700;
  box-shadow:0 2px 6px rgba(0,0,0,.18)
}
.gj-btn:hover{ filter:brightness(1.07); }
h1, h2, h3 { color: var(--ink); }
</style>
""", unsafe_allow_html=True)

st.title("🪄 Conf BBDD & Daily Quest")

st.markdown("""
> 🛠️ **Revisá tu tabla de tasks:**  
> Pulí tus misiones diarias. Editá, reemplazá o eliminá lo que no te sirva.  
> Solo vos sabés qué quests te acercan a tu mejor versión.  
> ¡Hacé que cada task valga XP real! 💪
""")

st.markdown('''
<div class="gj-info">
<b>📌 IMPORTANTE – Cómo deben ser tus Tasks</b><br>
✔️ Que puedas completarlas en un solo día.<br>
✔️ Deben ser claras, específicas y medibles.<br>
🚫 No uses frases vagas como “hacer algo saludable”.<br>
🎯 Mejor: “Preparar una comida saludable” o “Meditar 10 minutos”.<br>
♻️ Ideal si podés repetirlas cada semana.
</div>
''', unsafe_allow_html=True)

# ===== email desde querystring (API nueva) =====
qp = st.query_params
email = (qp.get("email", "") or "").strip().lower()

if not email:
    # 🔎 DEBUG TEMPORAL
    st.warning("No se detectó tu email. Abrí esta página desde el Dashboard (menú → **Editar Base**).")
    st.info(f"query_params recibidos: {dict(qp)}")  # <- sacalo cuando funcione
    st.stop()

# -------- auth --------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

def generar_hash_bbdd(df):
    raw = df.astype(str).apply(lambda x: ''.join(x), axis=1).sum()
    return hashlib.md5(raw.encode()).hexdigest()

# -------- catálogos globales --------
PILARES_OPTS = ["Body", "Mind", "Soul"]
DIFICULTAD_OPTS = ["Fácil", "Media", "Difícil"]

RASGOS_POR_PILAR = {
    "Body": ["Energía","Nutrición","Sueño","Recuperación","Hidratación",
             "Higiene","Vitalidad","Postura","Movilidad","Moderación"],
    "Mind": ["Enfoque","Aprendizaje","Creatividad","Gestión","Autocontrol",
             "Resiliencia","Orden","Proyección","Finanzas","Agilidad"],
    "Soul": ["Conexión","Espiritualidad","Propósito","Valores","Altruismo",
             "Insight","Gratitud","Naturaleza","Gozo","Autoestima"],
}

def rasgos_combo():
    out = []
    for pilar, rasgos in RASGOS_POR_PILAR.items():
        out += [f"{r}, {pilar}" for r in rasgos]
    return out

def clean_rasgo(val: str) -> str:
    s = (val or "").strip()
    if "," in s:
        return s.split(",")[0].strip()
    return s

# -------- app --------
try:
    # === Registros de Usuarios
    form_intro = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    registros_ws = form_intro.worksheet("Registros de Usuarios")
    registros = registros_ws.get_all_records()
    fila_usuario = next((r for r in registros if r["Email"].strip().lower() == email), None)

    if not fila_usuario:
        st.error("❌ No se encontró ninguna base de datos asociada a este correo.")
        st.stop()

    sheet_id = fila_usuario["GoogleSheetID"].split("/d/")[1].split("/")[0]
    ss = client.open_by_key(sheet_id)
    bbdd_ws = ss.worksheet("BBDD")
    setup_ws = ss.worksheet("Setup")

    # -------- leer BBDD --------
    values = bbdd_ws.get(f"A1:H{bbdd_ws.row_count}")
    headers = values[0] if values else ["Pilares","Rasgo","Stats","Tasks","Dificultad"]
    rows = values[1:] if len(values) > 1 else []
    df_actual = pd.DataFrame(rows, columns=headers).fillna("")

    # subset visible
    df_visible = df_actual[["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]].copy()

    # opciones que ya existen (para que no se vean celdas vacías)
    pilares_existentes = sorted(set(df_visible["Pilares"].astype(str).str.strip()) - {""})
    dificultad_existentes = sorted(set(df_visible["Dificultad"].astype(str).str.strip()) - {""})
    rasgos_existentes = sorted(set(df_visible["Rasgo"].astype(str).str.strip()) - {""})

    PILAR_SELECT_OPTIONS = sorted(set(PILARES_OPTS + pilares_existentes))
    DIFICULTAD_SELECT_OPTIONS = sorted(set(DIFICULTAD_OPTS + dificultad_existentes))
    RASGO_SELECT_OPTIONS = sorted(set(rasgos_existentes + rasgos_combo()))

    # editor (UNICO)
    st.markdown("## 🧾 Tasks")
    st.caption("Revisá tus tasks y edítalas o eliminálas para que se ajusten a tus objetivos.")

    df_editado = st.data_editor(
        df_visible,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Pilares": st.column_config.SelectboxColumn(
                "Pilares",
                options=PILAR_SELECT_OPTIONS,
                help="Elegí Body / Mind / Soul (se mantienen los valores existentes)."
            ),
            "Rasgo": st.column_config.SelectboxColumn(
                "Rasgo",
                options=RASGO_SELECT_OPTIONS,
                help="Podés elegir un rasgo existente o 'Rasgo, Pilar'. Al guardar se quedará solo el Rasgo."
            ),
            "Dificultad": st.column_config.SelectboxColumn(
                "Dificultad",
                options=DIFICULTAD_SELECT_OPTIONS
            ),
        },
    )

    if st.button("✅ Confirmar cambios"):
        # normalizaciones SOLO al guardar
        df_guardar = df_editado.copy()
        df_guardar["Rasgo"] = df_guardar["Rasgo"].apply(clean_rasgo)

        _map_pilar = {"body":"Body","mind":"Mind","soul":"Soul","cuerpo":"Body","mente":"Mind","alma":"Soul"}
        df_guardar["Pilares"] = df_guardar["Pilares"].astype(str).apply(
            lambda v: _map_pilar.get(v.strip().lower(), v.strip())
        )

        _map_diff = {"facil":"Fácil","fácil":"Fácil","media":"Media","medio":"Media","dificil":"Difícil","difícil":"Difícil"}
        df_guardar["Dificultad"] = df_guardar["Dificultad"].astype(str).apply(
            lambda v: _map_diff.get(v.strip().lower(), v.strip())
        )

        df_guardar[["Pilares","Rasgo","Stats","Tasks","Dificultad"]] = \
            df_guardar[["Pilares","Rasgo","Stats","Tasks","Dificultad"]].fillna("")

        # detectar cambios
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
                # abrir hoja con o sin tilde; crear si no existe
                try:
                    habitos_ws = ss.worksheet("Hábitos Logrados")
                except Exception:
                    try:
                        habitos_ws = ss.worksheet("Habitos Logrados")
                    except Exception:
                        habitos_ws = ss.add_worksheet(title="Hábitos Logrados", rows=100, cols=10)
                        habitos_ws.update("A1:G1", [["Fecha","Pilares","Rasgo","Stats","Tasks","Dificultad","EXP"]])

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

            # guardar BBDD (solo A:E) — PEGADO SEGURO
            df_out = df_guardar[["Pilares","Rasgo","Stats","Tasks","Dificultad"]].fillna("")
            n_rows = len(df_out)

            # 1) limpiar SOLO A2:E (sin tocar fórmulas de F en adelante)
            bbdd_ws.batch_clear([f"A2:E{bbdd_ws.row_count}"])

            # 2) reponer header por las dudas
            bbdd_ws.update("A1:E1", [["Pilares", "Rasgo", "Stats", "Tasks", "Dificultad"]])

            # 3) pegar EXACTO en A2:E{end}
            if n_rows > 0:
                end_row = 1 + n_rows  # fila final (incluye header en 1)
                bbdd_ws.update(f"A2:E{end_row}", df_out.values.tolist())

            # marcar en registros + webhook BOBO
            for idx, fila in enumerate(registros, start=2):
                if fila["Email"].strip().lower() == email:
                    registros_ws.update_cell(idx, 6, "SI")
                    registros_ws.update_cell(idx, 7, email)
                    break

            enviar_formulario_bobo()
            st.success("✅ Cambios confirmados. ¡Estamos configurando tu Daily Quest!")

    # botón volver (misma pestaña con look morado)
    dashboard_url = f"https://rfullivarri.github.io/gamificationweblanding/dashboardv3.html?email={email}"
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.5, 1])
    with col2:
        st.markdown(
            f'<div style="text-align:center;"><a class="gj-btn" href="{dashboard_url}" '
            f'onclick="window.location.href=\'{dashboard_url}\'; return false;">🎮 Volver a tu Dashboard</a></div>',
            unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"❌ Error al cargar o guardar los datos: {e}")
