from fastapi import APIRouter, Request, HTTPException
from config import SECRET_KEY

from services.bot_service import send_message
from utils.signature import verify_signature
from utils.extraction import extract_actor, extract_object, extract_target
import json
from logging_config import setup_logger


logger = setup_logger(__name__)
router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    # Extract headers and verify presence
    signature = request.headers.get("X-Nextcloud-Talk-Signature")
    random_value = request.headers.get("X-Nextcloud-Talk-Random")
    if not signature or not random_value:
        raise HTTPException(status_code=400, detail="Missing signature or random value headers")

    # Read and verify request body
    body = await request.body()
    if not verify_signature(SECRET_KEY, random_value, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse the JSON body
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Extract relevant information
    event_type = data.get("type")
    actor_info = extract_actor(data)
    object_info = extract_object(data)
    target_info = extract_target(data)

    logger.info(f"Event Type: {event_type}")
    logger.info(f"Actor Info: {actor_info}")
    logger.info(f"Object Info: {object_info}")
    logger.info(f"Target Info: {target_info}")

    # Prepare message data
    user_name = actor_info.get("name")
    target_id = target_info.get("id")

    message = {
        "message": f"How are you, {user_name}?",
        "replyTo": target_id,
        'silent': False,
    }

    # Send the message
    try:
        await send_message(target_id, message, random_value)
        logger.info(f"Sent message to {user_name} in chat {target_id}")
    except HTTPException as e:
        logger.error(f"Failed to send message: {e.detail}")
        raise

    return {"status": "ok"}
