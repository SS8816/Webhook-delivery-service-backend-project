import httpx
import logging
import json
import asyncio
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Subscription, DeliveryLog
from app.db import get_db  # Assuming you have a function to get DB session

async def deliver_webhook(subscription: Subscription, payload: dict, db: Session):
    attempt_number = 1
    max_retries = 5
    backoff_times = [10, 30, 60, 300, 900]  # in seconds

    # Generate a unique task ID for this delivery attempt (including retries)
    task_id = uuid.uuid4()

    try:
        headers = {"Content-Type": "application/json"}

        # If secret is set, include it as a custom header
        if subscription.secret:
            headers["X-Webhook-Secret"] = subscription.secret

        # Log the initial delivery attempt
        log_entry = DeliveryLog(
            task_id=task_id,
            subscription_id=subscription.id,
            attempt_number=attempt_number,
            status="attempting",
            payload=payload,
            timestamp=datetime.utcnow(),
        )
        db.add(log_entry)
        db.commit()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                subscription.target_url,
                content=json.dumps(payload),
                headers=headers,
                timeout=10
            )

            # Log success
            log_entry.status = "success"
            log_entry.http_status = response.status_code
            db.commit()
            logging.info(f"Webhook delivered to {subscription.target_url} with status {response.status_code}")
            return

    except httpx.HTTPError as e:
        logging.error(f"Failed to deliver webhook to {subscription.target_url}: {str(e)}")

        # Update initial attempt as failed
        log_entry.status = "failed_attempt"
        log_entry.error = str(e)
        db.commit()

        # Retry logic
        while attempt_number < max_retries:
            attempt_number += 1
            backoff_time = backoff_times[attempt_number - 2]
            logging.info(f"[Attempt {attempt_number}] Waiting {backoff_time} seconds before retrying...")
            await asyncio.sleep(backoff_time)

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        subscription.target_url,
                        content=json.dumps(payload),
                        headers=headers,
                        timeout=10
                    )

                # Log successful retry
                retry_log = DeliveryLog(
                    task_id=task_id,
                    subscription_id=subscription.id,
                    attempt_number=attempt_number,
                    status="success",
                    http_status=response.status_code,
                    payload=payload,
                    timestamp=datetime.utcnow(),
                )
                db.add(retry_log)
                db.commit()
                logging.info(f"Webhook successfully delivered on attempt {attempt_number}")
                return

            except httpx.HTTPError as retry_error:
                logging.error(f"Attempt {attempt_number} failed: {str(retry_error)}")

                retry_log = DeliveryLog(
                    task_id=task_id,
                    subscription_id=subscription.id,
                    attempt_number=attempt_number,
                    status="failed_attempt",
                    error=str(retry_error),
                    payload=payload,
                    timestamp=datetime.utcnow(),
                )
                db.add(retry_log)
                db.commit()

        # Final failure log after all retries
        final_log = DeliveryLog(
            task_id=task_id,
            subscription_id=subscription.id,
            attempt_number=attempt_number + 1,
            status="failure",
            payload=payload,
            error="Max retries reached",
            timestamp=datetime.utcnow(),
        )
        db.add(final_log)
        db.commit()
        logging.error(f"Max retries reached. Final failure logged for {subscription.target_url}")

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

        error_log = DeliveryLog(
            task_id=task_id,
            subscription_id=subscription.id,
            attempt_number=attempt_number,
            status="failure",
            payload=payload,
            error=str(e),
            timestamp=datetime.utcnow(),
        )
        db.add(error_log)
        db.commit()
