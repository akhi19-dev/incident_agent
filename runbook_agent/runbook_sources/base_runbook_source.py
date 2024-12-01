from abc import ABC, abstractmethod


class BaseRunbookSourceManager(ABC):
    """
    Abstract base class for Runbook sources.
    This class defines the basic structure for handling runbook operations
    such as listening for changes from the source (e.g., webhook, polling),
    and processing the changes (e.g., update, delete).
    """

    @abstractmethod
    def start(self):
        """
        Set up the mechanism to listen for changes from the source (e.g., webhook listener, polling).
        This method will typically run in a background process or a separate thread.

        :return: None
        """
        pass
