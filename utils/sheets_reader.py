import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_gamification_data(email):
    # 1. Autenticación con Google Sheets usando las credenciales del secrets.toml
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)

    # 2. Abrimos el archivo central
    base = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    registros = base.worksheet("Registros de Usuarios").get_all_records()

    # 3. Buscamos la fila correspondiente al email
    fila = next((r for r in registros if r["Email"] == email), None)
    if not fila:
        return None, None, None

    # 4. Obtenemos el ID del archivo de ese usuario
    spreadsheet_id = fila["GoogleSheetID"]
    gs = client.open_by_key(spreadsheet_id)

    # 5. Leemos las hojas necesarias
    bbdd = pd.DataFrame(gs.worksheet("BBDD").get_all_records())
    daily_log = pd.DataFrame(gs.worksheet("Daily Log").get_all_records())
    setup = pd.DataFrame(gs.worksheet("Setup").get_all_records())

    return bbdd, daily_log, setup
