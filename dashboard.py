import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data, update_avatar_url
import time
import os
import uuid

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# 📩 Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")


# Subida de imagen personalizada
st.markdown("### 📸 Subí tu Avatar personalizado (opcional)")

avatar_file = st.file_uploader("Subí tu imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])
if avatar_file:
    # Guardar temporalmente en un subfolder en Streamlit Cloud
    file_extension = avatar_file.name.split(".")[-1]
    avatar_path = f"temp_avatar_{uuid.uuid4()}.{file_extension}"
    with open(avatar_path, "wb") as f:
        f.write(avatar_file.read())

    # Subir a algún hosting (opcional, si usás algo como Cloudinary, Imgur API, etc.)
    # Por ahora, mostramos localmente (en modo local servirá)
    st.image(avatar_path, caption="Tu nuevo avatar")

    # 🚀 ACTUALIZAR URL en GSheet
    # Si estás trabajando en local, asumimos que vas a hostear las imágenes manualmente
    # Alternativa mínima: usar Imgur o Drive compartido con link público
    # Por ahora: mostramos el path temporal
    public_url = f"https://example.com/{avatar_path}"  # Cambiar si tenés hosting
    update_avatar_url(email, public_url)
    st.success("✅ Avatar actualizado en la base")


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
        avatar_url = data.get("avatar_url") or "https://i.imgur.com/z7nGzGx.png"

        # ------------------- LAYOUT A TRES COLUMNAS -------------------
        col1, col2, col3 = st.columns([1, 2, 1])

        # 📊 Info lateral izquierda
        with col1:
            st.subheader("🎯 Nivel actual")
            st.markdown(f"""
                <div style='text-align: center; font-size: 60px; font-weight: bold; color: #4B4B4B;'>
                    {nivel_actual}
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"✨ Te faltan **{xp_faltante} XP** para tu próximo nivel.")

            # 🎯 Avatar
            st.image(avatar_url, caption="Tu avatar", use_column_width=True)

            uploaded_file = st.file_uploader("📷 Subí tu nuevo avatar", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                filename = f"{uuid.uuid4()}.png"
                filepath = os.path.join("/tmp", filename)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                # Subí a tu hosting o Drive público y obtené URL
                uploaded_url = f"https://drive.google.com/uc?id=TUSUBIDAFAKE/{filename}"  # Reemplazá por tu lógica real
                update_avatar_url(email, uploaded_url)
                st.success("✅ Avatar actualizado. Recargá para verlo reflejado.")

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
