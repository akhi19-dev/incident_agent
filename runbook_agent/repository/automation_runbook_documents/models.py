from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AutomationRunbookDocumentModel(BaseModel):
    id: Optional[str] = None  # Unique identifier for the runbook
    name: Optional[str] = None  # Name of the runbook
    source: Optional[str] = (
        None  # Source from where the runbook originated (e.g., Azure, GitHub)
    )
    published_time: Optional[datetime] = (
        None  # Date and time when the runbook was published
    )
    is_indexed: Optional[bool] = None  # Flag to indicate whether the runbook is indexed
    description: Optional[str] = (
        None  # Description of the runbook's purpose and functionality
    )
    os_supported: Optional[List[str]] = (
        None  # List of operating systems supported by the runbook
    )
    args: Optional[List[str]] = None
    created_time: Optional[datetime] = None  # Timestamp when the runbook was created
    updated_time: Optional[datetime] = (
        None  # Timestamp when the runbook was last updated
    )
    type: Optional[str] = None  # Type of the runbook (e.g., Python, PowerShell)
    tags: Optional[List[str]] = (
        None  # Tags associated with the runbook for categorization
    )

    class Config:
        # Custom configuration for serializing datetime objects to ISO format
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Ensures datetime is serialized in ISO format
        }
