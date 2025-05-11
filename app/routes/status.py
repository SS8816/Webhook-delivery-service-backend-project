from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import SessionLocal
from app.models import DeliveryLog

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status/{task_id}")
async def get_task_status(task_id: UUID, db: Session = Depends(get_db)):
    logs = db.query(DeliveryLog).filter(DeliveryLog.task_id == task_id).order_by(DeliveryLog.attempt_number).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No delivery logs found for this task ID")
    return logs
