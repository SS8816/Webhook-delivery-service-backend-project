from celery import Celery
import redis
from app.utils import deliver_webhook
from app.db import get_db
from app.models import Subscription
from sqlalchemy.orm import sessionmaker
from app.database import SessionLocal

# Configure Celery to use Redis as the broker and result backend
celery_app = Celery(
    'webhook_delivery',
    broker='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
)

# Define task for Celery
@celery_app.task(bind=True)
def deliver_webhook_task(self, subscription_id: str, payload: dict):
    try:
        db = SessionLocal()
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if subscription:
            deliver_webhook(subscription, payload, db)
        db.close()
    except Exception as e:
        self.retry(exc=e)
