import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, time

import streamlit as st
from streamlit_calendar import calendar

from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuración de la página
st.set_page_config(page_title="Gestor de Eventos", page_icon="📅", layout="wide")

# Scopes requeridos: SOLO Sheets (La API de Gmail se removió en favor de SMTP)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets'
]

# TODO: Reemplaza con tu Spreadsheet ID real
SPREADSHEET_ID = '1-sS10Hzsp7RNus06NAy805qcYPgtdEgKb-GgKjO5YAk' 
RANGE_NAME = 'Hoja 1!A2:E' 

@st.cache_resource
def get_google_services():
    """
    Inicializa la conexión SOLO a la API de Google Sheets usando la Service Account.
    """
    creds_info = st.secrets["gcp_service_account"]
    
    creds = ServiceAccountCredentials.from_service_account_info(
        creds_info, 
        scopes=SCOPES
    )
            
    sheets_service = build('sheets', 'v4', credentials=creds)
    return sheets_service

@st.cache_data(ttl=60)
def fetch_events_from_sheets():
    try:
        sheets_service = get_google_services()
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        calendar_events = []
        for i, row in enumerate(values):
            if len(row) >= 3:
                nombre = row[0]
                inicio = row[1]
                fin = row[2]
                
                if nombre.strip():
                    calendar_events.append({
                        "id": f"event_{i}",
                        "title": nombre,
                        "start": inicio,
                        "end": fin,
                    })
        return calendar_events
    except Exception as e:
        st.error(f"Error al leer de Sheets: {e}")
        return []

def add_event_to_sheets(nombre, inicio, fin, correo):
    try:
        sheets_service = get_google_services()
        sheet_name = RANGE_NAME.split('!')[0]
        
        body = {
            'values': [[nombre, inicio, fin, "Registrado vía Web", correo]]
        }
        
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, 
            range=f"{sheet_name}!A:E",
            valueInputOption='USER_ENTERED', 
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return True
    except HttpError as error:
        st.error(f"Error al escribir en Sheets: {error}")
        return False

def send_confirmation_email(destinatario, nombre_evento, inicio):
    """
    Envía un correo usando el protocolo SMTP.
    Ideal para cuentas personales de Gmail sin depender de la API ni Service Accounts.
    """
    try:
        # Obtenemos las credenciales del correo desde st.secrets
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["app_password"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = f"Nuevo Evento Agendado: {nombre_evento}"
        
        body = (f"Hola,\n\n"
                f"Tu evento '{nombre_evento}' programado para el {inicio} ha sido registrado exitosamente.\n\n"
                f"Saludos.")
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Conexión al servidor seguro de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Envío y cierre
        server.sendmail(sender_email, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar correo (SMTP): {e}")
        return False


# --- INTERFAZ DE STREAMLIT ---

st.title("📅 Calendario Interactivo con Sheets")

with st.sidebar:
    st.header("➕ Agendar Nuevo Evento")
    
    with st.form("new_event_form"):
        nombre_evento = st.text_input("Nombre del Evento")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha Inicio")
            hora_inicio = st.time_input("Hora Inicio", value=time(9, 0))
        with col2:
            fecha_fin = st.date_input("Fecha Fin")
            hora_fin = st.time_input("Hora Fin", value=time(10, 0))
            
        correo = st.text_input("Correo de Notificación")
        
        submitted = st.form_submit_button("Guardar Evento")
        
        if submitted:
            if not nombre_evento or not correo:
                st.warning("Por favor, llena el nombre del evento y el correo.")
            else:
                inicio_str = datetime.combine(fecha_inicio, hora_inicio).isoformat()
                fin_str = datetime.combine(fecha_fin, hora_fin).isoformat()
                
                with st.spinner("Guardando y enviando notificación..."):
                    success = add_event_to_sheets(nombre_evento, inicio_str, fin_str, correo)
                    if success:
                        send_confirmation_email(correo, nombre_evento, inicio_str)
                        st.success("¡Evento creado con éxito!")
                        
                        fetch_events_from_sheets.clear()
                        st.rerun()

events = fetch_events_from_sheets()

calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
}

st.markdown("---")
st.subheader("Vista de Eventos")

calendar(events=events, options=calendar_options)
