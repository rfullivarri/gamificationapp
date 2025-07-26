import streamlit as st
from PIL import Image
import plotly.express as px
from utils.sheets_reader import get_gamification_data, update_avatar_url, parse_percentage, subir_a_drive_y_obtener_link
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
        xp_HP = data["xp_HP"]
        xp_Mood = data["xp_Mood"]
        xp_Focus = data["xp_Focus"]
        

# --------------------- LAYOUT A TRES COLUMNAS -----------------------------------------------------------------------------------------
    
        col1, col2, col3 = st.columns([1, 2, 1])

# COLUMNA 1 --------------------------------------------------------------------------------------------------------------------------
        with col1:
                # Mostrar avatar actual
                st.image(avatar_url, width=200)
    
                # Opción para cambiar imagen (estética minimal)
                cambiar_avatar = st.checkbox("🖼 Cambiar avatar", key="cambiar_avatar")
    
                if cambiar_avatar:
                    avatar_uploader = st.file_uploader(
                        label="Subí tu nuevo avatar",
                        type=["jpg", "jpeg", "png"],
                        label_visibility="collapsed"
                    )
    
                    if avatar_uploader:
                        # Guardar temporal
                        file_extension = avatar_uploader.name.split(".")[-1]
                        temp_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
    
                        with open(temp_path, "wb") as f:
                            f.write(avatar_uploader.read())
    
                        # Subir a Drive y obtener URL
                        from utils.sheets_reader import subir_a_drive_y_obtener_link
                        nuevo_link = subir_a_drive_y_obtener_link(temp_path, f"{email}_avatar.{file_extension}")
    
                        # Mostrar imagen nueva
                        st.image(nuevo_link, width=200)
    
                        # Actualizar en base
                        update_avatar_url(email, nuevo_link)
    
                        # Aviso y recarga
                        st.success("✅ Avatar actualizado. Refrescá la página.")

# 💠 Estado diario---------------------------------------------------------------------
                st.subheader("💠 Estado diario")
                #st.progress(0.75, text="🫀 HP")
                #st.progress(0.60, text="🏵️ Mood")
                #st.progress(0.40, text="🧠 Focus")
    
                st.progress(parse_percentage(xp_HP), text=f"🫀 HP – {int(parse_percentage(xp_HP) * 100)}%")
                st.progress(parse_percentage(xp_Mood), text=f"🏵️ Mood – {int(parse_percentage(xp_Mood) * 100)}%")
                st.progress(parse_percentage(xp_Focus), text=f"🧠 Focus – {int(parse_percentage(xp_Focus) * 100)}%")

#COLUMNA 2--------------------------------------------------------------------------------------------------------------
        with col2:
            st.subheader("📊 Radar de Rasgos")
        
            df_radar = data["acumulados_subconjunto"][["Rasgos", "TEXPR"]].copy()
            df_radar = df_radar.dropna(subset=["Rasgos", "TEXPR"])
            df_radar["TEXPR"] = pd.to_numeric(df_radar["TEXPR"], errors="coerce")
            df_radar = df_radar.dropna()
        
            if not df_radar.empty:
                df_radar = pd.concat([df_radar, df_radar.iloc[[0]]], ignore_index=True)
        
                # Cálculo del nuevo límite superior del radar
                max_val = df_radar["TEXPR"].max()
                limite_superior = round(max_val * 1.3)
        
                fig = px.line_polar(
                    df_radar,
                    r="TEXPR",
                    theta="Rasgos",
                    line_close=True,
                    template="seaborn"
                )
        
                fig.update_traces(fill='toself', line_color='royalblue')
        
                # Agregar puntos con los valores
                fig.add_trace(
                    px.scatter_polar(df_radar, r="TEXPR", theta="Rasgos", text=df_radar["TEXPR"].astype(str)).data[0]
                )
        
                fig.update_traces(
                    selector=dict(mode='markers+text'),
                    marker=dict(size=8, color='lightblue'),
                    textposition="top center",
                    textfont_size=12
                )
        
                fig.update_layout(
                    polar=dict(
                        bgcolor="#f0f0f0",
                        radialaxis=dict(
                            visible=True,
                            range=[0, limite_superior],
                            showline=False,
                            showticklabels=True,
                            gridcolor="gray",
                            dtick=40,
                            gridwidth=0.5
                        ),
                        angularaxis=dict(
                            rotation=90,
                            direction="clockwise",
                            gridcolor="gray",
                            gridwidth=0.5
                        )
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
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
