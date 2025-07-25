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
            avatar_path = f"temp_avatars/{email.replace('@', 'at')}.jpg"
            if os.path.exists(avatar_path):
                st.image(Image.open(avatar_path), use_column_width
