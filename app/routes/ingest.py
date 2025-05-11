from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from uuid import UUID
import hmac
import hashlib

from app.database import SessionLocal
from app.models import Subscription
from app.schemas import WebhookPayload
from app.celery_worker import deliver_webhook_task  # Import Celery task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingest/{subscription_id}", status_code=status.HTTP_202_ACCEPTED)
async def ingest_webhook(
    subscription_id: UUID,
    data: WebhookPayload,
    x_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    # Retrieve the subscription from the database
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Optional: HMAC verification if secret is set
    if subscription.secret:
        if not x_signature:
            raise HTTPException(status_code=400, detail="Missing X-Signature header")

        # Create the expected signature based on the payload and the secret
        payload_bytes = str(data.payload).encode("utf-8")  # Ensure dict is converted safely
        expected_signature = hmac.new(
            key=subscription.secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

        # Compare the expected signature with the provided one
        if not hmac.compare_digest(expected_signature, x_signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Detach the subscription from the session (to avoid passing live session object across threads)
    db.expunge(subscription)

    # Queue the delivery task to Celery
    deliver_webhook_task.apply_async((str(subscription.id), data.payload))

    return {"message": "Webhook received and queued"}
