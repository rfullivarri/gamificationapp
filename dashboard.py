import streamlit as st
from PIL import Image
import plotly.express as px
import time
import os
import uuid
import pandas as pd

from utils.sheets_reader import (
    get_gamification_data,
    update_avatar_url,
    parse_percentage,
    subir_a_drive_y_obtener_link
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
        daily_log = data["daily_log"]

# --------------------- LAYOUT A TRES COLUMNAS --------------------------------------------------
        col1, col2, col3 = st.columns([1, 2, 1])

# 🖼 COLUMNA 1 – AVATAR Y ESTADO ---------------------------------------------------------
        with col1:
            def es_url_valida(url):
                return url.startswith("http") and not url.endswith("/")

            if es_url_valida(avatar_url):
                st.image(avatar_url, width=200)
            else:
                st.warning("⚠️ No se encontró avatar válido para este usuario.")
                st.image(avatar_url, width=200)

            cambiar_avatar = st.checkbox("🖼 Cambiar avatar", key="cambiar_avatar")
            avatar_uploader = None
            if cambiar_avatar:
                avatar_uploader = st.file_uploader(
                    label="Subí tu nuevo avatar",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )

            if avatar_uploader:
                file_extension = avatar_uploader.name.split(".")[-1]
                temp_path = f"/tmp/temp_avatar.{file_extension}"

                with open(temp_path, "wb") as f:
                    f.write(avatar_uploader.read())

                nombre_usuario = email.split("@")[0]
                nombre_limpio = "".join(c for c in nombre_usuario if c.isalnum()).lower()
                nombre_archivo = f"{nombre_limpio}_avatar.{file_extension}"

                try:
                    nuevo_link = subir_a_drive_y_obtener_link(temp_path, nombre_archivo)
                    update_avatar_url(email, nuevo_link)
                    st.image(nuevo_link, width=200)
                    st.success("✅ Avatar actualizado. Refrescá la página.")
                except Exception as e:
                    st.error(f"❌ Error al subir la imagen: {e}")

            st.subheader("💠 Estado diario")
            st.progress(parse_percentage(xp_HP), text=f"🫀 HP – {int(parse_percentage(xp_HP) * 100)}%")
            st.progress(parse_percentage(xp_Mood), text=f"🏵️ Mood – {int(parse_percentage(xp_Mood) * 100)}%")
            st.progress(parse_percentage(xp_Focus), text=f"🧠 Focus – {int(parse_percentage(xp_Focus) * 100)}%")

# 📊 COLUMNA 2 – RADAR Y EXP DIARIA ---------------------------------------------------------
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

#---EXP POR DÍA----------------------------------------------------------------------------------------
                st.markdown("### 📈 Daily Cultivation")
        
                df_daily = data["daily_log"].copy()
        
                # Asegurar que la columna Fecha es datetime (saltando errores)
                df_daily["Fecha"] = pd.to_datetime(df_daily["Fecha"], errors="coerce")
                df_daily = df_daily.dropna(subset=["Fecha", "EXP"])
        
                # Obtener mes actual y formatearlo
                today = pd.Timestamp.today()
                current_month = today.strftime("%Y-%m")
        
                # Crear lista de meses únicos
                df_daily["Mes"] = df_daily["Fecha"].dt.strftime("%Y-%m")
                meses_unicos = sorted(df_daily["Mes"].dropna().unique())
        
                # Selector de mes
                mes_seleccionado = st.selectbox("📅 Seleccioná el mes:", meses_unicos, index=meses_unicos.index(current_month) if current_month in meses_unicos else 0)
        
                # Filtrar por mes seleccionado
                df_mes = df_daily[df_daily["Mes"] == mes_seleccionado]
        
                # Agrupar por fecha y sumar EXP
                df_exp_por_dia = df_mes.groupby("Fecha")["EXP"].sum().reset_index()
        
                # Mostrar gráfico
                st.line_chart(df_exp_por_dia.set_index("Fecha"))

# 🏆 COLUMNA 3 – XP Y NIVEL ---------------------------------------------------------
        with col3:
            st.subheader(f"🏆 Total XP: {xp_total}")
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
