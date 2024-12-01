from pydantic import BaseModel
from typing import Dict
from dataclasses import dataclass


class WebhookData(BaseModel):
    id: str
    name: str
    operationName: str
    statusCode: int
    resourceId: str
    properties: Dict  # You can specify a more detailed type for properties if necessary

    class Config:
        # Ensure that any extra fields are ignored (useful for flexibility)
        extra = "ignore"


@dataclass
class WebhookConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str
    resource_group: str
    automation_account: str
    webhook_endpoint_url: str
    webhook_name: str = "automation-webhook"
