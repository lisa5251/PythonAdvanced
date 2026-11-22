import base64
import hashlib
import hmac
import json
import os
import time


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing from .env")


def _encode_segment(value: dict) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode()


def create_access_token(user_id: int) -> str:
    header = _encode_segment({"alg": "HS256", "typ": "JWT"})
    payload = _encode_segment({
        "sub": str(user_id),
        "exp": int(time.time()) + 3600,
    })
    signing_input = f"{header}.{payload}".encode()
    signature = hmac.new(
        SECRET_KEY.encode(),
        signing_input,
        hashlib.sha256,
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header}.{payload}.{encoded_signature}"
