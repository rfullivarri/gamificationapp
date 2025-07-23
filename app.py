import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gamification Dashboard", layout="wide")

st.title("🎮 Gamification Dashboard")
st.write("Este es un prototipo editable conectado a tu Google Sheet.")

# Conexión al Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_service_account"], scope)
client = gspread.authorize(credentials)

# Abrimos el archivo específico y la hoja BBDD
sheet = client.open("Gamification N1 (respuestas)").worksheet("BBDD")

# Obtenemos todas las filas y tomamos solo hasta la columna E
all_data = sheet.get_all_values()
df = pd.DataFrame(all_data[1:], columns=all_data[0])  # Encabezados en la primera fila
df = df.iloc[:, :5]  # Solo columnas A hasta E

# Interfaz editable
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Botón de confirmación
if st.button("✅ Confirmar edición"):
    st.success("Datos confirmados. ¡Podés seguir con tu viaje de mejora!")

    # 🔜 PRÓXIMO PASO: enviar señal a Google Sheets para ejecutar el script
