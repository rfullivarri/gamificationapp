import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data
import time

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 Self-Improvement Dashboard</h1>", unsafe_allow_html=True)

# 📩 Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    data = get_gamification_data(email)

    if data:
        # ✅ Mensaje de éxito que desaparece
        success_message = st.empty()
        success_message.success("✅ Tenemos tus stats!")
        time.sleep(2)
        success_message.empty()

        # 🧠 Leer datos de la pestaña Setup (celda fija)
        setup = data["setup"]
        xp_total = setup.at[5, "E"]     # E6
        nivel_actual = setup.at[7, "E"] # E8
        xp_faltante = setup.at[8, "E"]  # E9

        # ------------------- LAYOUT A TRES COLUMNAS -------------------
        col1, col2, col3 = st.columns([1.3, 1.2, 1.5])

        # 📊 Radar a la izquierda
        with col1:
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

        # 🎯 Avatar y Nivel en el medio
        with col2:
            st.subheader("🎯 Nivel actual")
            st.metric(label="Nivel", value=nivel_actual)

            st.subheader("🎭 Tu avatar")
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_container_width=True)

            st.markdown(f"**Total EXP:** {xp_total}")
            st.markdown(f"**XP para siguiente nivel:** {xp_faltante}")

        # 💠 Estado diario a la derecha
        with col3:
            st.subheader("💠 Estado diario")
            st.progress(0.75, text="🫀 HP")
            st.progress(0.60, text="🏵️ Mood")
            st.progress(0.40, text="🧠 Focus")

        # 📋 Tabla abajo
        st.markdown("---")
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")
