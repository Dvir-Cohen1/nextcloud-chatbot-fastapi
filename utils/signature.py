import hmac
import hashlib

def verify_signature(secret_key: str, random_value: str, body: bytes, signature: str) -> bool:
    expected_signature = hmac.new(
        key=secret_key.encode(),
        msg=(random_value + body.decode()).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def sign_message(shared_secret, message, random_header):
    random_header_bytes = random_header.encode('utf-8')
    shared_secret_bytes = shared_secret.encode('utf-8')
    signature = hmac.new(shared_secret_bytes, digestmod=hashlib.sha256)
    signature.update(random_header_bytes)
    signature.update(message.encode('utf-8'))
    
    return signature.hexdigest()