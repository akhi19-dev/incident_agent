from abc import ABC, abstractmethod
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from typing import List, Optional


class AbstractAutomationRunbookService(ABC):
    @abstractmethod
    async def add_runbook(
        self, runbook_data: AutomationRunbookDocumentModel
    ) -> AutomationRunbookDocumentModel:
        pass

    @abstractmethod
    async def update_runbook_by_id(
        self, id: str, runbook_data: AutomationRunbookDocumentModel
    ):
        pass

    @abstractmethod
    async def update_runbook_by_name_and_source(
        self, name: str, source: str, runbook_data: AutomationRunbookDocumentModel
    ):
        """
        Abstract method to update a runbook by its name and source.
        """
        pass

    @abstractmethod
    async def get_runbook_by_name_and_source(
        self,
        name: str,
        source: str,
    ) -> AutomationRunbookDocumentModel:
        pass

    @abstractmethod
    async def get_unindexed_automation_runbook(
        self,
    ) -> List[AutomationRunbookDocumentModel]:
        pass

    @abstractmethod
    async def delete_runbook(self, runbook_name: str, source: str) -> bool:
        pass

    @abstractmethod
    async def get_by_id(
        self, runbook_id: str
    ) -> Optional[AutomationRunbookDocumentModel]:
        pass
