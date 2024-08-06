from fastapi import APIRouter, HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils.signature import sign_message
import os
import json
import httpx
from logging_config import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/bot/{token}/message")
async def send_message(token: str, message_data: dict, random_value: str):
    request_body = json.dumps(message_data)
    digest = sign_message(SECRET_KEY, message_data.get("message"), random_value)

    headers = {
        'Content-Type': 'application/json',
        'X-Nextcloud-Talk-Bot-Random': random_value,
        'X-Nextcloud-Talk-Bot-Signature': digest,
        'OCS-APIRequest': 'true',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/message",
            data=request_body,
            headers=headers,
            timeout=60
        )

    if response.status_code == 200:
        return {"status": "message sent"}
    else:
        error_message = f"Failed with status code {response.status_code}: {response.text}"
        logger.error(f"Error sending message: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)

@router.post("/bot/{token}/reaction/{messageId}")
async def react_to_message(token: str, messageId: str, reaction: str):
    random_value = os.urandom(16).hex()
    payload = json.dumps({"reaction": reaction})
    signature = sign_message(SECRET_KEY, payload, random_value)

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

