import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data

# Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    data = get_gamification_data(email)

    if data:
        st.success("✅ Base cargada correctamente")

        # ----------------- AVATAR -----------------
        st.subheader("🎭 Avatar de Jugador")
        uploaded_file = st.file_uploader("Subí tu avatar estilo 'story'", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Tu avatar", use_column_width=True)
        else:
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)

        # ----------------- NIVEL -----------------
        st.subheader("🎯 Nivel actual")
        nivel = data["niveles"]["Nivel"][0] if not data["niveles"].empty else "Desconocido"
        st.metric(label="Nivel", value=nivel)

        # ----------------- PROGRESO -----------------
        st.subheader("💠 Estado diario")
        st.progress(0.75, text="🫀 HP")
        st.progress(0.60, text="🏵️ Mood")
        st.progress(0.40, text="🧠 Focus")

        # ----------------- RADAR CHART -----------------
        st.subheader("📊 Radar de Rasgos")
        df_radar = data["acumulados_subconjunto"][["Rasgos", "CP"]].copy()
        df_radar.columns = ["Rasgo", "Puntaje"]

        if not df_radar.empty:
            fig = px.line_polar(df_radar, r="Puntaje", theta="Rasgo", line_close=True,
                                template="plotly_dark", title="Radar de Rasgos")
            fig.update_traces(fill='toself')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos para el radar chart.")

        # ----------------- TABLA RESUMEN -----------------
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")
