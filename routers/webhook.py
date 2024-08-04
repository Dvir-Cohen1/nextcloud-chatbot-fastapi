from fastapi import APIRouter, Request, HTTPException
from config import SECRET_KEY
from utils import verify_signature

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Nextcloud-Talk-Signature")
    random_value = request.headers.get("X-Nextcloud-Talk-Random")

    if not signature or not random_value:
        raise HTTPException(status_code=400, detail="Missing headers")

    body = await request.body()

    if not verify_signature(SECRET_KEY, random_value, body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Process the message (implement your custom logic here)
    message = body.decode()
    print(f"Received message: {message}")

    return {"status": "ok"}
