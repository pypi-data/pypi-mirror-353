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
    def __init__(self, question: str, chat_history: list[dict], user_info: dict):
        self.question = question
        self.chat_history = chat_history
        self.user_info = user_info

    def _get_access_token(self) -> str:
        access_token = self.user_info.get("access_token", None)
        return access_token

    @kernel_function(name="get_calendar_events", description="Get upcoming Outlook calendar events")
    def get_calendar_events(self, days: int = 1) -> str:
        with tracer.start_as_current_span("SemanticKernelOrchestrator_orchestrate.get_calendar_events"):
            logger.info("Method get_calendar_events of OutlookCalendarPlugin started")
            try:
                logger.info("Retrieving access token for calendar events")
                token = self._get_access_token()
                logger.info(f"Access token: {token} retrieved successfully")
            except Exception as e:
                answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text=f"Authentication error: {str(e)}",
                    operation="Explain the user in his language that you failed to get calendar appointment due to an error.",
                )
                return answer
            headers = {"Authorization": f"Bearer {token}"}
            now = datetime.datetime.utcnow().isoformat() + "Z"
            end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
            url = f"https://graph.microsoft.com/v1.0/me/calendarview?startDateTime={now}&endDateTime={end}"
            resp = requests.get(url, headers=headers)
            logger.info("Calendar get results: %s", resp.text)
            if resp.status_code != 200:
                answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text=f"Failed to fetch events: {resp.text}",
                    operation="Explain the user in his language that you failed to fetch calendar events due to an error.",
                )
                return answer
            events = resp.json().get("value", [])
            if not events:
                answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text="No events found.",
                    operation="Explain the user in his language that no events were found in the calendar.",
                )
                return answer
            events_text = "\n".join([f"{e.get('subject', 'No subject')} at {e.get('start', {}).get('dateTime', 'Unknown time')}" for e in events])
            answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text=events_text,
                    operation="Summarize the calendar schedule in the user's language.",
                )
            return answer

    @kernel_function(name="schedule_appointment", description="Schedule a new Outlook calendar appointment")
    def schedule_appointment(self, subject: str, start_time: str, end_time: str) -> str:
        with tracer.start_as_current_span("SemanticKernelOrchestrator_orchestrate.schedule_appointment"):
            logger.info("Method schedule_appointment of OutlookCalendarPlugin started")
            try:
                token = self._get_access_token()
            except Exception as e:
                answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text=f"Failed to schedule appointment: {str(e)}",
                    operation="Explain the user in his language that you failed to schedule a calendar appointment due to an error.",
                )
                return answer
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
                    operation="Explain to the user in his language that the appointment was scheduled successfully.",
                )
                return answer
            else:
                answer = TextProcessingTool().answer_question(
                    question=self.question,
                    chat_history=self.chat_history,
                    text=f"Failed to schedule appointment: {resp.text}",
                    operation="Explain to the user in his language that the appointment scheduling failed.",
                )
                return answer