import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gamification Dashboard", layout="wide")
st.title("🎮 Gamification Dashboard")
st.write("Este es un prototipo conectado con tu Google Sheet de Respuestas.")

# 🔐 Autenticación
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# 📄 Conectarse a la hoja correcta
spreadsheet = client.open("Gamification N1 (respuestas)")  # Nombre exacto del archivo
worksheet = spreadsheet.worksheet("BBDD")  # Nombre exacto de la pestaña

# 📊 Leer el rango exacto de la tabla principal (evitando conflictos)
rango = "A1:M100"  # Asegurate que este rango contenga toda la tabla sin irse a otras tablas abajo
records = worksheet.get(rango)
data = pd.DataFrame(records[1:], columns=records[0])  # Filas desde la 2da, columnas desde headers

# Mostrar el contenido
st.subheader("📋 Vista de tu Base de Datos")
st.dataframe(data)
