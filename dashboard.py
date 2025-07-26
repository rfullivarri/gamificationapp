import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data, update_avatar_url
import time
import os
import uuid
import pandas as pd

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")


#📩 Input de correo-----------------------------------------------------------------------------------------------------------------

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
        avatar_url = data.get("avatar_url") or "https://i.imgur.com/z7nGzGx.png"
        

# --------------------- LAYOUT A TRES COLUMNAS -----------------------------------------------------------------------------------------
    
        col1, col2, col3 = st.columns([1, 2, 1])

# COLUMNA 1 --------------------------------------------------------------------------------------------------------------------------
        with col1:
            # Si hay imagen previa o subida, mostrarla (sin título, sin caption)
            if avatar_url or "avatar_path" in locals():
                st.image(avatar_url, width=200)

            # Input silencioso para cambiar imagen (solo el botón, sin nada más)
            avatar_file = st.file_uploader(
                label=" ",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )

            # Si se carga una nueva imagen
            if avatar_file:
                file_extension = avatar_file.name.split(".")[-1]
                avatar_path = f"temp_avatar_{uuid.uuid4()}.{file_extension}"
                with open(avatar_path, "wb") as f:
                    f.write(avatar_file.read())

                # Mostrar la nueva imagen arriba, reemplazando la anterior
                st.image(avatar_path, width=200)

                # Actualizar avatar_url para que se mantenga
                avatar_url = f"https://example.com/{avatar_path}"
                update_avatar_url(email, avatar_url)

            # 💠 Estado diario
            st.subheader("💠 Estado diario")
            st.progress(0.75, text="🫀 HP")
            st.progress(0.60, text="🏵️ Mood")
            st.progress(0.40, text="🧠 Focus")

#COLUMNA 2--------------------------------------------------------------------------------------------------------------
        with col2:
            st.subheader("📊 Radar de Rasgos")
        
            # Extraer Rasgos y TEXPR
            df_radar = data["acumulados_subconjunto"][["Rasgos", "TEXPR"]].copy()
            df_radar = df_radar.dropna(subset=["Rasgos", "TEXPR"])
        
            # Convertir TEXPR a numérico
            df_radar["TEXPR"] = pd.to_numeric(df_radar["TEXPR"], errors="coerce")
            df_radar = df_radar.dropna(subset=["TEXPR"])
        
            if not df_radar.empty:
                # Escalado logarítmico suave para balancear visualmente
                df_radar["Valor Escalado"] = df_radar["TEXPR"].apply(lambda x: (x + 1)**0.5)  # raíz cuadrada suaviza extremos
        
                # Normalizar para que se mantenga en rango [0, 1.3]
                max_val = df_radar["Valor Escalado"].max()
                df_radar["Valor Escalado"] = df_radar["Valor Escalado"] / max_val * 1.3 if max_val > 0 else 0
        
                fig = px.line_polar(
                    df_radar,
                    r="Valor Escalado",
                    theta="Rasgos",
                    line_close=True,
                    template="simple_white"
                )
                fig.update_traces(fill='toself')
        
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            range=[0, 1.3],
                            showticklabels=False,
                            ticks='',
                            showline=False
                        )
                    ),
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=False
                )
        
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos para graficar.")
#COLUMNA 3----------------------------------------------------------------------------------------------------------------
        with col3:
            st.subheader(f"🏆**Total XP:** {xp_total}")
            st.subheader("🎯 Nivel actual")
            st.markdown(f"""
                <div style='text-align: center; font-size: 50px; font-weight: bold; color: #4B4B4B;'>
                    {nivel_actual}
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"✨ Te faltan **{xp_faltante} XP** para tu próximo nivel.")

                        

        # 📋 Tabla resumen
        st.markdown("---")
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")
