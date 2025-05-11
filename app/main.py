import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,  # Set the minimum level of logging (INFO, DEBUG, ERROR, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Logging setup is working!")
from fastapi import FastAPI
from app.routes import subscriptions
from app.routes import ingest
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import ingest

app = FastAPI()

# Include your subscriptions route
app.include_router(subscriptions.router)
app.include_router(ingest.router) 

@app.get("/health")
def read_health():
    return {"status": "ok"}
@app.get("/items")
def read_item():
    return {"item": "example"}

from app.retention import delete_old_logs
@app.on_event("startup")
async def start_retention_task():
    asyncio.create_task(delete_old_logs())


from app.routes import status  # if you created a separate status.py

app.include_router(status.router)
app.mount("/", StaticFiles(directory="templates", html=True), name="static")