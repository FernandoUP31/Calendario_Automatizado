import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Definimos los permisos (scopes) que necesita la aplicación.
# IMPORTANTE: Si modificas estos scopes, debes borrar el archivo 'token.json'.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

# TODO: Reemplaza con el ID de tu Google Sheet (lo encuentras en la URL de tu hoja de cálculo)
SPREADSHEET_ID = '1-sS10Hzsp7RNus06NAy805qcYPgtdEgKb-GgKjO5YAk'
# TODO: Reemplaza con el nombre de tu hoja y el rango que contiene los datos.
# Asume que los datos están en las columnas A a F. Empezamos en A2 para saltar la cabecera.
RANGE_NAME = 'Hoja 1!A2:F'
# Ajusta a tu zona horaria (ej. 'America/Mexico_City', 'Europe/Madrid', 'America/Bogota')
TIME_ZONE = 'America/Lima'

def get_credentials():
    """
    Maneja la autenticación y autorización del usuario.
    Si es la primera vez, abre el navegador para pedir permisos y genera 'token.json'.
    Si ya existe 'token.json', lo utiliza para futuras ejecuciones.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas disponibles, se solicitan.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Abre el navegador localmente para autenticar
            creds = flow.run_local_server(port=0)
        
        # Guardamos las credenciales para la próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def create_calendar_event(calendar_service, nombre, inicio, fin, descripcion, correo):
    """
    Crea un evento en Google Calendar.
    Formatos de fecha esperados para 'inicio' y 'fin': 'YYYY-MM-DDTHH:MM:SS' (ej. 2026-08-27T09:00:00)
    Retorna el ID del evento creado o None si ocurre un error.
    """
    event = {
        'summary': nombre,
        'description': descripcion,
        'start': {
            'dateTime': inicio, 
            'timeZone': TIME_ZONE,
        },
        'end': {
            'dateTime': fin,
            'timeZone': TIME_ZONE,
        },
        'attendees': [
            {'email': correo},
        ],
        # Configuración explícita de recordatorios
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 30},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    try:
        # Se inserta el evento en el calendario principal del usuario autenticado
        event_result = calendar_service.events().insert(
            calendarId='primary', 
            body=event,
            sendUpdates='all' # Enviar invitación por correo a los asistentes
        ).execute()
        print(f"[Calendar] Evento creado exitosamente: {event_result.get('htmlLink')}")
        return event_result.get('id')
    except HttpError as error:
        print(f"[Calendar] Error al crear evento: {error}")
        return None

def send_confirmation_email(gmail_service, destinatario, nombre_evento, inicio):
    """
    Envía un correo de confirmación de forma independiente usando la API de Gmail.
    """
    try:
        message = EmailMessage()
        message.set_content(
            f"Hola,\n\n"
            f"Tu evento '{nombre_evento}' programado para el {inicio} ha sido agendado exitosamente.\n\n"
            f"Saludos."
        )
        message['To'] = destinatario
        message['From'] = 'me' # 'me' indica la cuenta del usuario autenticado
        message['Subject'] = f"Confirmación de evento agendado: {nombre_evento}"

        # Codificamos el mensaje en base64 para enviarlo mediante la API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_message = gmail_service.users().messages().send(
            userId="me", 
            body=create_message
        ).execute()
        print(f"[Gmail] Correo de confirmación enviado a {destinatario}.")
    except HttpError as error:
        print(f"[Gmail] Error al enviar correo: {error}")

def update_sheet_status(sheets_service, row_index):
    """
    Actualiza la celda de la columna 'Estado' a 'Agendado'.
    Asume que 'Estado' es la columna F (letra F en la hoja).
    """
    # El rango exacto de la celda a actualizar, ej: 'Hoja 1!F2'
    sheet_name = RANGE_NAME.split('!')[0]
    cell_range = f"{sheet_name}!F{row_index}" 
    
    body = {
        'values': [['Agendado']]
    }
    
    try:
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, 
            range=cell_range,
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()
        print(f"[Sheets] Fila {row_index} actualizada a 'Agendado'.")
    except HttpError as error:
        print(f"[Sheets] Error al actualizar la hoja: {error}")

def main():
    # 1. Autenticación y obtención de credenciales
    creds = get_credentials()

    try:
        # 2. Construcción de los servicios para interactuar con las APIs
        sheets_service = build('sheets', 'v4', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
        gmail_service = build('gmail', 'v1', credentials=creds)

        # 3. Leer los datos desde Google Sheets
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No se encontraron datos en el rango especificado.')
            return

        # El índice de fila inicial (asumiendo que RANGE_NAME empieza en la fila 2)
        # Esto es importante para saber en qué fila exacta actualizar el estado
        row_number = int(''.join(filter(str.isdigit, RANGE_NAME.split('!')[1].split(':')[0])))
        
        # 4. Procesamiento de cada fila
        for row in values:
            # Rellenar con strings vacíos si la fila tiene menos de 6 columnas 
            # (ocurre si las celdas del final están vacías)
            while len(row) < 6:
                row.append('')
                
            nombre, inicio, fin, descripcion, correo, estado = row[:6]

            # Solo procesamos si el estado está vacío
            if estado.strip() == '':
                print(f"\n--- Procesando nuevo registro: {nombre} ---")
                
                # Paso A: Crear evento en Google Calendar
                event_id = create_calendar_event(calendar_service, nombre, inicio, fin, descripcion, correo)
                
                if event_id:
                    # Paso B: Enviar correo vía Gmail
                    send_confirmation_email(gmail_service, correo, nombre, inicio)
                    
                    # Paso C: Actualizar el estado en Google Sheets
                    update_sheet_status(sheets_service, row_number)
            else:
                # Opcional: imprimir los registros que se están saltando
                # print(f"Saltando '{nombre}', estado actual: '{estado}'")
                pass
                
            row_number += 1
            
        print("\nProceso finalizado correctamente.")

    except HttpError as err:
        print(f"Ocurrió un error general con la API: {err}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()

