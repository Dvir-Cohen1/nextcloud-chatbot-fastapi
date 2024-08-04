import hmac
import hashlib

def verify_signature(secret_key: str, random_value: str, body: bytes, signature: str) -> bool:
    expected_signature = hmac.new(
        key=secret_key.encode(),
        msg=(random_value + body.decode()).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def generate_signature(secret_key: str, random_value: str, payload: str) -> str:
    return hmac.new(
        key=secret_key.encode(),
        msg=f"{random_value}{payload}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
