import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

creds = None
emails = ["bayronfajardor@gmail.com", "fersungfloo@gmail.com"]
def main():
    creds = None
    
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())


       
    try:
        service = build("calendar", "v3", credentials=creds)
        
        now = dt.datetime.now().isoformat() + "Z"
        #Parametros = {"CalendarId" : str, "conferenceDataVersion" : int, "maxAttendees" : int
        # "sendNotifications" : bool, "supports Attachments" : bool} 
        event = {
            "summary": "Python Event",
            "location": "",
            "description": "Reunion por zoom :https://us04web.zoom.us/j/73680662569?pwd=eRA7gFrgFNsq46ERYoCozjijhWtNGd.1 ",
            "colorId": "6",
            "start": {
                "dateTime": "2025-12-05T09:00:00-05:00",
                "timeZone": "America/Bogota",
            },
            "end": {
                "dateTime": "2025-12-05T17:00:00-05:00",
                "timeZone": "America/Bogota",
            },
            "recurrence": [
                "RRULE:FREQ=DAILY;COUNT=3",
            ],
            "attendees": [
                {"email": emails[0]},
                {"email": emails[1]},
            ],
            "reminders": {"useDefault": True},
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        
        print(f"Evento creado {event.get('htmlLink')}")
        

            
    except HttpError as error:
        print("Ha ocurrido un error maricon", error)
        

if __name__ == "__main__":
    main()
        