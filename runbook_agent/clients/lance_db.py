# app/lancedb_client.py
import lancedb
import threading
from runbook_agent.config import init_config
from datetime import timedelta

cfg = init_config()


class LanceDBClientSingleton:
    """
    Singleton to manage a shared LanceDB client across threads.
    Ensures that only one instance of the client is created and shared.
    """

    _instance = None
    _lock = threading.Lock()  # Lock to ensure thread-safe singleton creation

    def __new__(cls):
        # If the instance doesn't exist, create one
        if cls._instance is None:
            with cls._lock:  # Ensure thread safety during initialization
                if (
                    cls._instance is None
                ):  # Double check in case another thread initialized it first
                    cls._instance = lancedb.connect(
                        cfg.lance.db_uri, read_consistency_interval=timedelta(minutes=5)
                    )
        return cls._instance

    def __init__(self):
        pass  # No need to initialize anything here

    def get_client(self):
        """
        Returns the shared LanceDB client instance.
        """
        return self._instance


# Global LanceDB client singleton
lancedb_client = LanceDBClientSingleton()
