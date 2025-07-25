import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data
import time

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# 📩 Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    data = get_gamification_data(email)

    if data:
        # ✅ Mensaje de éxito temporal
        success_message = st.empty()
        success_message.success("✅ Tenemos tus stats!")
        time.sleep(2)
        success_message.empty()

        # 🧠 Leer datos del diccionario
        xp_total = data["xp_total"]
        nivel_actual = data["nivel_actual"]
        xp_faltante = data["xp_faltante"]

        # ------------------- LAYOUT A TRES COLUMNAS -------------------
        col1, col2, col3 = st.columns([1.1, 1.8, 1.1])

        # 📊 Radar de Rasgos
        with col1:
             # 🎯 Nivel
            st.subheader("🎯 Nivel actual")
            st.metric(label="Nivel", value=nivel_actual)
            st.markdown(f"✨ Te faltan **{xp_faltante} XP** para tu próximo nivel.")
            
            # 🎯 Avatar
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)
            
            # 💠 Estado diario
            st.subheader("💠 Estado diario")
            st.progress(0.75, text="🫀 HP")
            st.progress(0.60, text="🏵️ Mood")
            st.progress(0.40, text="🧠 Focus")

        
        with col2:
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

        
        with col3:
             st.subheader(f"🏆**Total EXP:** {xp_total}")            

        # 📋 Tabla resumen
        st.markdown("---")
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")

