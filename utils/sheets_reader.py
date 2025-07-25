import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def get_gamification_data(email):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    base = client.open("FORMULARIO INTRO  SELF IMPROVEMENT JOURNEY (respuestas)")
    registros = base.worksheet("Registros de Usuarios").get_all_records()

    fila = next((r for r in registros if r["Email"] == email), None)
    if not fila:
        return None, None, None

    spreadsheet_id = fila["GoogleSheetID"]
    gs = client.open_by_key(spreadsheet_id)

    bbdd = pd.DataFrame(gs.worksheet("BBDD").get_all_records())
    daily_log = pd.DataFrame(gs.worksheet("Daily Log").get_all_records())
    setup = pd.DataFrame(gs.worksheet("Setup").get_all_records())

    return bbdd, daily_log, setup
