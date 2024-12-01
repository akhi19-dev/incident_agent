import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor.v2017_04_01 import MonitorManagementClient
from azure.mgmt.monitor.v2020_10_01.models import (
    AlertRuleAllOfCondition,
    AlertRuleAnyOfOrLeafCondition,
    ActivityLogAlertResource,
    AlertRuleLeafCondition,
    ActionList,
    ActionGroup,
)
from azure.mgmt.monitor.v2023_01_01.models import (
    WebhookReceiver,
    ActionGroupResource,
)
from azure.mgmt.automation import AutomationClient
from runbook_agent.runbook_sources.services.azure_service.azure_runbook_models import (
    WebhookConfig,
)
from runbook_agent.repository.automation_runbook_documents.models import (
    AutomationRunbookDocumentModel,
)
from runbook_agent.repository.automation_runbook_documents.base_automation_runbook_documents_service import (
    AbstractAutomationRunbookService,
)
from runbook_agent.repository.vector_store.base_repository import VectorBaseRepository
from runbook_agent.indexing_service.indexing_engine import IndexingEngine
import asyncio


class AzureRunbookSourceManager:
    def __init__(
        self,
        config: WebhookConfig,
        repository: AbstractAutomationRunbookService,
        vectorStore: VectorBaseRepository,
        indexingService: IndexingEngine,
    ):
        self.config = config
        self.logger = self._setup_logger()
        self.credentials = None
        self.event_grid_client = None
        self.monitor_client = None
        self.automation_client = None
        self._initialize_clients()
        self.action_group_name = "nva_actions"
        self.activity_log_alert_name = "runbook_source"
        self.action_group_id = f"/subscriptions/{self.config.subscription_id}/resourceGroups/{self.config.resource_group}/providers/microsoft.insights/actionGroups/{self.action_group_name}"
        self.repository = repository
        self.vector_store = vectorStore
        self.indexing_service = indexingService

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("AzureWebhookManager")
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
        try:
            self.credentials = ClientSecretCredential(
                tenant_id=self.config.tenant_id,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
            self.monitor_client = MonitorManagementClient(
                self.credentials, self.config.subscription_id
            )
            self.automation_client = AutomationClient(
                self.credentials, self.config.subscription_id
            )
            self.logger.info("Azure clients initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure clients: {str(e)}")
            raise

    def action_group_exists(self, action_group_name: str) -> bool:
        """Check if the Action Group already exists."""
        try:
            # Attempt to get the action group by name
            result = self.monitor_client.action_groups.get(
                self.config.resource_group, action_group_name
            )
            return result.id
        except Exception:
            return None

    def activity_log_alert_exists(self, alert_name: str) -> bool:
        """Check if the Action Group already exists."""
        try:
            # Attempt to get the action group by name
            result = self.monitor_client.activity_log_alerts.get(
                self.config.resource_group, activity_log_alert_name=alert_name
            )
            return result.id
        except Exception:
            return None

    def create_action_group(self):
        """Create an Action Group for triggering the webhook with a name."""
        try:
            # Check if the Action Group already exists
            id = self.action_group_exists(self.action_group_name)
            if id is not None:
                self.logger.info(
                    f"Skipping creation of Action Group '{self.action_group_name}' as it already exists."
                )
                return id

            # Define the webhook receiver that will be triggered by the alert
            webhook_receiver = WebhookReceiver(
                name="RunbookWebhookReceiver",
                service_uri=self.config.webhook_endpoint_url,
            )

            # Create the Action Group
            action_group = ActionGroupResource(
                location="Global",  # Location should be 'Global' for action groups
                group_short_name=self.action_group_name,  # Short name for the action group
                enabled=True,
                webhook_receivers=[webhook_receiver],  # Include the webhook receivers
            )

            # Create the Action Group in Azure
            action_group_resource = self.monitor_client.action_groups.create_or_update(
                resource_group_name=self.config.resource_group,
                action_group_name=self.action_group_name,
                action_group=action_group,
            )

            self.logger.info(
                f"Action Group '{self.action_group_name}' created successfully."
            )
            return action_group_resource.id

        except Exception as e:
            self.logger.error(f"Error creating Action Group: {str(e)}")
            raise

    def create_activity_log_alert(self):
        """Create an Activity Log alert for Runbook published and deleted events."""
        try:
            id = self.activity_log_alert_exists(self.activity_log_alert_name)
            if id is not None:
                self.logger.info(
                    f"Skipping creation of activity log alert '{self.activity_log_alert_name}' as it already exists."
                )
                return id

            action_group_id = self.create_action_group()

            condition = AlertRuleAllOfCondition(
                all_of=[
                    AlertRuleAnyOfOrLeafCondition(
                        any_of=[
                            AlertRuleLeafCondition(
                                field="operationName",
                                equals="Microsoft.Automation/automationAccounts/runbooks/publish/action",
                            ),
                            AlertRuleLeafCondition(
                                field="operationName",
                                equals="Microsoft.Automation/automationAccounts/runbooks/delete",
                            ),
                        ]
                    ),
                    AlertRuleAnyOfOrLeafCondition(
                        field="category", equals="Administrative"
                    ),
                    AlertRuleAnyOfOrLeafCondition(
                        field="resourceType",
                        equals="microsoft.automation/automationaccounts/runbooks",
                    ),
                ]
            )

            action_groups = ActionList(
                action_groups=[ActionGroup(action_group_id=action_group_id)]
            )

            resource_id = f"/subscriptions/{self.config.subscription_id}/resourceGroups/{self.config.resource_group}/providers/Microsoft.Automation/automationAccounts/{self.config.automation_account}"
            # Create the Activity Log alert rule
            alert_rule = ActivityLogAlertResource(
                scopes=[resource_id],
                condition=condition,
                actions=action_groups,
                description="Trigger an action when a Runbook is published or deleted",
                enabled=True,
            )

            # Create or update the alert rule
            alert_rule_name = "RunbookActivityAlert"
            alert_rule_poller = (
                self.monitor_client.activity_log_alerts.create_or_update(
                    resource_group_name=self.config.resource_group,
                    activity_log_alert_name=self.activity_log_alert_name,
                    activity_log_alert=alert_rule,
                )
            )
            self.logger.info(
                f"Activity Log Alert '{alert_rule_name}' created successfully"
            )
            return alert_rule_poller.id

        except Exception as e:
            self.logger.error(f"Error creating Activity Log alert: {str(e)}")
            raise

    async def update_is_indexed_flag(self):
        while True:
            try:
                # Query the repository for all runbooks where is_indexed is False
                runbooks_to_index = (
                    await self.repository.get_unindexed_automation_runbook()
                )

                if runbooks_to_index:
                    for runbook in runbooks_to_index:
                        await self.repository.update_runbook_is_indexed(
                            runbook.id, is_indexed=True
                        )
            except Exception as e:
                self.logger.error(
                    f"Error occurred while updating indexing flag: {str(e)}"
                )

            await asyncio.sleep(300)  # Sleep for 5 minutes

    async def sync_existing_runbooks(self):
        """
        Fetch the list of all runbooks in the specified Automation Account.

        :return: A list of dictionaries containing runbook details (name, type, state)
        """
        runbooks = self.automation_client.runbook.list_by_automation_account(
            self.config.resource_group, self.config.automation_account
        )

        for runbook in runbooks:
            try:
                existing_runbook = await self.repository.get_runbook_by_name_and_source(
                    name=runbook.name, source="azure"
                )
                if existing_runbook is not None:
                    continue

                await self.repository.add_runbook(
                    runbook_data=AutomationRunbookDocumentModel(
                        name=runbook.name,
                        source="azure",
                        published_time=runbook.last_modified_time,
                        is_indexed=False,
                        type=runbook.runbook_type,
                        args=[],
                        os_supported=[],
                        tags=[],
                    )
                )
            except Exception as e:
                print(e)
                continue
