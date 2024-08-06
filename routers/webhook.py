from fastapi import APIRouter, Request, HTTPException
from config import SECRET_KEY
from utils.signature import verify_signature
from utils.extraction import extract_actor, extract_object, extract_target
import json
from logging_config import setup_logger
from .bot import send_message

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Nextcloud-Talk-Signature")
    random_value = request.headers.get("X-Nextcloud-Talk-Random")
    print(random_value)
    if not signature or not random_value:
        raise HTTPException(status_code=400, detail="Missing headers")

    body = await request.body()

    if not verify_signature(SECRET_KEY, random_value, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        data = json.loads(body.decode())
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = data.get("type")
    actor_info = extract_actor(data)
    object_info = extract_object(data)
    target_info = extract_target(data)

    logger.info(f"Event Type: {event_type}")
    logger.info(f"Actor Info: {actor_info}")
    logger.info(f"Object Info: {object_info}")
    logger.info(f"Target Info: {target_info}")

    user_name = actor_info.get("name")
    user_id = actor_info.get("id")
    target_id = target_info.get("id")
    
    object_id = object_info.get("id")

    message = {
        "message": f"How are you, {user_name}?",
        "replyTo": target_id,
        "referenceId": object_id,
        'silent': False,  

    }

    try:
        await send_message(target_id, message,random_value)
        logger.info(f"Sent message to {user_name} in chat {target_id}")
    except HTTPException as e:
        logger.error(f"Failed to send message: {e.detail}")

    return {"status": "ok"}