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

    @abstractmethod
    def schedule_runbook_execution(
        self,
        resource_group: str,
        automation_account_name: str,
        schedule_name: str,
        runbook_name: str,
        parameters: dict,
        start_time: str,  # Mandatory: Schedule start time in ISO 8601 format
        expiry_time: str = None,  # Optional: Expiry time for the schedule
        interval: int = 1,  # Interval for recurrence (default 1)
        frequency: str = "OneTime",  # Mandatory: "OneTime", "Day", "Week", etc.
        time_zone: str = "UTC",  # Mandatory: Time zone
        week_days: list[
            str
        ] = None,  # Optional: Days of the week (e.g., ["Monday", "Wednesday"])
        month_days: list[int] = None,  # Optional: Days of the month (e.g., [1, 15, 31])
    ):
        """
        Schedule a runbook execution
        """
        pass
