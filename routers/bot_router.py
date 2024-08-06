from fastapi import APIRouter, Request, HTTPException
from services.bot_service import handle_user_message
from utils.signature import verify_signature
from utils.extraction import extract_actor, extract_object, extract_target
import json
from config import SECRET_KEY

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
    actor_info = extract_actor(data)
    object_info = extract_object(data)
    target_info = extract_target(data)
    # message_text = data.get("message")

    content_data = object_info.get("content", "{}")
    message_text = content_data.get("message")

    # Handle user message
    try:
        await handle_user_message(actor_info, object_info, target_info, message_text, random_value)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    return {"status": "ok"}
