import streamlit as st
from utils.sheets_reader import get_gamification_data
from PIL import Image

st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# Ingreso de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    bbdd, daily_log, setup = get_gamification_data(email)

    if bbdd is not None:
        st.success("✅ Base cargada correctamente")

        # Sección de imagen
        st.subheader("🎭 Avatar de Jugador")
        uploaded_file = st.file_uploader("Subí tu avatar estilo 'story'", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Tu avatar", use_column_width=True)
        else:
            st.image("https://i.imgur.com/z7nGzGx.png", caption="Avatar por defecto", use_column_width=True)

        # Nivel actual desde Setup
        st.subheader("🎯 Nivel actual")
        nivel = setup["Nivel"][0] if "Nivel" in setup.columns else 0
        st.metric(label="Nivel", value=nivel)

        # Barras HP, Mood, Focus
        st.subheader("💠 Estado diario")
        st.progress(0.75, text="🫀 HP")
        st.progress(0.60, text="🏵️ Mood")
        st.progress(0.40, text="🧠 Focus")

    else:
        st.error("No se encontró base para ese correo.")
