import requests
import datetime
from semantic_kernel.functions import kernel_function
from logging import getLogger
from opentelemetry import trace, baggage
from opentelemetry.propagate import extract
from typing import Annotated
from ..tools.text_processing_tool import TextProcessingTool
# logger = getLogger("__main__" + ".base_package")
logger = getLogger("__main__")
# tracer = trace.get_tracer("__main__" + ".base_package")
tracer = trace.get_tracer("__main__")

class OutlookCalendarPlugin:
    def __init__(self, question: str, chat_history: list[dict], request_headers: dict):
        self.question = question
        self.chat_history = chat_history
        self.request_headers = request_headers

    def _get_access_token(self) -> str:
        auth_header = self.request_headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Missing or invalid Authorization header")
        return auth_header.split(" ")[1]

    @kernel_function(name="get_calendar_events", description="Get upcoming Outlook calendar events")
    def get_calendar_events(self, operation: Annotated[str, "The operation to be performed on the calendar events. Like Summarize, Paraphrase, etc. If a language is specified, return that as part of the operation. Preserve the operation name in the user language."], days: int = 1) -> str:
        try:
            token = self._get_access_token()
        except Exception as e:
            return f"Authentication error: {str(e)}"
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.datetime.utcnow().isoformat() + "Z"
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
        url = f"https://graph.microsoft.com/v1.0/me/calendarview?startDateTime={now}&endDateTime={end}"
        resp = requests.get(url, headers=headers)
        logger.info("Calendar get results: %s", resp.text)
        if resp.status_code != 200:
            return f"Failed to fetch events: {resp.text}"
        events = resp.json().get("value", [])
        if not events:
            answer = TextProcessingTool().answer_question(
                question=self.question,
                chat_history=self.chat_history,
                text="No events found.",
                operation=operation,
            )
            return answer
        events_text = "\n".join([f"{e.get('subject', 'No subject')} at {e.get('start', {}).get('dateTime', 'Unknown time')}" for e in events])
        answer = TextProcessingTool().answer_question(
                question=self.question,
                chat_history=self.chat_history,
                text=events_text,
                operation=operation,
            )
        return answer

    @kernel_function(name="schedule_appointment", description="Schedule a new Outlook calendar appointment")
    def schedule_appointment(self, operation: Annotated[str, "The operation to be performed on the calendar events. Like Summarize, Paraphrase, etc. If a language is specified, return that as part of the operation. Preserve the operation name in the user language."], subject: str, start_time: str, end_time: str) -> str:
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
        logger.info("Calendar set results: %s", resp.text)
        if resp.status_code == 201:
            answer = TextProcessingTool().answer_question(
                question=self.question,
                chat_history=self.chat_history,
                text="Appointment scheduled successfully.",
                operation=operation,
            )
            return answer
        else:
            answer = TextProcessingTool().answer_question(
                question=self.question,
                chat_history=self.chat_history,
                text=f"Failed to schedule appointment: {resp.text}",
                operation=operation,
            )
            return answer