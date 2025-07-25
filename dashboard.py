import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os
from utils.sheets_reader import get_gamification_data, save_avatar_to_drive

# Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# Entrada de correo
email = st.text_input("📧 Ingresá tu correo electrónico para acceder a tu base personalizada:")

if email:
    data = get_gamification_data(email)

    if data:
        st.success("✅ Datos cargados correctamente")

        tabla = data["tabla_principal"]
        acumulados_subconjunto = data["acumulados_subconjunto"]
        niveles = data["niveles"]

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🎭 Tu Avatar")

            # Mostrar avatar si ya está cargado
            avatar_path = f"temp_avatars/{email.replace('@', '_at_')}.jpg"
            if os.path.exists(avatar_path):
                st.image(Image.open(avatar_path), use_column_width=True, caption="Tu avatar")
            else:
                st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)

            # Subida de nuevo avatar
            uploaded_file = st.file_uploader("Subí una imagen estilo 'story' (avatar)", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Nuevo avatar", use_column_width=True)

                # Guardar local y en Drive
                os.makedirs("temp_avatars", exist_ok=True)
                image.save(avatar_path)
                save_avatar_to_drive(email, uploaded_file)

        with col2:
            st.subheader("🎯 Nivel actual")
            nivel = niveles.iloc[0, 1] if not niveles.empty else "N/A"
            st.metric(label="Nivel", value=nivel)

            st.subheader("💠 Estado diario")
            st.progress(0.75, text="🫀 HP")
            st.progress(0.60, text="🏵️ Mood")
            st.progress(0.40, text="🧠 Focus")

        # Cálculo de EXP por Rasgo (tabla A:M)
        if "Rasgo" in tabla.columns and "EXP" in tabla.columns:
            exp_por_rasgo = tabla.groupby("Rasgo")["EXP"].sum().reset_index()
            fig = px.line_polar(
                exp_por_rasgo,
                r="EXP",
                theta="Rasgo",
                line_close=True,
                title="🎯 EXP acumulada por Rasgo",
                height=500
            )
            fig.update_traces(fill="toself")
            st.plotly_chart(fig, use_container_width=True)

        # Mostrar acumulados
        st.subheader("📋 Resumen de Progreso")
        st.dataframe(acumulados_subconjunto, use_container_width=True)

    else:
        st.error("No se encontraron datos para ese correo.")
