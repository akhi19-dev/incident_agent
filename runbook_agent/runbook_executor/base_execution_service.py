from abc import ABC, abstractmethod


class BaseExecutionService(ABC):
    """
    Abstract Base Class for runbook job execution.
    Each platform-specific executor will inherit from this.
    """

    @abstractmethod
    def trigger_runbook(
        self, resource_group, automation_account_name, runbook_name, parameters
    ):
        """
        Trigger the runbook with the provided parameters.
        """
        pass

    @abstractmethod
    def get_runbook_status(self, resource_group, automation_account_name, job_name):
        """
        Retrieve the status of the runbook job.
        """
        pass

    @abstractmethod
    def wait_for_runbook_completion(
        self, resource_group, automation_account_name, job_id, hook_function
    ):
        """
        Wait for runbook job to complete.
        """
        pass
