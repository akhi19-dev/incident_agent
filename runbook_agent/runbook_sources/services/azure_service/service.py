import logging
import asyncio
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.indexing_service.indexing_engine import IndexingEngine
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
from runbook_agent.runbook_sources.services.azure_service.runbook_indexing_service import (
    RunbookIndexer,
)
from runbook_agent.runbook_sources.services.azure_service.azure_register_webhook_service import (
    AzureRunbookSourceManager,
)


class RunbookManager:
    def __init__(
        self,
        config,
        repository: AbstractAutomationRunbookService,
        vectorStore: VectorBaseRepository,
        indexingService: IndexingEngine,
    ):
        # Initialize the config, repository, vector store, and indexing service
        self.config = config
        self.logger = self._setup_logger()
        self.repository = repository
        self.vector_store = vectorStore
        self.indexing_service = indexingService
        self.azure_runbook_source_manager = AzureRunbookSourceManager(
            config=config,
            repository=repository,
            vectorStore=vectorStore,
            indexingService=indexingService,
        )
        self.runbook_indexer = RunbookIndexer(
            config, repository, vectorStore, indexingService
        
        )

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("RunbookManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def start(self):
        """Start the manager by syncing existing runbooks, creating the Activity Log alert, and starting background polling."""
        self.logger.info("Starting Runbook Manager...")

        # Sync existing runbooks
        await self.azure_runbook_source_manager.sync_existing_runbooks()

        # Create the Activity Log alert
        self.azure_runbook_source_manager.create_activity_log_alert()

        # Start polling for unindexed runbooks in the background
        self.logger.info(
            "Starting background polling for unindexed runbooks every 5 minutes."
        )
        asyncio.create_task(self.runbook_indexer.poll_for_unindexed_runbooks())
