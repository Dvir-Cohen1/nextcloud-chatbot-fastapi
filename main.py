from fastapi import FastAPI
from routers import bot_router
from logging_config import setup_logger

# Initialize FastAPI app & Logger
app = FastAPI()
logger = setup_logger(__name__)

# Include router
app.include_router(bot_router.router)

@app.get("/")
def home():
    return {"bot_status": "active"}
