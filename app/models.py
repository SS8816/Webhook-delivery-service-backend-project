# app/models.py
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    BigInteger,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_url = Column(Text, nullable=False)
    secret = Column(Text, nullable=True)
    event_types = Column(ARRAY(Text), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Define relationship to DeliveryLog
    deliveries = relationship("DeliveryLog", back_populates="subscription")

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id = Column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False
    )
    task_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    http_status = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=False)
    timestamp = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Define relationship to Subscription
    subscription = relationship("Subscription", back_populates="deliveries")
