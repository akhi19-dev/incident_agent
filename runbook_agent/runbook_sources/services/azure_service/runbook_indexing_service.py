import logging
from azure.mgmt.automation import AutomationClient
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from runbook_agent.indexing_service.indexing_engine import IndexingEngine
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
import asyncio
from runbook_agent.llms.open_ai import chat_completion_request_instructor
from runbook_agent.runbook_sources.prompts import (
    get_runbook_analysis_message,
    list_of_function,
    RunbookAnalyserResponse,
)
from runbook_agent.repository.vector_store.schemas import QueryDocId
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository


class RunbookIndexer:
    def __init__(
        self,
        config,
        repository: AbstractAutomationRunbookService,
        vector_store: VectorBaseRepository,
        indexing_engine: IndexingEngine,
    ):
        self.config = config
        self.logger = self._setup_logger()
        self.repository = repository
        self.indexing_engine = indexing_engine
        self.vector_store = vector_store
        self.automation_client = None
        self._initialize_clients()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("RunbookIndexer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _initialize_clients(self) -> None:
        """Initialize Azure clients for automation service."""
        try:
            from azure.identity import ClientSecretCredential

            self.credentials = ClientSecretCredential(
                tenant_id=self.config.tenant_id,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
            self.automation_client = AutomationClient(
                self.credentials, self.config.subscription_id
            )
            self.logger.info("Automation client initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Automation client: {str(e)}")
            raise

    async def get_runbook_content_direct(self, runbook_name):
        import requests

        # Get access token
        credential = self.credentials
        token = credential.get_token("https://management.azure.com/.default").token

        # Construct URL
        url = (
            f"https://management.azure.com/subscriptions/{self.config.subscription_id}"
            f"/resourceGroups/{self.config.resource_group}"
            f"/providers/Microsoft.Automation/automationAccounts/{self.config.automation_account}"
            f"/runbooks/{runbook_name}/content?api-version=2023-11-01"
        )

        # Make request
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text

    async def index_runbook(self, runbook):
        """Index the runbook into the repository and vector store."""
        try:
            # Fetch the content of the runbook from Azure
            runbook_content = await self.get_runbook_content_direct(runbook.name)
            if not runbook_content:
                self.logger.warning(
                    f"Skipping indexing for runbook '{runbook.name}' due to missing content."
                )
                return

            response = chat_completion_request_instructor(
                get_runbook_analysis_message(
                    runbook=runbook_content, list_of_functions=list_of_function
                ),
                model="gpt-4o-mini",
                temperature=0.2,
                max_tokens=4000,
                response_model=RunbookAnalyserResponse,
            )

            responseModel = None
            if isinstance(response, RunbookAnalyserResponse):
                responseModel = response
            else:
                return

            try:
                self.vector_store.delete_by_doc_ids(
                    query=[QueryDocId(doc_id=runbook.id)]
                )
            except Exception as e:
                self.logger.error(f"Error deleting runbook '{runbook.id}': {str(e)}")

            description = responseModel.description + '\n' + '\n'.join(responseModel.issues_it_resolves) + '\n' + '\n'.join(responseModel.user_queries)
            self.indexing_engine.insert_text_to_vector_store(
                doc_id=runbook.id,
                file_name=runbook.name,
                text=description,
                label="",
            )
            runbook_document = AutomationRunbookDocumentModel(
                is_indexed=True,
                description=description,
                os_supported=[os.lower() for os in responseModel.array_of_os],
                args=[
                    f"{argumentModel.name.lower()}:{argumentModel.function_to_extract.lower()}"
                    for argumentModel in responseModel.array_of_args
                ],
            )
            # Add the runbook to the repository
            await self.repository.update_runbook_by_name_and_source(
                name=runbook.name,
                source="azure",
                runbook_data=runbook_document,
            )

            self.logger.info(f"Runbook '{runbook.name}' indexed successfully.")

        except Exception as e:
            self.logger.error(f"Error indexing runbook '{runbook.name}': {str(e)}")

    async def index_unindexed_runbooks(self):
        """Fetch all unindexed runbooks from the repository and index them."""
        try:
            # Fetch runbooks from the repository where is_indexed is False
            runbooks_to_index = await self.repository.get_unindexed_automation_runbook()

            if not runbooks_to_index:
                self.logger.info("No unindexed runbooks found.")
                return

            # Index each runbook
            for runbook in runbooks_to_index:
                await self.index_runbook(runbook)

        except Exception as e:
            self.logger.error(f"Error indexing unindexed runbooks: {str(e)}")

    async def poll_for_unindexed_runbooks(self):
        """Polls every 5 minutes to index unindexed runbooks."""
        while True:
            await self.index_unindexed_runbooks()
            await asyncio.sleep(300)  # Sleep for 5 minutes (300 seconds)
