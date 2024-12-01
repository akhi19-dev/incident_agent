import boto3
import threading
from runbook_agent.config import init_config

cfg = init_config()


class BedrockClientSingleton:
    """
    Singleton to manage a shared Boto3 Bedrock runtime client across threads.
    Ensures that only one instance of the client is created and shared.
    """

    _instance = None
    _lock = threading.Lock()  # Lock to ensure thread-safe singleton creation

    def __new__(cls):
        # If the instance doesn't exist, create one
        if cls._instance is None:
            with cls._lock:  # Ensure thread safety during initialization
                if (
                    cls._instance is None and cls._is_valid_aws_config()
                ):  # Double check in case another thread initialized it first
                    cls._instance = boto3.client(
                        "bedrock-runtime",
                        aws_access_key_id=cfg.aws.access_key_id,
                        aws_secret_access_key=cfg.aws.secret_access_key,
                        region_name=cfg.aws.region,
                    )
        return cls._instance

    @staticmethod
    def _is_valid_aws_config():
        """Checks if the AWS configuration has the required values and they are not empty."""
        aws_config = cfg.aws
        return (
            aws_config.get("access_key_id") != ""
            and aws_config.get("secret_access_key") != ""
            and aws_config.get("region") != ""
        )

    def __init__(self):
        pass  # No need to initialize anything here

    def get_client(self):
        """
        Returns the shared Bedrock client instance.
        """
        return self._instance


# Global Bedrock client singleton
bedrock_runtime_client = BedrockClientSingleton()
