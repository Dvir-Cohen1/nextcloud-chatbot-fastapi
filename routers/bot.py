from fastapi import APIRouter, HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils.signature import generate_signature
import os
import json
import httpx
from logging_config import setup_logger
import random
import string
import hmac
import hashlib

router = APIRouter()
logger = setup_logger(__name__)

# @router.post("/bot/{token}/message")
async def send_message(token: str, message_data: dict,random_value:str):

    # random_value = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))  # Generate a random value
    # random_value = os.urandom(16).hex()
    # payload = json.dumps(message)
    # signature = generate_signature(SECRET_KEY, random_value, payload)


    request_body = json.dumps(message_data)

    message = message_data.get("message", "")
    digest = sign_message(SECRET_KEY, message, random_value)

    headers = {
    'Content-Type': 'application/json',
    'X-Nextcloud-Talk-Bot-Random': random_value,
    'X-Nextcloud-Talk-Bot-Signature': digest,
    'OCS-APIRequest': 'true',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/message",
            json=request_body,
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








# --------------------------------------------------------------
def sign_message(shared_secret, message, random_header):
    random_header_bytes = random_header.encode('utf-8')
    shared_secret_bytes = shared_secret.encode('utf-8')
    signature = hmac.new(shared_secret_bytes, digestmod=hashlib.sha256)
    signature.update(random_header_bytes)
    signature.update(message.encode('utf-8'))
    
    return signature.hexdigest()
