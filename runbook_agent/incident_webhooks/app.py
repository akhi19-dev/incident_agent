# api/webhook.py
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from runbook_agent.query_engine.query_engine import QueryEngine
from runbook_agent.embedding_provider.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
from runbook_agent.runbook_sources.prompts import (
    function_map,
    select_runbook_for_execution,
    RunbookDetails,
    action_sequences,
)
from runbook_agent.runbook_executor.runbook_execution_factory import (
    BaseExecutionService,
)
from runbook_agent.runbook_sources.services.azure_service.azure_runbook_models import (
    WebhookConfig,
)
import requests
import os
from datetime import datetime
import pytz
import uuid
from prisma import Prisma
import asyncio

# Create a router instance
router = APIRouter()


# Define the Pydantic model for the request payload
class Payload(BaseModel):
    sys_id: str
    short_description: str
    caller_id: str
    description: str
    severity: str
    status: str


def init(
    embedding_provider: BaseEmbeddingProvider,
    vector_store: VectorBaseRepository,
    r: AbstractAutomationRunbookService,
    executor: BaseExecutionService,
    c: WebhookConfig,
    client: Prisma,
):
    global queryEngine
    global repository
    global azureExecutor
    global config
    global prisma_client
    repository = r
    queryEngine = QueryEngine(
        embedding_provider=embedding_provider, vector_store=vector_store
    )
    azureExecutor = executor
    config = c
    prisma_client = client


@router.post("/service_now/webhook")
async def receive_payload(payload: Payload, background_tasks: BackgroundTasks):
    existing_incident = await prisma_client.incident.find_first(
        where={
            "url": f"https://dev209832.service-now.com/nav_to.do?uri=incident.do?sys_id={payload.sys_id}"
        }
    )
    if not existing_incident:
        await prisma_client.incident.create(
            data={
                "org_id": "6fed2673-1fc3-4367-be99-2dd985d78319",
                "subject": payload.short_description,
                "start_time": datetime.now().utcnow(),
                "end_time": datetime.now().utcnow(),
                "severity": "critical",
                "description": payload.description,
                "status": "new",
                "urgency": 3,
                "impact": 3,
                "url": f"https://dev209832.service-now.com/nav_to.do?uri=incident.do?sys_id={payload.sys_id}",
            }
        )
    background_tasks.add_task(take_incident_action, payload)
    return {"message": "Payload received and processing started in the background."}


async def take_incident_action(payload: Payload):
    # You can perform any action here with the received data
    results = queryEngine.query_vector_store(payload.description)
    searched_runbooks = [
        RunbookDetails(doc_id=result.doc_id, description=result.text)
        for result in results
    ]
    selected_runbook = select_runbook_for_execution(
        description=payload.description, runbooks=searched_runbooks
    )
    if selected_runbook.doc_id == "":
        return
    print(selected_runbook, searched_runbooks)

    runbook_details = await repository.get_by_id(selected_runbook.doc_id)
    if runbook_details is None:
        return
    parameters = {}
    vmArgName = ""
    vmNamesResponse = None
    for item in runbook_details.args:
        # Split the item at the colon
        parameterKey, funcName = item.split(":", 1)

        if funcName == "":
            return

        func = function_map[funcName]
        if func is None:
            return
        if funcName == "get_vm_names()":
            vmArgName = parameterKey
            vmNamesResponse = func(payload.description)
            continue
        parameters[parameterKey] = func()

    if vmNamesResponse is not None and len(vmNamesResponse.vm_names) > 0:
        for vm in vmNamesResponse.vm_names:
            parameters[vmArgName] = vm
            action_pipeline = action_sequences(
                ticket_description=payload.description,
                selected_runbook_description=selected_runbook.description,
                user_entity_information=f"Focus only on actions to be taken for entity {vm}",
            )
            print(action_pipeline)
            if action_pipeline.func_name == "SchdeuleTaskForExecution":
                timezone = pytz.timezone(action_pipeline.args["time_zone"])
                start_time = datetime.fromisoformat(action_pipeline.args["start_time"])
                expiry_time = None
                if (
                    "expiry_time" in action_pipeline.args
                    and action_pipeline.args["expiry_time"] != ""
                ):
                    expiry_time = datetime.fromisoformat(
                        action_pipeline.args["expiry_time"]
                    )
                interval = action_pipeline.args["interval"]
                frequency = action_pipeline.args["frequency"]
                id = azureExecutor.schedule_runbook_execution(
                    resource_group=config.resource_group,
                    automation_account_name=config.automation_account,
                    schedule_name=uuid.uuid4(),
                    runbook_name=runbook_details.name,
                    parameters=parameters,
                    start_time=start_time,
                    expiry_time=expiry_time,
                    interval=interval,
                    frequency=frequency,
                    time_zone=timezone,
                )
                update_description(
                    "Completed",
                    f"Task scheduled for {vm}",
                    os.getenv("SERVICE_NOW_URL"),
                    payload.sys_id,
                    os.getenv("SERVICE_NOW_USERNAME"),
                    os.getenv("SERVICE_NOW_PASSWORD"),
                )
                update_incident_table(
                    "Completed",
                    f"Task scheduled for {vm}",
                    payload.sys_id,
                    runbook_details.name,
                )
            if action_pipeline.func_name == "TriggerTaskImmediately":
                id = azureExecutor.trigger_runbook(
                    resource_group=config.resource_group,
                    automation_account_name=config.automation_account,
                    runbook_name=runbook_details.name,
                    parameters=parameters,
                )
                await poll_job(id, payload.sys_id, vm, runbook_details.name)
    elif vmArgName == "":
        id = azureExecutor.trigger_runbook(
            resource_group=config.resource_group,
            automation_account_name=config.automation_account,
            runbook_name=runbook_details.name,
            parameters=parameters,
        )
        await poll_job(id, payload.sys_id, "", runbook_details.name)


async def poll_job(id: str, sys_id: str, vm: str, runbook_name: str):
    def hook(status, output):
        update_incident_table(
            "completed", output, sys_id, runbook_name
        )
        return update_description(
            status,
            output,
            os.getenv("SERVICE_NOW_URL"),
            sys_id,
            os.getenv("SERVICE_NOW_USERNAME"),
            os.getenv("SERVICE_NOW_PASSWORD"),
        )

    azureExecutor.wait_for_runbook_completion(
        resource_group=config.resource_group,
        automation_account_name=config.automation_account,
        job_id=id,
        hook_function=hook,
    )


def update_incident_table(status, output, sys_id, runbook_name):
    runbook_link_template = (
        "https://portal.azure.com/#@futurepath.dev/resource/subscriptions/8a73585c-429c-4438-900a-3202dc668d02/"
        "resourceGroups/nva_auto_resolve_demo_rg/providers/Microsoft.Automation/"
        "automationAccounts/azure-runbook-nva-disc-usage-demo/runbooks/{runbook_name}/overview"
    )

    # Generate the runbook link
    runbook_link = runbook_link_template.format(runbook_name=runbook_name)

    try:
        # Try to get the current running loop
        loop = asyncio.get_running_loop()
        # Use asyncio.create_task to schedule the coroutine
        loop.create_task(
            _update_incident_async(status, output, sys_id, runbook_link, runbook_name)
        )
    except RuntimeError:
        # If no event loop is running, create a new loop and run the coroutine
        asyncio.run(_update_incident_async(status, output, sys_id, runbook_link))


async def _update_incident_async(status, output, sys_id, runbook_link, runbook_name):
    try:
        await prisma_client.incident.update_many(
            where={
                "url": f"https://dev209832.service-now.com/nav_to.do?uri=incident.do?sys_id={sys_id}"
            },
            data={
                "runbook_executed": True,
                "runbook_status": status.lower(),
                "runbook_name": runbook_name,
                "runbook_link": runbook_link,
                "runbook_output": output,
            },
        )
    except Exception as e:
        print(e)


def update_description(status, output, instance_url, sys_id, username, password):
    url = f"{instance_url}/api/now/table/incident/{sys_id}"

    # Headers to indicate the content type
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    get_response = requests.get(url, auth=(username, password), headers=headers)

    if get_response.status_code == 200:
        current_description = (
            get_response.json().get("result", {}).get("description", "")
        )
        if current_description != "":
            current_description = f"{current_description}\n\n"
    else:
        print(f"Failed to retrieve incident. Status code: {get_response.status_code}")
        return

    # Construct the URL for the record in ServiceNow
    url = f"{instance_url}/api/now/table/incident/{sys_id}"

    # Headers to indicate the content type
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # The payload to update the description
    payload = {
        "description": f"{current_description}-----------------------------------\nJob execution status : {status} at {datetime.now().strftime("%d-%m-%Y %H:%M")} \n\nOutput:\n{output}\n-----------------------------------\n"
    }

    # Make the PUT request to update the description
    response = requests.patch(
        url, auth=(username, password), headers=headers, json=payload
    )

    # Check if the update was successful
    if response.status_code == 200:
        print(f"Description updated successfully for ticket with sys_id: {sys_id}")
    else:
        print(f"Failed to update description. Status code: {response.status_code}")

    return response
