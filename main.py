# main.py
from fastapi import FastAPI
import sys

sys.path.append("/Users/akhileshjain/Documents/FuturePath/incident_agent")
from runbook_agent.repository.automation_runbook_documents.automation_runbook_documents_service import (
    getAutomationRunbookService,
)
from runbook_agent.clients.prisma import get_prisma_client, init_prisma_client
from runbook_agent.repository.vector_store.vector_store_service import (
    VectorStoreService,
)
from runbook_agent.repository.vector_store.models import VectorStores
from runbook_agent.indexing_service.indexing_engine import IndexingEngine
from runbook_agent.embedding_provider.embedding_provider_factory import (
    EmbeddingServiceFactory,
)
from runbook_agent.embedding_provider.models import (
    EmbeddingModels,
    OPENAIModels,
)
from runbook_agent.runbook_sources.runbook_source_factory import RunbookSourceFactory
from runbook_agent.runbook_sources.services.azure_service.azure_runbook_models import (
    WebhookConfig,
)
from runbook_agent.incident_webhooks.app import router as incident_webhook_router
from runbook_agent.runbook_sources.services.azure_service.app import (
    router as azure_router,
)
from runbook_agent.incident_webhooks.app import init
from runbook_agent.runbook_executor.runbook_execution_factory import (
    ExecutionServiceFactory,
)
import os

# Create FastAPI app instance
app = FastAPI()

# Include routers
app.include_router(incident_webhook_router)
app.include_router(azure_router)


# Define hook function for execution service (can be used later)
def my_hook_function(status, output):
    print(status, output)


# Function to initialize the runbook source manager
async def init_runbook_source_manager():
    # Define the configuration for the platform (Azure, for example)
    config = {
        "platform": "azure",
        "azure": WebhookConfig(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            resource_group=os.getenv("AZURE_RESOURCE_GROUP"),
            automation_account=os.getenv("AZURE_AUTOMATION_ACCOUNT"),
            webhook_endpoint_url=os.getenv("AZURE_WEBHOOK_ENDPOINT"),
            webhook_name=os.getenv("AZURE_WEBHOOK_NAME"),
        ),
    }
    await init_prisma_client()
    # Initialize the necessary services
    repository = getAutomationRunbookService(get_prisma_client())
    vectorStore = VectorStoreService(VectorStores.LANCEDB, "incident_agent_runbook")
    embedding_provider = EmbeddingServiceFactory.create_embedding_service(
        provider_type=EmbeddingModels.OPENAI,
        model_id=OPENAIModels.TEXT_EMBEDDING_3_SMALL.value,
    )
    executor = ExecutionServiceFactory.create_executor(
        platform="azure",
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    )

    init(
        embedding_provider=embedding_provider,
        vector_store=vectorStore,
        r=repository,
        executor=executor,
        c=config.get("azure"),
        client=get_prisma_client()
    )

    indexingService = IndexingEngine(
        embedding_provider=embedding_provider, vector_store=vectorStore
    )
    runbookSource = RunbookSourceFactory.create(
        config=config,
        repository=repository,
        vectorStore=vectorStore,
        indexingService=indexingService,
    )

    # Start the runbook source manager
    await runbookSource.start()

    # Example: Trigger an execution for a runbook
    # You can enable the execution part when needed
    # executor = ExecutionServiceFactory.create_executor(...)
    # job_id = executor.trigger_runbook(...)
    # executor.wait_for_runbook_completion(...)

# FastAPI startup event to initialize services
@app.on_event("startup")
async def startup():
    # Initialize the runbook source manager during startup
    await init_runbook_source_manager()
