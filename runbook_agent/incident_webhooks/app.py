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
)
from runbook_agent.runbook_executor.runbook_execution_factory import (
    AzureRunbookExecutor,
)
from runbook_agent.runbook_sources.services.azure_service.azure_runbook_models import (
    WebhookConfig,
)
import requests


# Create a router instance
router = APIRouter()


# Define the Pydantic model for the request payload
class Payload(BaseModel):
    sys_id: str
    short_description: str
    caller_id: str


def init(
    embedding_provider: BaseEmbeddingProvider,
    vector_store: VectorBaseRepository,
    r: AbstractAutomationRunbookService,
    executor: AzureRunbookExecutor,
    c: WebhookConfig,
):
    global queryEngine
    global repository
    global azureExecutor
    global config
    repository = r
    queryEngine = QueryEngine(
        embedding_provider=embedding_provider, vector_store=vector_store
    )
    azureExecutor = executor
    config = c


@router.post("/service_now/webhook")
async def receive_payload(payload: Payload, background_tasks: BackgroundTasks):
    background_tasks.add_task(take_incident_action, payload)
    return {"message": "Payload received and processing started in the background."}


async def take_incident_action(payload: Payload):
    # You can perform any action here with the received data
    results = queryEngine.query_vector_store(payload.short_description)
    searched_runbooks = [
        RunbookDetails(doc_id=result.doc_id, description=result.text)
        for result in results
    ]
    selected_runbook = select_runbook_for_execution(
        description=payload.short_description, runbooks=searched_runbooks
    )
    if selected_runbook.doc_id == "":
        return

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
            vmNamesResponse = func(payload.short_description)
            continue
        parameters[parameterKey] = func()

    if vmNamesResponse is not None and len(vmNamesResponse.vm_names) > 0:
        for vm in vmNamesResponse.vm_names:
            parameters[vmArgName] = vm
            id = azureExecutor.trigger_runbook(
                resource_group=config.resource_group,
                automation_account_name=config.automation_account,
                runbook_name=runbook_details.name,
                parameters=parameters,
            )
            await poll_job(id, payload.sys_id)
    elif vmArgName == "":
        id = azureExecutor.trigger_runbook(
            resource_group=config.resource_group,
            automation_account_name=config.automation_account,
            runbook_name=runbook_details.name,
            parameters=parameters,
        )
        await poll_job(id, payload.sys_id)


async def poll_job(id: str, sys_id: str):
    def hook(status, output):
        return update_description(
            status,
            output,
            "https://dev209832.service-now.com",
            sys_id,
            "yatish@futurepath.ai",
            "Best@123",
        )

    azureExecutor.wait_for_runbook_completion(
        resource_group=config.resource_group,
        automation_account_name=config.automation_account,
        job_id=id,
        hook_function=hook,
    )


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
        "description": f"{current_description}-----------------------------------\nJob execution status : {status} \n\n Output:{output}\n-----------------------------------\n"
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
