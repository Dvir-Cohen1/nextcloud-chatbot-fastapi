from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import hmac
import hashlib
import os
import json
import httpx
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from a .env file
load_dotenv()

# Environment variables
SECRET_KEY = os.getenv("NEXTCLOUD_BOT_SECRET")
NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"bot_status": "active"}

@app.post("/webhook")
async def webhook(request: Request):
    print("Received message: ")
     
    # Extract headers
    signature = request.headers.get("X-Nextcloud-Talk-Signature")
    random_value = request.headers.get("X-Nextcloud-Talk-Random")
    
    if not signature or not random_value:
        raise HTTPException(status_code=400, detail="Missing headers")

    # Read the request body
    body = await request.body()
    
    # Validate the signature
    expected_signature = hmac.new(
        key=SECRET_KEY.encode(),
        msg=(random_value + body.decode()).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Process the message
    # For example, log or handle the message
    print(f"Received message: {body.decode()}")

    return {"status": "ok"}

@app.post("/bot/{token}/message")
async def send_message(token: str, message: dict):
    random = os.urandom(16).hex()
    signature = hmac.new(
        key=SECRET_KEY.encode(),
        msg=f"{random}{json.dumps(message)}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {
        "X-Nextcloud-Talk-Bot-Random": random,
        "X-Nextcloud-Talk-Bot-Signature": signature,
        "OCS-APIRequest": "true"
    }

    # Send message to Nextcloud
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/message",
            json=message,
            headers=headers
        )

    if response.status_code == 201:
        return {"status": "message sent"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/bot/{token}/reaction/{messageId}")
async def react_to_message(token: str, messageId: str, reaction: str):
    random = os.urandom(16).hex()
    signature = hmac.new(
        key=SECRET_KEY.encode(),
        msg=f"{random}{{\"reaction\": \"{reaction}\"}}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {
        "X-Nextcloud-Talk-Bot-Random": random,
        "X-Nextcloud-Talk-Bot-Signature": signature,
        "OCS-APIRequest": "true"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/reaction/{messageId}",
            json={"reaction": reaction},
            headers=headers
        )

    if response.status_code == 201:
        return {"status": "reaction added"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
