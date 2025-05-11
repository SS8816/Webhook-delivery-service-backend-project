# app/routes/subscriptions.py

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from typing import Optional, List

from app.database import SessionLocal
from app.models import Subscription, DeliveryLog
from app.schemas import SubscriptionCreate, SubscriptionOut, DeliveryLogOut

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new subscription
@router.post("/subscriptions", response_model=SubscriptionOut)
async def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = Subscription(
        id=uuid4(),
        target_url=subscription.target_url,
        secret=subscription.secret,
        event_types=subscription.event_types
    )
    try:
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create subscription: " + str(e))

    return db_subscription

# Get all subscriptions
@router.get("/subscriptions", response_model=List[SubscriptionOut])
async def get_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

# Get a specific subscription by ID
@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionOut)
async def get_subscription(subscription_id: UUID, db: Session = Depends(get_db)):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_subscription:
        return db_subscription
    raise HTTPException(status_code=404, detail="Subscription not found")

# Update a subscription
@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionOut)
async def update_subscription(subscription_id: UUID, subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_subscription:
        db_subscription.target_url = subscription.target_url
        db_subscription.secret = subscription.secret
        db_subscription.event_types = subscription.event_types
        db.commit()
        db.refresh(db_subscription)
        return db_subscription
    raise HTTPException(status_code=404, detail="Subscription not found")

# Delete a subscription
@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: UUID, db: Session = Depends(get_db)):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_subscription:
        db.delete(db_subscription)
        db.commit()
        return {"message": "Subscription deleted"}
    raise HTTPException(status_code=404, detail="Subscription not found")

# Get delivery logs for a subscription
@router.get("/subscriptions/{subscription_id}/deliveries", response_model=List[DeliveryLogOut])
async def get_delivery_logs(
    subscription_id: UUID,
    status: Optional[str] = Query(None, description="Filter by delivery status: success, failure, etc."),
    limit: int = Query(20, description="Max number of logs to return"),
    db: Session = Depends(get_db)
):
    query = db.query(DeliveryLog).filter(DeliveryLog.subscription_id == subscription_id)

    if status:
        query = query.filter(DeliveryLog.status == status)

    logs = query.order_by(DeliveryLog.timestamp.desc()).limit(limit).all()
    return logs
