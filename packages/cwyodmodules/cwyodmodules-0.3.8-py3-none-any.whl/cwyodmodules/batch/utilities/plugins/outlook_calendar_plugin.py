import requests
import datetime
from semantic_kernel.functions import kernel_function

class OutlookCalendarPlugin:
    def __init__(self, request_headers: dict):
        self.request_headers = request_headers

    def _get_access_token(self) -> str:
        auth_header = self.request_headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Missing or invalid Authorization header")
        return auth_header.split(" ")[1]

    @kernel_function(name="get_calendar_events", description="Get upcoming Outlook calendar events")
    def get_calendar_events(self, days: int = 1) -> str:
        try:
            token = self._get_access_token()
        except Exception as e:
            return f"Authentication error: {str(e)}"
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.datetime.utcnow().isoformat() + "Z"
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
        url = f"https://graph.microsoft.com/v1.0/me/calendarview?startDateTime={now}&endDateTime={end}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return f"Failed to fetch events: {resp.text}"
        events = resp.json().get("value", [])
        if not events:
            return "No events found."
        return "\n".join([f"{e.get('subject', 'No subject')} at {e.get('start', {}).get('dateTime', 'Unknown time')}" for e in events])

    @kernel_function(name="schedule_appointment", description="Schedule a new Outlook calendar appointment")
    def schedule_appointment(self, subject: str, start_time: str, end_time: str) -> str:
        try:
            token = self._get_access_token()
        except Exception as e:
            return f"Authentication error: {str(e)}"
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