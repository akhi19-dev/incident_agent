# api/webhook.py
from fastapi import APIRouter, HTTPException, Request
import logging
import re
from datetime import datetime
from runbook_agent.repository.automation_runbook_documents.automation_runbook_documents_service import (
    getAutomationRunbookService,
)
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from runbook_agent.clients.prisma import get_prisma_client

# Create a router instance
router = APIRouter()

# Set up logging
logger = logging.getLogger("WebhookReceiver")


# Define the POST route to handle incoming webhook requests
@router.post("/azure/automation_runbook_webhook")
async def handle_webhook(request: Request):
    """
    Handles incoming webhook requests from Azure Activity Log Alerts
    """
    try:
        response = await request.json()
        properties = (
            response.get("data", {})
            .get("context", {})
            .get("activityLog", {})
            .get("properties", {})
        )
        if properties == {}:
            return

        eventTimestamp = (
            response.get("data", {})
            .get("context", {})
            .get("activityLog", {})
            .get("eventTimestamp")
        )
        if eventTimestamp == {}:
            return
        # Initialize automation runbook repository
        automation_runbook_repository = getAutomationRunbookService(get_prisma_client())

        # Extract the runbook name from the resourceId
        runbook_name = re.search(r"runbooks/([^/]+)", properties.get("entity")).group(1)

        # Parse the event timestamp into a datetime object
        event_timestamp_str = re.sub(r"(\.\d{6})\d+", r"\1", eventTimestamp)
        format_str = "%Y-%m-%dT%H:%M:%S.%f%z"

        event_time = datetime.strptime(event_timestamp_str, format_str)

        existing_runbook = (
            await automation_runbook_repository.get_runbook_by_name_and_source(
                name=runbook_name,
                source="azure",
            )
        )
        if existing_runbook is not None:
            # Update the runbook in the repository
            await automation_runbook_repository.update_runbook_by_name_and_source(
                name=runbook_name,
                source="azure",
                runbook_data=AutomationRunbookDocumentModel(
                    published_time=event_time,
                    is_indexed=False,
                ),
            )
            return
        await automation_runbook_repository.add_runbook(
            runbook_data=AutomationRunbookDocumentModel(
                name=runbook_name,
                source="azure",
                published_time=event_time,
                is_indexed=False,
                os_supported=[],
                args=[],
                type="",
                tags=[],
            )
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Error processing webhook: {str(e)}"
        )
