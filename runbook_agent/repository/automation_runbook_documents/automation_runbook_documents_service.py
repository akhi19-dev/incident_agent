from prisma import Prisma
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from runbook_agent.repository.automation_runbook_documents.automation_runbook_repository import (
    AutomationRunbookClient,
)
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
from typing import List, Optional


def getAutomationRunbookService(
    prisma_client: Prisma,
) -> AbstractAutomationRunbookService:
    return AutomationRunbookService(prisma_client=prisma_client)


class AutomationRunbookService(AbstractAutomationRunbookService):
    def __init__(self, prisma_client: Prisma):
        self.repository = AutomationRunbookClient(prisma_client)

    async def add_runbook(
        self, runbook_data: AutomationRunbookDocumentModel
    ) -> AutomationRunbookDocumentModel:
        """
        Adds a new runbook document.

        Args:
            runbook_data (AutomationRunbookDocumentModel): The runbook data to be added.

        Returns:
            AutomationRunbookDocumentModel: The added runbook.
        """
        return await self.repository.add_runbook(runbook_data)

    async def update_runbook_by_id(
        self,
        id: str,
        runbook_data: AutomationRunbookDocumentModel,
    ):
        """
        Updates a runbook document.

        Args:
            id (str): The id of the runbook to update.
            runbook_data (AutomationRunbookDocumentModel): The new data for the runbook.
        """
        return await self.repository.update_runbook_by_id(id, runbook_data)

    async def update_runbook_by_name_and_source(
        self,
        name: str,
        source: str,
        runbook_data: AutomationRunbookDocumentModel,
    ):
        """
        Updates a runbook document.

        Args:
            name (str): The name of the runbook to update.
            source (str): The source of the runbook to update.
            runbook_data (AutomationRunbookDocumentModel): The new data for the runbook.
        """
        return await self.repository.update_runbook_by_name_and_source(
            name, source, runbook_data
        )

    async def delete_runbook(self, runbook_name: str, source: str) -> bool:
        """
        Deletes a runbook document.

        Args:
            runbook_name (str): The name of the runbook to delete.
            source (str): The source of the runbook.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return await self.repository.delete_runbook(runbook_name, source)

    async def get_unindexed_automation_runbook(
        self,
    ) -> List[AutomationRunbookDocumentModel]:
        """
        Gets unindexed runbook document.

        Returns:
            runbook_data (AutomationRunbookDocumentModel): The data for the runbook.
        """
        return await self.repository.get_unindexed_runbooks()

    async def get_runbook_by_name_and_source(
        self, name: str, source: str
    ) -> Optional[AutomationRunbookDocumentModel]:
        """
        Gets unindexed runbook document.

        Args:
            runbook_name (str): The name of the runbook to delete.
            source (str): The source of the runbook.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return await self.repository.get_by_name_and_source(name=name, source=source)

    async def get_by_id(
        self, runbook_id: str
    ) -> Optional[AutomationRunbookDocumentModel]:
        return await self.repository.get_by_id(runbook_id=runbook_id)
