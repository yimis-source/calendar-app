import requests
import os.path
import datetime as dt
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ZOOM_ACCOUNT_ID = "7-IYqCpyQYqdpXyA_ej9Nw"
ZOOM_CLIENT_ID = "yI4aZ0q3R8GTWgXgpa4MsA"
ZOOM_CLIENT_SECRET = "3Vgs4jUiTqkJ3ha3O7KGmTWXM7inLLAX"
ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_MEETINGS_URL = "https://api.zoom.us/v2/users/me/meetings"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_TOKEN_FILE = "token.json"
GOOGLE_CREDENTIALS_FILE = "credentials.json"
EMAILS = ["fersungfloo@gmail.com", "bayronfajardor@gmail.com"]
TIMEZONE = "America/Bogota"

class ZoomManager:
    """Gestiona la creacion de reuniones en Zoom"""
    
    def __init__(self):
        """Inicializa el gestor con las credenciales de Zoom"""
        self.account_id = ZOOM_ACCOUNT_ID
        self.client_id = ZOOM_CLIENT_ID
        self.client_secret = ZOOM_CLIENT_SECRET
        self.token_url = ZOOM_TOKEN_URL
        self.meetings_url = ZOOM_MEETINGS_URL
        
    def obtener_token(self):
        """Obtiene el token de autenticacion de Zoom"""
        url = f"{self.token_url}?grant_type=account_credentials&account_id={self.account_id}"
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        return response.json()['access_token']
    
    def crear_reunion(self, token, tema, emails_invitados=None, duracion=60, minutos_adelante=5):
        """Crea una reunion en Zoom con los parametros especificados"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        start_time = (datetime.utcnow() + timedelta(minutes=minutos_adelante)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        invitados = []
        if emails_invitados:
            invitados = [{"email": email} for email in emails_invitados]
        
        datos_reunion = {
            "topic": tema,
            "type": 2,
            "start_time": start_time,
            "duration": duracion,
            "timezone": TIMEZONE,
            "password": "123456",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "audio": "both",
                "meeting_invitees": invitados
            }
        }
        
        response = requests.post(self.meetings_url, headers=headers, json=datos_reunion)
        return response.json()

class GoogleCalendarManager:
    """Gestiona la creacion de eventos en Google Calendar"""
    
    def __init__(self):
        """Inicializa el gestor con las credenciales de Google"""
        self.scopes = GOOGLE_SCOPES
        self.token_file = GOOGLE_TOKEN_FILE
        self.credentials_file = GOOGLE_CREDENTIALS_FILE
        self.creds = None
        
    def autenticar(self):
        """Autentica con Google y guarda las credenciales"""
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(self.creds.to_json())
    
    def crear_evento(self, resumen, descripcion, hora_inicio, hora_fin, emails_invitados, ubicacion=""):
        """Crea un evento en Google Calendar con los datos proporcionados"""
        try:
            service = build("calendar", "v3", credentials=self.creds)
            
            asistentes = [{"email": email} for email in emails_invitados]
            
            evento = {
                "summary": resumen,
                "location": ubicacion,
                "description": descripcion,
                "colorId": "6",
                "start": {
                    "dateTime": hora_inicio,
                    "timeZone": TIMEZONE,
                },
                "end": {
                    "dateTime": hora_fin,
                    "timeZone": TIMEZONE,
                },
                "recurrence": [
                    "RRULE:FREQ=DAILY;COUNT=3",
                ],
                "attendees": asistentes,
                "reminders": {"useDefault": True},
            }
            evento = service.events().insert(calendarId="primary", body=evento).execute()
            
            print(f"Evento creado {evento.get('htmlLink')}")
            return evento
            
        except HttpError as error:
            print("Ha ocurrido un error", error)
            return None

def main():
    """Funcion principal que coordina la creacion de reunion en Zoom y evento en Calendar"""
    zoom = ZoomManager()
    token = zoom.obtener_token()
    
    reunion = zoom.crear_reunion(token, "Reunion con Yimis", emails_invitados=EMAILS, duracion=60, minutos_adelante=5)
    
    print(f"\nReunion creada exitosamente")
    print(f"Tema: {reunion['topic']}")
    print(f"ID: {reunion['id']}")
    print(f"Link: {reunion['join_url']}")
    print(f"Password: {reunion.get('password', 'N/A')}")
    print(f"Hora inicio: {reunion['start_time']}")
    print(f"Invitados: {', '.join(EMAILS)}")
    
    calendar = GoogleCalendarManager()
    calendar.autenticar()
    calendar.crear_evento(
        resumen="Python Event",
        descripcion=f"Reunion por zoom: {reunion['join_url']}",
        hora_inicio="2025-12-05T09:00:00-05:00",
        hora_fin="2025-12-05T17:00:00-05:00",
        emails_invitados=EMAILS
    )

if __name__ == "__main__":
    main()