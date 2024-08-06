from fastapi import HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils.signature import sign_message
import json
import httpx
from logging_config import setup_logger
from typing import Dict
import hashlib
import time

logger = setup_logger(__name__)

# In-memory store for conversation states
conversation_state: Dict[str, str] = {}

async def send_message(token: str, message: str, random_value: str, reply_to: str = None):
    message_data = {
        "message": message,
        "replyTo": reply_to,
        "silent": False,
        "referenceId": hashlib.sha256(f"{message}{time.time()}".encode()).hexdigest(),
    }

    request_body = json.dumps(message_data)
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
            data=request_body,
            headers=headers,
            timeout=60
        )

    if response.status_code != 201:
        error_message = f"Failed to send message with status code {response.status_code}: {response.text}"
        logger.error(error_message)
        raise HTTPException(status_code=response.status_code, detail=error_message)

    return {"status": "message sent", "referenceId": message_data["referenceId"]}

async def handle_user_message(actor_info, target_info, message_text, random_value):
    user_name = actor_info.get("name")
    target_id = target_info.get("id")

    if not user_name or not target_id:
        raise HTTPException(status_code=400, detail="Missing user or target information")

    if not message_text:
        error_message = "I didn't receive any valid message. Please try again."
        logger.error(error_message)
        await send_message(target_id, error_message, random_value)
        return

    state = conversation_state.get(target_id)
    logger.info(f"Current state for target_id {target_id}: {state}")
    logger.info(f"Received message: {message_text}")

    if state is None:
        await start_conversation(user_name, target_id, random_value)
    elif state == "waiting_for_action":
        await handle_action_selection(target_id, message_text, random_value)
    elif state == "waiting_for_details":
        await handle_details_provided(target_id, message_text, random_value)
    else:
        conversation_state[target_id] = None

async def start_conversation(user_name: str, target_id: str, random_value: str):
    message = f"Hello {user_name}, what would you like to do today? 'deposit' or 'withdraw'"
    await send_message(target_id, message, random_value, reply_to=target_id)
    conversation_state[target_id] = "waiting_for_action"

async def handle_action_selection(target_id: str, message_text: str, random_value: str):
    user_choice = message_text.strip().lower()
    if user_choice in ["deposit", "withdraw"]:
        message = "Please enter account number and brand."
        await send_message(target_id, message, random_value)
        conversation_state[target_id] = "waiting_for_details"
    else:
        error_message = "I didn't understand that. Please choose 'deposit' or 'withdraw'."
        await send_message(target_id, error_message, random_value)

async def handle_details_provided(target_id: str, message_text: str, random_value: str):
    try:
        account_number, brand = message_text.split(",")
        # Perform side effects or operations here
        success_message = "Your operation was successful."
        await send_message(target_id, success_message, random_value)
        # Reset the conversation state for the next interaction
        conversation_state[target_id] = None
    except ValueError:
        error_message = "Invalid format. Please enter in the format 'acnumber,brand'."
        await send_message(target_id, error_message, random_value)
