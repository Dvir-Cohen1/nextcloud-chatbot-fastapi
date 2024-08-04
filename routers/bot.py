from fastapi import APIRouter, HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils import generate_signature
import os
import json
import httpx

router = APIRouter()

@router.post("/bot/{token}/message")
async def send_message(token: str, message: dict):
    random_value = os.urandom(16).hex()
    payload = json.dumps(message)
    signature = generate_signature(SECRET_KEY, random_value, payload)

    headers = {
        "X-Nextcloud-Talk-Bot-Random": random_value,
        "X-Nextcloud-Talk-Bot-Signature": signature,
        "OCS-APIRequest": "true"
    }

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

@router.post("/bot/{token}/reaction/{messageId}")
async def react_to_message(token: str, messageId: str, reaction: str):
    random_value = os.urandom(16).hex()
    payload = json.dumps({"reaction": reaction})
    signature = generate_signature(SECRET_KEY, random_value, payload)

    headers = {
        "X-Nextcloud-Talk-Bot-Random": random_value,
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
