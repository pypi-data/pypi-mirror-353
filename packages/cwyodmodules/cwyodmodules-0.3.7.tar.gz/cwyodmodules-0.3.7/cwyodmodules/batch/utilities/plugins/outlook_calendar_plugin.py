from semantic_kernel.functions import kernel_function
from msal import ConfidentialClientApplication
import requests
import datetime
from semantic_kernel.functions import kernel_function
from flask import jsonify

class OutlookCalendarPlugin:
    def __init__(self, request_headers):
        self.request_headers = request_headers
    # def _get_access_token(self):
    #     app = ConfidentialClientApplication(
    #         self.client_id,
    #         authority=f"https://login.microsoftonline.com/{self.tenant_id}",
    #         client_credential=self.client_secret,
    #     )
    #     scopes = ["https://graph.microsoft.com/.default"]
    #     result = app.acquire_token_for_client(scopes=scopes)
    #     return result["access_token"]
    
    def _get_access_token(self):
        auth_header = self.request_headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        access_token = auth_header.split(" ")[1]
        return access_token

    @kernel_function(name="get_calendar_events", description="Get upcoming Outlook calendar events")
    def get_calendar_events(self, days: int = 1) -> str:
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.datetime.utcnow().isoformat() + "Z"
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
        url = f"https://graph.microsoft.com/v1.0/me/calendarview?startDateTime={now}&endDateTime={end}"
        resp = requests.get(url, headers=headers)
        events = resp.json().get("value", [])
        if not events:
            return "No events found."
        return "\n".join([f"{e['subject']} at {e['start']['dateTime']}" for e in events])

    @kernel_function(name="schedule_appointment", description="Schedule a new Outlook calendar appointment")
    def schedule_appointment(self, subject: str, start_time: str, end_time: str) -> str:
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = "https://graph.microsoft.com/v1.0/me/events"
        event = {
            "subject": subject,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
        }
        resp = requests.post(url, headers=headers, json=event)
        if resp.status_code == 201:
            return "Appointment scheduled successfully."
        else:
            return f"Failed to schedule appointment: {resp.text}"