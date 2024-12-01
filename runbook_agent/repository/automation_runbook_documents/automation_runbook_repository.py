from prisma import Prisma
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from typing import List, Optional


class AutomationRunbookClient:
    def __init__(self, prisma_client: Prisma):
        self.client = prisma_client

    async def add_runbook(
        self, runbook_data: AutomationRunbookDocumentModel
    ) -> AutomationRunbookDocumentModel:
        """
        Adds a new runbook document to the database.

        Args:
            runbook_data (AutomationRunbookDocumentModel): The data of the runbook to be added.

        Returns:
            AutomationRunbookDocumentModel: The added runbook document.
        """
        created_runbook = await self.client.automation_script_documents.create(
            data={
                "name": runbook_data.name,
                "source": runbook_data.source,
                "published_time": runbook_data.published_time,
                "is_indexed": runbook_data.is_indexed,
                "description": runbook_data.description,
                "os_supported": runbook_data.os_supported,
                "args": runbook_data.args,
                "type": runbook_data.type,
                "tags": runbook_data.tags,
            }
        )
        return created_runbook

    async def update_runbook_by_id(
        self, id: str, runbook_data: AutomationRunbookDocumentModel
    ):
        """
        Updates multiple fields of an existing runbook document in the database.

        Args:
            id (str): The ID of the runbook to update.
            runbook_data (AutomationRunbookDocumentModel): The data to update the runbook with.
        """
        # Prepare the data dictionary with only the fields that are not None
        data_to_update = {
            field: value
            for field, value in runbook_data.dict(exclude_unset=True).items()
        }

        # Ensure the 'id' field is not included in the data_to_update dictionary, since it's handled by 'where'
        if "id" in data_to_update:
            del data_to_update["id"]

        try:
            # Perform the update operation
            await self.client.automation_script_documents.update(
                where={"id": id}, data=data_to_update
            )
        except Exception as e:
            # Log or handle the error as appropriate
            print(f"Error updating runbook: {e}")
            raise

    async def update_runbook_by_name_and_source(
        self, name: str, source: str, runbook_data: AutomationRunbookDocumentModel
    ):
        """
        Updates multiple fields of an existing runbook document in the database.

        Args:
            name (str): The ID of the runbook to update.
            source (str): The source of the runbook to update
            runbook_data (AutomationRunbookDocumentModel): The data to update the runbook with.
        """
        # Prepare the data dictionary with only the fields that are not None
        data_to_update = {
            field: value
            for field, value in runbook_data.dict(exclude_unset=True).items()
        }

        if "name" in data_to_update:
            del data_to_update["name"]
        if "source" in data_to_update:
            del data_to_update["source"]

        try:
            # Perform the update operation
            await self.client.automation_script_documents.update_many(
                where={"name": name, "source": source}, data=data_to_update
            )
        except Exception as e:
            print(f"Error updating runbook: {e}")
            raise

    async def delete_runbook(self, runbook_name: str, source: str) -> bool:
        """
        Deletes a runbook document from the database by ID.

        Args:
            runbook_id (str): The ID of the runbook to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            await self.client.automation_script_documents.delete(
                where={"name": runbook_name, "source": source}
            )
            return True
        except Exception as e:
            print(f"Error deleting runbook: {e}")
            return False

    async def get_unindexed_runbooks(self) -> List[AutomationRunbookDocumentModel]:
        """
        Fetches all runbooks from the database where the 'isIndexed' flag is False.

        Returns:
            List[AutomationRunbookDocumentModel]: A list of unindexed runbook documents.
        """
        try:
            unindexed_runbooks = (
                await self.client.automation_script_documents.find_many(
                    where={"is_indexed": False}
                )
            )

            # Convert the results to a list of AutomationRunbookDocumentModel instances
            return [
                AutomationRunbookDocumentModel(
                    id=runbook.id,
                    name=runbook.name,
                    source=runbook.source,
                    published_time=runbook.published_time,
                    is_indexed=runbook.is_indexed,
                    description=runbook.description,
                    os_supported=runbook.os_supported,
                    args=runbook.args,
                    type=runbook.type,
                    tags=runbook.tags,
                )
                for runbook in unindexed_runbooks
            ]
        except Exception as e:
            print(f"Error fetching unindexed runbooks: {e}")
            return []

    async def get_by_name_and_source(
        self, name: str, source: str
    ) -> Optional[AutomationRunbookDocumentModel]:
        """
        Fetches a single runbook from the database by its name and source.

        Args:
            name (str): The name of the runbook.
            source (str): The source of the runbook.

        Returns:
            Optional[AutomationRunbookDocumentModel]: A single runbook document or None if not found.
        """
        try:
            # Fetch the runbook from the database where name and source match
            runbook = await self.client.automation_script_documents.find_first(
                where={"name": name, "source": source}  # Filtering by name and source
            )
            if runbook:
                return AutomationRunbookDocumentModel(
                    id=runbook.id,
                    name=runbook.name,
                    source=runbook.source,
                    published_time=runbook.published_time,
                    is_indexed=runbook.is_indexed,
                    description=runbook.description,
                    os_supported=runbook.os_supported,
                    args=runbook.args,
                    type=runbook.type,
                    tags=runbook.tags,
                )
            else:
                return None  # Return None if no matching runbook is found

        except Exception as e:
            print(f"Error fetching runbook by name and source: {e}")
            return None  # Return None in case of an error

    async def get_by_id(
        self, runbook_id: str
    ) -> Optional[AutomationRunbookDocumentModel]:
        """
        Fetches a single runbook from the database by its id.

        Args:
            runbook_id (str): The ID of the runbook.

        Returns:
            Optional[AutomationRunbookDocumentModel]: A single runbook document or None if not found.
        """
        try:
            runbook = await self.client.automation_script_documents.find_first(
                where={"id": runbook_id}
            )
            if runbook:
                return AutomationRunbookDocumentModel(
                    id=runbook.id,
                    name=runbook.name,
                    source=runbook.source,
                    published_time=runbook.published_time,
                    is_indexed=runbook.is_indexed,
                    description=runbook.description,
                    os_supported=runbook.os_supported,
                    args=runbook.args,
                    type=runbook.type,
                    tags=runbook.tags,
                )
            else:
                return None

        except Exception as e:
            print(f"Error fetching runbook by id: {e}")
            return None
