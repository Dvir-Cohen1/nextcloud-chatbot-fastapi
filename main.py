from fastapi import FastAPI
from routers import webhook, bot
from logging_config import setup_logger

# Initialize FastAPI app & Logger
app = FastAPI()
logger = setup_logger(__name__)

# Include routers
app.include_router(webhook.router)
app.include_router(bot.router)

@app.get("/")
def home():
    return {"bot_status": "active"}
