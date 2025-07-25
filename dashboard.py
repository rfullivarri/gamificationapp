import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 Self-Improvement Dashboard</h1>", unsafe_allow_html=True)

# 📩 Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

# 🔄 Script para desaparecer mensaje verde
st.markdown("""
    <script>
        setTimeout(() => {
            let successMsg = window.parent.document.querySelector('[data-testid="stNotificationContentSuccess"]');
            if (successMsg) successMsg.parentElement.style.display = 'none';
        }, 2000);
    </script>
""", unsafe_allow_html=True)

if email:
    data = get_gamification_data(email)

    if data:
        st.success("✅ Tenemos tus stats!")

        # ------------------- LAYOUT A TRES COLUMNAS -------------------
        col1, col2, col3 = st.columns([1.2, 2, 1])

        with col1:
            # 🎯 Nivel
            st.subheader("🎯 Nivel actual")
            nivel = data["niveles"]["Nivel"][0] if not data["niveles"].empty else "Desconocido"
            st.metric(label="Nivel", value=nivel)

            # 📸 Avatar (uploader oculto)
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Tu avatar", use_column_width=True)

        with col2:
            # 📊 Radar de Rasgos
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
            # 🧪 Experiencia total
            total_exp = data["niveles"]["Total EXP"][0] if not data["niveles"].empty else 0
            st.metric(label="🎮 Total EXP", value=int(total_exp))

            # ❤️ Estado Diario
            st.subheader("💠 Estado diario")
            st.progress(0.75, text="🫀 HP")
            st.progress(0.60, text="🏵️ Mood")
            st.progress(0.40, text="🧠 Focus")

        st.markdown("---")

        # 📋 Resumen
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")

