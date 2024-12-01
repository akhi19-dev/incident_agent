from runbook_agent.runbook_sources.services.azure_service.service import (
    RunbookManager,
)
from runbook_agent.runbook_sources.base_runbook_source import BaseRunbookSourceManager
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.indexing_service.indexing_engine import IndexingEngine


class RunbookSourceFactory:
    """
    Factory for creating a RunbookSource based on configuration or parameters.
    This could create sources for various platforms like Azure, AWS, etc.
    """

    @staticmethod
    def create(
        config: dict,
        repository: AbstractAutomationRunbookService,
        vectorStore: VectorBaseRepository,
        indexingService: IndexingEngine,
    ) -> BaseRunbookSourceManager:
        """
        Factory method to create a RunbookSource instance.
        :param config: A dictionary containing configuration parameters.
        :param repository: The repository for storing the runbook data.
        :return: A concrete implementation of BaseRunbookSource.
        """
        platform = config.get("platform", "azure").lower()

        if platform == "azure":
            return RunbookManager(
                config=config["azure"],
                repository=repository,
                vectorStore=vectorStore,
                indexingService=indexingService,
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")
