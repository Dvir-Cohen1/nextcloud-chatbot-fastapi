from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import webhook, bot

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(webhook.router)
app.include_router(bot.router)

@app.get("/")
def home():
    return {"bot_status": "active"}
