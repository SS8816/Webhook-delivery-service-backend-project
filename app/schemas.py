from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime

# Request model
class SubscriptionCreate(BaseModel):
    target_url: HttpUrl
    secret: Optional[str] = None
    event_types: Optional[List[str]] = None

# Response model
class SubscriptionOut(BaseModel):
    id: UUID
    target_url: HttpUrl
    secret: Optional[str]
    event_types: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DeliveryLogOut(BaseModel):
    id: int
    subscription_id: UUID
    task_id: UUID
    attempt_number: int
    status: str
    http_status: Optional[int]
    error: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime

    class Config:
        orm_mode = True

# Used for webhook ingestion
class WebhookPayload(BaseModel):
    payload: Dict[str, Any]
