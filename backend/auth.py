"""Short lived, signed citizen access tokens for API ownership checks."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import Citizen

REQUIRE_CITIZEN_AUTH = os.getenv(
    "REQUIRE_CITIZEN_AUTH",
    "true" if os.getenv("VERCEL") or os.getenv("APP_ENV", "").lower() == "production" else "false",
).lower() in {"1", "true", "yes", "on"}
_LOCAL_SECRET = secrets.token_bytes(32)
_bearer = HTTPBearer(auto_error=False)


def _secret() -> bytes:
    configured = os.getenv("CITIZEN_TOKEN_SECRET", "")
    if configured:
        return configured.encode("utf-8")
    fallback = os.getenv("VERCEL_GIT_COMMIT_SHA") or os.getenv("SECRET_KEY")
    if fallback:
        return hashlib.sha256(fallback.encode("utf-8")).digest()
    return _LOCAL_SECRET


def issue_access_token(citizen_id: str, expires_in: int = 60 * 60 * 12) -> str:
    payload = json.dumps({"sub": citizen_id, "exp": int(time.time()) + expires_in}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(_secret(), encoded, hashlib.sha256).digest()
    return encoded.decode() + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode()


def get_current_citizen(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Optional[Citizen]:
    if not REQUIRE_CITIZEN_AUTH:
        return None
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Citizen sign-in is required.", headers={"WWW-Authenticate": "Bearer"})
    try:
        encoded, supplied_signature = credentials.credentials.split(".", 1)
        expected = hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest()
        signature = base64.urlsafe_b64decode(supplied_signature + "=" * (-len(supplied_signature) % 4))
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        payload_bytes = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        payload = json.loads(payload_bytes)
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired token")
        citizen_id = str(payload["sub"])
    # pyrefly: ignore[unreachable-except-clause]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Citizen session is invalid or expired.", headers={"WWW-Authenticate": "Bearer"})

    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if citizen is None:
        raise HTTPException(status_code=401, detail="Citizen session is no longer valid.")
    return citizen


def ensure_citizen_owner(citizen_id: str, current: Optional[Citizen]) -> None:
    if REQUIRE_CITIZEN_AUTH and (current is None or current.id != citizen_id):
        raise HTTPException(status_code=403, detail="You may only access your own citizen record.")
