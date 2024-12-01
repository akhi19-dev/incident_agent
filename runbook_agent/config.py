# Import required modules
from dotenv import load_dotenv
from easydict import EasyDict as edict
from typing import Any
import os

# Load environment variables from the .env file
load_dotenv()


def init_config() -> edict[Any]:
    cfg = edict()
    cfg.openai = edict()
    cfg.openai.API_KEY = os.getenv("OPENAI_API_KEY")
    # Azure
    cfg.azure = edict()
    cfg.azure.tenant_id = os.getenv("AZURE_TENANT_ID", "default_tenant_id")
    cfg.azure.openai_api_key = os.getenv("OPENAI_API_KEY", "default_openai_api_key")
    cfg.azure.client_id = os.getenv("AZURE_CLIENT_ID", "default_client_id")
    cfg.azure.client_secret = os.getenv("AZURE_CLIENT_SECRET", "default_client_secret")
    cfg.azure.subscription_id = os.getenv(
        "AZURE_SUBSCRIPTION_ID", "default_subscription_id"
    )
    cfg.azure.resource_group = os.getenv(
        "AZURE_RESOURCE_GROUP", "default_resource_group"
    )
    cfg.azure.automation_account = os.getenv(
        "AZURE_AUTOMATION_ACCOUNT", "default_automation_account"
    )
    cfg.azure.webhook_endpoint = os.getenv(
        "AZURE_RUNBOOK_WEBHOOK_ENDPOINT", "default_webhook_endpoint"
    )
    cfg.azure.webhook_name = os.getenv(
        "AZURE_RUNBOOK_WEBHOOK_NAME", "default_webhook_name"
    )

    # AWS
    cfg.aws = edict()
    cfg.aws.access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    cfg.aws.secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    cfg.aws.region = os.getenv("AWS_REGION")
    # LanceDB
    cfg.lance = edict()
    cfg.lance.db_uri = os.getenv("LANCE_DB_URI")
    return cfg
