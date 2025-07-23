import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este es un prototipo conectado con tu Google Sheet.")

# Conexión al Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)

sheet = client.open("Gamification v1 (Plantilla)").worksheet("BBDD")
data = pd.DataFrame(sheet.get_all_records())

st.subheader("📊 Vista general de tu base de datos")
st.dataframe(data)
