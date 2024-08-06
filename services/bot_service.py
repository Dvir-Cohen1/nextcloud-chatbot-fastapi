from fastapi import HTTPException
from config import SECRET_KEY, NEXTCLOUD_URL
from utils.signature import sign_message
import os
import json
import httpx
from logging_config import setup_logger
from typing import Dict
import hashlib
import time

logger = setup_logger(__name__)

# In-memory store for conversation states
conversation_state: Dict[str, str] = {}

async def send_message(token: str, message_data: dict, random_value: str):
    request_body = json.dumps(message_data)
    digest = sign_message(SECRET_KEY, message_data.get("message"), random_value)

    # Generate a unique referenceId using a combination of message content and current time
    reference_id = hashlib.sha256(f"{message_data.get('message')}{time.time()}".encode()).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'X-Nextcloud-Talk-Bot-Random': random_value,
        'X-Nextcloud-Talk-Bot-Signature': digest,
        'OCS-APIRequest': 'true',
    }

    # Include the referenceId in the message data
    message_data['referenceId'] = reference_id

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/bot/{token}/message",
            data=request_body,
            headers=headers,
            timeout=60
        )

    if response.status_code == 201:
        return {"status": "message sent", "referenceId": reference_id}
    else:
        error_message = f"Failed with status code {response.status_code}: {response.text}"
        logger.error(f"Error sending message: {error_message}")
        raise HTTPException(status_code=response.status_code, detail=error_message)

async def handle_user_message(actor_info, object_info, target_info, message_text, random_value):
    user_name = actor_info.get("name")
    target_id = target_info.get("id")

    if not user_name or not target_id:
        raise HTTPException(status_code=400, detail="Missing user or target information")

    if not message_text:
        logger.error("Received a None message_text. Unable to process the request.")
        error_message = {
            "message": "I didn't receive any valid message. Please try again.",
            "replyTo": target_id,
            'silent': False,
        }
        await send_message(target_id, error_message, random_value)
        return

    state = conversation_state.get(target_id)
    logger.info(f"Current state for target_id {target_id}: {state}")
    logger.info(f"Received message: {message_text}")

    if not state:
        initial_message = {
            "message": f"Hello {user_name}, what would you like to do today?",
            "replyTo": target_id,
            "options": ["deposit", "withdraw"],
            'silent': False,
        }
        await send_message(target_id, initial_message, random_value)
        conversation_state[target_id] = "waiting_for_action"
    elif state == "waiting_for_action":
        user_choice = message_text.strip().lower()
        logger.info(f"User choice: {user_choice}")

        if user_choice in ["deposit", "withdraw"]:
            follow_up_message = {
                "message": "Please enter account number and brand.",
                "replyTo": target_id,
                'silent': False,
            }
            await send_message(target_id, follow_up_message, random_value)
            conversation_state[target_id] = "waiting_for_details"
        else:
            error_message = {
                "message": "I didn't understand that. Please choose 'deposit' or 'withdraw'.",
                "replyTo": target_id,
                'silent': False,
            }
            await send_message(target_id, error_message, random_value)
    elif state == "waiting_for_details":
        try:
            account_number, brand = message_text.split(",")
            final_message = {
                "message": "Your operation was successful.",
                "replyTo": target_id,
                'silent': False,
            }
            await send_message(target_id, final_message, random_value)
            # Reset the conversation state for this target_id
            conversation_state[target_id] = None
        except ValueError:
            error_message = {
                "message": "Invalid format. Please enter in the format 'acnumber,brand'.",
                "replyTo": target_id,
                'silent': False,
            }
            await send_message(target_id, error_message, random_value)
    else:
        # Reset the conversation state if it falls into an unknown state
        conversation_state[target_id] = None
