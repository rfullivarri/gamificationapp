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

# Abrimos el archivo y la hoja BBDD
sheet = client.open("Gamification N1 (respuestas)").worksheet("BBDD")

# Obtenemos los datos completos y los encabezados
all_data = sheet.get_all_values()
df = pd.DataFrame(all_data[1:], columns=all_data[0])  # A partir de fila 2, con headers en la fila 1
df = df.iloc[:, :5]  # Mostramos solo columnas A hasta E (Pilar, Rasgo, Stat, Task, Dificultad)

# Calculamos una altura dinámica para evitar scroll vertical
editor_height = 40 * len(df) + 80  # 40px por fila estimado + margen
if editor_height < 300:
    editor_height = 300  # Altura mínima

# Editor interactivo y editable
edited_df = st.data_editor(
    df,
    num_rows="dynamic",               # Permite eliminar o agregar filas
    use_container_width=True,
    height=editor_height
)

# Botón de confirmación
if st.button("✅ Confirmar edición"):
    st.success("Datos confirmados. ¡Podés seguir con tu viaje de mejora!")

    # 🔜 PRÓXIMO PASO: aquí se conectará con Google Apps Script para generar el Formulario diario
