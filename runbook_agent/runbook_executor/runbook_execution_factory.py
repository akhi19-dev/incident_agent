from runbook_agent.runbook_executor.services.azure_execution_service import (
    AzureRunbookExecutor,
)
from runbook_agent.runbook_executor.base_execution_service import (
    BaseExecutionService,
)


class ExecutionServiceFactory:
    """
    Factory class to create instances of platform-specific execution services.
    """

    @staticmethod
    def create_executor(platform, **kwargs) -> BaseExecutionService:
        """
        Factory method to create an executor based on the platform.
        :param platform: The platform type (e.g., 'azure', 'aws').
        :param kwargs: Any additional arguments needed to initialize the executor.
        :return: An instance of a platform-specific executor.
        """
        if platform == "azure":
            return AzureRunbookExecutor(
                tenant_id=kwargs["tenant_id"],
                client_id=kwargs["client_id"],
                client_secret=kwargs["client_secret"],
                subscription_id=kwargs["subscription_id"],
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")
