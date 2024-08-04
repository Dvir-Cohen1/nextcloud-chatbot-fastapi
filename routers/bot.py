from fastapi import APIRouter, HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils.signature import generate_signature
import os
import json
import httpx
from logging_config import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/bot/{token}/message")
async def send_message(token: str, message: dict):
    random_value = os.urandom(16).hex()
    payload = json.dumps(message)
    signature = generate_signature(SECRET_KEY, random_value, payload)

    headers = {
        "X-Nextcloud-Talk-Bot-Random": random_value,
        "X-Nextcloud-Talk-Bot-Signature": signature,
        "HTTP_X_NEXTCLOUD_TALK_BACKEND": NEXTCLOUD_URL,
        "OCS-APIRequest": "true",
        "Content-Type":"application/json",
        "Accept":"application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/message",
            json=message,
            headers=headers
        )

    if response.status_code == 201:
        return {"status": "message sent"}
    else:
        error_message = f"Failed with status code {response.status_code}: {response.text}"
        logger.error(f"Error sending message: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)

@router.post("/bot/{token}/reaction/{messageId}")
async def react_to_message(token: str, messageId: str, reaction: str):
    random_value = os.urandom(16).hex()
    payload = json.dumps({"reaction": reaction})
    signature = generate_signature(SECRET_KEY, random_value, payload)

    headers = {
        "X-Nextcloud-Talk-Random": random_value,
        "X-Nextcloud-Talk-Signature": signature,
        "HTTP_X_NEXTCLOUD_TALK_BACKEND": NEXTCLOUD_URL,
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
        error_message = f"Failed with status code {response.status_code}: {response.text}"
        logger.error(f"Error adding reaction: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)
