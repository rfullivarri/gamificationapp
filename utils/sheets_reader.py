import gspread
import pandas as pd
import re
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_gamification_data(email):
    # 1. Autenticación con Google Sheets usando las credenciales desde secrets.toml
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)

    # 2. Abrimos el archivo central de registros
    base = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    registros = base.worksheet("Registros de Usuarios").get_all_records()

    # 3. Buscamos la fila correspondiente al email ingresado
    fila = next((r for r in registros if r["Email"] == email), None)
    if not fila:
        st.error("❌ No se encontró una base de datos vinculada a ese correo.")
        return None, None, None

    # 4. Extraemos el ID puro desde la URL completa del Google Sheet
    spreadsheet_url = fila["GoogleSheetID"]
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
    if not match:
        st.error("❌ No se pudo extraer el ID del Google Sheet desde la URL.")
        return None, None, None

    spreadsheet_id = match.group(1)

    # 5. Abrimos el archivo del usuario por su ID
    gs = client.open_by_key(spreadsheet_id)

    # 6. Leemos las hojas necesarias
    try:
        bbdd = pd.DataFrame(gs.worksheet("BBDD").get_all_records())
        daily_log = pd.DataFrame(gs.worksheet("Daily Log").get_all_records())
        setup = pd.DataFrame(gs.worksheet("Setup").get_all_records())
    except Exception as e:
        st.error(f"❌ No se pudieron leer las hojas del archivo del usuario: {e}")
        return None, None, None

    return bbdd, daily_log, setup
