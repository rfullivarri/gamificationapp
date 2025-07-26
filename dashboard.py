import streamlit as st
from PIL import Image
import plotly.express as px
import time
import os
import uuid
import pandas as pd

from utils.sheets_reader import (
    get_gamification_data,
    parse_percentage,
)

# 🧱 Configuración general
st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🧠 Self-Improvement Dashboard")

# 📩 Input de correo
email = st.text_input("📧 Ingresá tu correo electrónico")

if email:
    data = get_gamification_data(email)

    if data:
        # ✅ Mensaje de carga
        success_message = st.empty()
        success_message.success("✅ Tenemos tus stats!")
        time.sleep(2)
        success_message.empty()

        # 📦 Extraer datos
        xp_total = data["xp_total"]
        nivel_actual = data["nivel_actual"]
        xp_faltante = data["xp_faltante"]
        avatar_url = data.get("avatar_url") or "https://i.imgur.com/z7nGzGx.png"
        xp_HP = data["xp_HP"]
        xp_Mood = data["xp_Mood"]
        xp_Focus = data["xp_Focus"]

        # --------------------- LAYOUT A TRES COLUMNAS ---------------------
        col1, col2, col3 = st.columns([1, 2, 1])

        # 🖼 COLUMNA 1 – AVATAR Y ESTADO -----------------------------------
        with col1:
            st.image(avatar_url, width=200)

          

            # 💠 Estado diario
            st.subheader("💠 Estado diario")
            st.progress(parse_percentage(xp_HP), text=f"🫀 HP – {int(parse_percentage(xp_HP) * 100)}%")
            st.progress(parse_percentage(xp_Mood), text=f"🏵️ Mood – {int(parse_percentage(xp_Mood) * 100)}%")
            st.progress(parse_percentage(xp_Focus), text=f"🧠 Focus – {int(parse_percentage(xp_Focus) * 100)}%")

        # 📊 COLUMNA 2 – RADAR ---------------------------------------------
        with col2:
            st.subheader("📊 Radar de Rasgos")

            df_radar = data["acumulados_subconjunto"][["Rasgos", "TEXPR"]].copy()
            df_radar = df_radar.dropna(subset=["Rasgos", "TEXPR"])
            df_radar["TEXPR"] = pd.to_numeric(df_radar["TEXPR"], errors="coerce")
            df_radar = df_radar.dropna()

            if not df_radar.empty:
                df_radar = pd.concat([df_radar, df_radar.iloc[[0]]], ignore_index=True)
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
                        radialaxis=dict(visible=True, range=[0, limite_superior], showline=False,
                                        showticklabels=True, gridcolor="gray", dtick=40, gridwidth=0.5),
                        angularaxis=dict(rotation=90, direction="clockwise", gridcolor="gray", gridwidth=0.5)
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos para graficar.")

            st.subheader("🪴 Daily Cultivation")
            #df= data["daily_cultivation"]
            #df["Fecha"] = pd.to_datetime(df["Fecha"])
            #df.set_index("Fecha", inplace=True)
            #st.line_chart(df[["XP"]])

            # Usar directamente el DataFrame que ya tenés
            data["daily_cultivation"]["Fecha"] = pd.to_datetime(data["daily_cultivation"]["Fecha"])
            
            fig = px.line(
                data["daily_cultivation"],
                x="Fecha",
                y="XP",
                markers=True,
                text="XP"
            )
            
            fig.update_traces(
                textposition="top center",
                line_shape="spline",  # curva suave
                line=dict(width=2),
                marker=dict(size=6)
            )
            
            fig.update_layout(
                yaxis=dict(range=[0, data["daily_cultivation"]["XP"].max() + 5]),
                plot_bgcolor="#f7f7f7",
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)


        

        # 🏆 COLUMNA 3 – NIVELES Y XP --------------------------------------
        with col3:
            st.subheader(f"🏆**Total XP:** {xp_total}")
            st.subheader("🎯 Nivel actual")
            st.markdown(f"""
                <div style='text-align: center; font-size: 50px; font-weight: bold; color: #4B4B4B;'>
                    {nivel_actual}
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"✨ Te faltan **{xp_faltante} XP** para tu próximo nivel.")

        # 📋 Tabla resumen final
        st.markdown("---")
        st.subheader("📋 Resumen por Subconjunto")
        st.dataframe(data["acumulados_subconjunto"], use_container_width=True)

    else:
        st.error("❌ No se encontró base para ese correo.")
