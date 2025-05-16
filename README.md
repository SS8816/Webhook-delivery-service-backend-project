# Webhook Delivery Service Backend

Welcome to the **Webhook Delivery Service Backend**! This backend service provides a robust solution for managing webhook subscriptions, processing asynchronous webhook deliveries, logging delivery attempts, and handling retries.

---

## Project Overview
This backend handles webhook delivery requests, tracks delivery status, and offers retry mechanisms for failed deliveries. It utilizes **FastAPI** for building the API, **Celery** for task queuing, **Redis** for caching, and a **PostgreSQL** or **SQLite** database to store subscription and delivery information.

---

## Key Features
- **Webhook Subscription Management**: Users can create and manage webhook subscriptions.
- **Asynchronous Webhook Delivery**: Webhooks are delivered asynchronously with retry logic in case of failure.
- **Delivery Logging**: All delivery attempts, their outcomes, and timestamps are logged.
- **Redis Caching**: Caches subscription lookups to optimize performance.
- **Log Retention**: Delivery logs older than 72 hours are automatically deleted to save storage.

---

## Architecture Choices

- **FastAPI**: Chosen for its high performance and ease of use for building RESTful APIs.
- **Celery**: Used for background task processing, especially for handling asynchronous delivery retries.
- **Redis**: Serves as a task queue and cache, improving the scalability and performance of webhook deliveries.
- **PostgreSQL**: A relational database to store subscriptions and delivery logs, ensuring consistency.
- **Retry Strategy**: In case of a failed webhook delivery, the service retries the delivery up to a specified maximum number of attempts, with exponential backoff.
- **Docker**: Ensures the service can be easily containerized and run on any environment.

---

## Database Schema & Indexing

### Database Schema

The schema consists of two main tables:

1. **Subscriptions Table**:
   - `id`: Primary key (UUID or auto-incremented ID)
   - `url`: The URL where webhooks will be delivered.
   - `event_type`: The type of event triggering the webhook (e.g., `user_signup`).

2. **Delivery Logs Table**:
   - `id`: Primary key (UUID or auto-incremented ID)
   - `subscription_id`: Foreign key linking to the `subscriptions` table.
   - `status`: Delivery status (e.g., `delivered`, `failed`).
   - `attempts`: The number of attempts made to deliver the webhook.
   - `timestamp`: Timestamp of when the delivery was attempted.
   
### Indexing Strategy

- Indexes are created on:
  - `subscription_id` for fast lookups of delivery logs by subscription.
  - `status` for filtering deliveries by outcome (e.g., failed deliveries).
  - `timestamp` for quick access to recent logs and cleanup of old logs.

---

## Setup Instructions

### Prerequisites
- **Docker**: Make sure you have Docker installed. If not, download and install from [here](https://www.docker.com/get-started).
- **Python 3.x**: If not using Docker, Python 3.x is required for local development.

### Running the Application Locally Using Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/webhook-delivery-service.git
   cd webhook-delivery-service
2. Build and run Docker containers:
      docker-compose up --build
      This will:
         - Build the necessary images.
         -Start the application, Redis, and Celery worker in containers.

3. Access the application:
   Once the containers are running, you can access the API at http://localhost:8000.

4. Access logs:
   Logs are stored inside the logs/ directory within the project folder.


## API Endpoints
**Here are some example cURL commands demonstrating how to interact with the API:**

1. Create Subscription
   Create a new subscription that will receive webhooks.

   curl -X POST "http://localhost:8000/subscriptions/" -H "Content-Type: application/json" -d      '{"url": "https://webhook.example.com", "event_type": "user_signup"}'

2. List Subscriptions
   Retrieve all subscriptions.
   
   curl -X GET "http://localhost:8000/subscriptions/"

3. Deliver Webhook
   Manually trigger a webhook delivery.
   
   curl -X POST "http://localhost:8000/deliveries/" -H "Content-Type: application/json" -d         '{"subscription_id": 1, "payload": {"user_id": 123, "event": "signup"}}'
   
4. View Delivery Logs
   Check the status of a specific delivery attempt.

   curl -X GET "http://localhost:8000/logs/abc123/"

5. Delete Old Logs
   Clean up logs older than 72 hours.

   curl -X DELETE "http://localhost:8000/logs/old/"


## Cost Estimation for Deployed Solution
Assumptions:

Average of 5000 webhooks ingested per day.

Each webhook has an average of 1.2 delivery attempts.

The application is deployed on the AWS Free Tier.

AWS Free Tier Costs:
EC2 Instance: A t2.micro instance is eligible for the free tier, which provides 750 hours per month.

Cost: $0 (within free tier limits).

RDS (PostgreSQL): A db.t2.micro instance is eligible for the free tier with 750 hours per month.

Cost: $0 (within free tier limits).

Redis: The free tier provides 750 hours per month for ElastiCache.

Cost: $0 (within free tier limits).

S3 for Logs: Assuming logs are minimal, using S3 for log storage may incur low costs, especially under 5GB of data.

Cost: $0 for small-scale usage.

Estimated Monthly Cost:

Assuming everything remains within the AWS Free Tier, the estimated monthly cost is $0.

## Credits
FastAPI: FastAPI framework for building high-performance APIs.

Celery: Celery for background task management and retries.

Redis: Redis for task queueing and caching.

Docker: Docker for containerization.

Uvicorn: ASGI server for running the FastAPI application.

PostgreSQL: Relational database for storing subscriptions and logs.

Docker Compose: For the orchestration of multiple containers.

## Deployment 
I apologize, I didn't have enough time to deploy it.
