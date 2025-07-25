import streamlit as st
import plotly.express as px
from PIL import Image
from utils.sheets_reader import get_gamification_data
import os

st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Dashboard de Autosuperación")

email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    data = get_gamification_data(email)

    if data:
        st.success("✅ Base cargada correctamente")

        tabla_principal = data["tabla_principal"]
        acumulados_subconjunto = data["acumulados_subconjunto"]
        daily_log = data["daily_log"]
        niveles = data["niveles"]
        game_mode = data["game_mode"]
        reward_setup = data["reward_setup"]
        rewards = data["rewards"]

        # -----------------------------------------
        # SECCIÓN 1 — AVATAR
        # -----------------------------------------
        st.subheader("🎭 Avatar")
        avatar_folder = "avatars"
        avatar_path = f"{avatar_folder}/{email.replace('@', '_')}.png"
        os.makedirs(avatar_folder, exist_ok=True)

        uploaded_file = st.file_uploader("Subí tu avatar estilo 'story'", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            with open(avatar_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.image(uploaded_file, caption="Tu avatar", use_column_width=True)
        elif os.path.exists(avatar_path):
            st.image(Image.open(avatar_path), caption="Tu avatar", use_column_width=True)
        else:
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)

        st.markdown("---")

        # -----------------------------------------
        # SECCIÓN 2 — ESTADO DIARIO
        # -----------------------------------------
        st.subheader("💠 Estado diario")
        st.progress(0.75, text="🫀 HP")    # Reemplazar luego con cálculo real
        st.progress(0.60, text="🏵️ Mood")
        st.progress(0.40, text="🧠 Focus")

        st.markdown("---")

        # -----------------------------------------
        # SECCIÓN 3 — RADAR DE RASGOS
        # -----------------------------------------
        st.subheader("📊 Radar de Rasgos")

        radar_data = tabla_principal.groupby("Rasgo").agg({"EXP": "sum"}).reset_index()
        fig = px.line_polar(
            radar_data,
            r="EXP",
            theta="Rasgo",
            line_close=True,
            title="Distribución de EXP por Rasgo"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # -----------------------------------------
        # SECCIÓN 4 — ACUMULADOS POR SUBCONJUNTO
        # -----------------------------------------
        st.subheader("📘 Stats por subconjunto")
        st.dataframe(acumulados_subconjunto, use_container_width=True)

        st.markdown("---")

        # -----------------------------------------
        # SECCIÓN 5 — REWARDS Y SETUP
        # -----------------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Setup de Juego")
            st.dataframe(game_mode, use_container_width=True)
            st.dataframe(niveles, use_container_width=True)

        with col2:
            st.subheader("🎁 Setup de Recompensas")
            st.dataframe(reward_setup, use_container_width=True)

        st.markdown("---")

        # -----------------------------------------
        # SECCIÓN 6 — HISTÓRICO DE RECOMPENSAS
        # -----------------------------------------
        st.subheader("🏆 Recompensas Obtenidas")
        st.dataframe(rewards, use_container_width=True)

    else:
        st.error("No se encontró base para ese correo.")
