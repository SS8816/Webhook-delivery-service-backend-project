import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import DeliveryLog
import logging

async def delete_old_logs():
    while True:
        try:
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=72)

            deleted_count = db.query(DeliveryLog).filter(DeliveryLog.timestamp < cutoff_time).delete()
            db.commit()

            logging.info(f"[Retention] Deleted {deleted_count} delivery logs older than 72 hours.")
        except Exception as e:
            logging.error(f"[Retention] Error deleting old logs: {str(e)}")
        finally:
            db.close()

        await asyncio.sleep(3600)  # Run once every hour
