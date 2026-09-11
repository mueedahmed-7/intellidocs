from datetime import datetime, timedelta, timezone

from jose import jwt

from backend.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


def create_access_token(
    user_id: str,
):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token


def decode_access_token(token: str) -> str:
    """
    Decodes a JWT and returns the user_id (the 'sub' claim).
    Raises jose.JWTError (or subclasses like ExpiredSignatureError)
    on any invalid/expired token — callers should catch that.
    """
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise KeyError("Token is missing its subject claim.")
    return user_id
