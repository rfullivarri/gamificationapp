import gspread
import pandas as pd
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
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
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
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
    daily_log = to_df(ws_daily.get("A1:D"))

    ws_setup = gs.worksheet("Setup")
    niveles = to_df(ws_setup.get("A1:B"))
    game_mode = to_df(ws_setup.get("G1:G"))
    reward_setup = to_df(ws_setup.get("I1:O"))
    setup_raw = ws_setup.get("E6:E11")
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
        "reward_setup": reward_setup,
        "rewards": rewards,
        "xp_total": xp_total,
        "nivel_actual": nivel_actual,
        "xp_faltante": xp_faltante,
        "avatar_url": avatar_url,
        "xp_HP": xp_HP,
        "xp_Mood": xp_Mood,
        "xp_Focus": xp_Focus,
    }

def normalizar_link_drive(link):
    if not link:
        return ""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"
    elif "uc?id=" in link:
        return link
    else:
        return link

def update_avatar_url(email, url):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
    client = gspread.authorize(creds)

    sheet = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    tab = sheet.worksheet("Registros de Usuarios")

    data = tab.get_all_values()
    for idx, row in enumerate(data):
        if row and row[0].strip().lower() == email.strip().lower():
            tab.update_cell(idx + 1, 9, normalizar_link_drive(url))
            break


def upload_avatar_and_save_url(uploaded_file, email):
    if uploaded_file:
        # Guardar el archivo temporalmente
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Subir a Google Drive
        drive_service = build("drive", "v3", credentials=creds)
        folder_ID = "1y9UeK80kPNJF1ejpB_L450D8-Zk84s2d"
        file_metadata = {
            "name": uploaded_file.name,
            "parents": [folder_ID]  # ID de tu carpeta de Drive (tipo "Gamification Life")
        }
        media = MediaFileUpload(uploaded_file.name, resumable=True)
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = uploaded.get("id")

        # Generar link compartible
        drive_service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()
        url = f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk"

        # Guardar en el Sheet
        update_avatar_url_in_sheet(email, url)

        return url
