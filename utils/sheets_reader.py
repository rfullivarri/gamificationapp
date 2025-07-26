import gspread
import pandas as pd
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st

def parse_percentage(val):
    if val is None:
        return 0.0
    if isinstance(val, str):
        val = val.strip().replace('%', '').replace(',', '.')
        try:
            val = float(val)
        except:
            return 0.0
    return max(0.0, min(val if val <= 1 else val / 100, 1.0))

def to_df(raw_data):
    return pd.DataFrame(raw_data[1:], columns=raw_data[0])

def get_gamification_data(email):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    base = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    registros = base.worksheet("Registros de Usuarios").get_all_records()

    fila = next((r for r in registros if r["Email"].strip().lower() == email.strip().lower()), None)
    if not fila:
        return None

    avatar_url = fila.get("Avatar URL", "").strip()
    if not avatar_url:
        avatar_url = "https://i.imgur.com/z7nGzGx.png"

    spreadsheet_url = fila["GoogleSheetID"]
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
    spreadsheet_id = match.group(1) if match else spreadsheet_url
    gs = client.open_by_key(spreadsheet_id)

    ws_bbdd = gs.worksheet("BBDD")
    tabla_principal = to_df(ws_bbdd.get("A1:M"))
    acumulados_subconjunto = to_df(ws_bbdd.get("W1:AE"))

    ws_daily = gs.worksheet("Daily Log")
    daily_log = to_df(ws_daily.get("A1:E"))

    ws_setup = gs.worksheet("Setup")
    niveles = to_df(ws_setup.get("A1:B"))
    game_mode = to_df(ws_setup.get("G1:G"))
    
    # ✅ Lectura robusta del bloque E6:E11
    setup_raw = ws_setup.get_values("E6:E11")
    if len(setup_raw) < 6:
        raise ValueError("Faltan datos en el rango E6:E11 del Setup")

    xp_total = setup_raw[0][0]
    nivel_actual = setup_raw[1][0]
    xp_faltante = setup_raw[2][0]
    xp_HP = setup_raw[3][0]
    xp_Mood = setup_raw[4][0]
    xp_Focus = setup_raw[5][0]

    ws_rewards = gs.worksheet("Recompensas")
    rewards = to_df(ws_rewards.get("A1:H"))

    return {
        "tabla_principal": tabla_principal,
        "acumulados_subconjunto": acumulados_subconjunto,
        "daily_log": daily_log,
        "niveles": niveles,
        "game_mode": game_mode,
        "reward_setup": to_df(ws_setup.get("I1:O")),
        "rewards": rewards,
        "xp_total": xp_total,
        "nivel_actual": nivel_actual,
        "xp_faltante": xp_faltante,
        "avatar_url": avatar_url,
        "xp_HP": xp_HP,
        "xp_Mood": xp_Mood,
        "xp_Focus": xp_Focus,
    }
