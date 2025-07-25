import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from utils.sheets_reader import get_gamification_data

st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    bbdd, daily_log, setup, acumulados_subconjunto, *_ = get_gamification_data(email)

    if bbdd is not None:
        st.success("✅ Base cargada correctamente")

        # ───── 🎭 Avatar del Jugador ─────
        st.subheader("🎭 Avatar de Jugador")
        uploaded_file = st.file_uploader("Subí tu avatar estilo 'story'", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Tu avatar", use_column_width=True)
        else:
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)

        # ───── 🎯 Nivel actual ─────
        st.subheader("🎯 Nivel actual")
        nivel = setup["Nivel"][0] if "Nivel" in setup.columns else 0
        st.metric(label="Nivel", value=nivel)

        # ───── 💠 Estado Diario ─────
        st.subheader("💠 Estado diario")
        col1, col2, col3 = st.columns(3)
        col1.progress(0.75, text="🫀 HP")
        col2.progress(0.60, text="🏵️ Mood")
        col3.progress(0.40, text="🧠 Focus")

        # ───── 📊 Radar Chart de Stats ─────
        st.subheader("📈 Radar de Stats (EXP acumulada)")
        radar_data = acumulados_subconjunto.groupby("Stats", as_index=False)["𝑡𝑜𝑡𝑎𝑙 𝐸𝑥"].sum()
        if len(radar_data) >= 3:
            fig = px.line_polar(radar_data, r="𝑡𝑜𝑡𝑎𝑙 𝐸𝑥", theta="Stats", line_close=True,
                                title="EXP por Stat", markers=True)
            fig.update_traces(fill="toself")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔍 Aún no hay suficientes registros para mostrar el radar chart.")

        # ───── 📋 Tabla de acumulados ─────
        st.subheader("📋 Acumulados por Subconjunto")
        st.caption("Resumen por Pilar, Rasgo y Stat.")
        st.dataframe(acumulados_subconjunto, use_container_width=True, hide_index=True)

    else:
        st.error("❌ No se encontró base para ese correo.")
