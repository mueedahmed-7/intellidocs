"""
FastAPI dependency that reads the "Authorization: Bearer <token>" header,
validates the JWT, and returns the logged-in user's id.
Use this on any endpoint that should require the user to already be
logged in (e.g. "set up face login").
"""

from fastapi import Header, HTTPException
from jose import JWTError

from utils.jwt_handler import decode_access_token


def get_current_user_id(authorization: str = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header.",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        user_id = decode_access_token(token)
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please log in again.",
        )

    return user_id
