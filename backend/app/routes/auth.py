"""
Simplified demo authentication (spec section 14): a full auth system would
add complexity out of proportion to an MVP demo, so this issues one static
bearer token for a hardcoded demo account. Swap in real auth (OAuth2 /
JWT-per-user) before ever deploying this beyond a local demo.
"""
from fastapi import APIRouter, Header, HTTPException, status

from app.config import DEMO_USER_EMAIL, DEMO_USER_PASSWORD, DEMO_TOKEN
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if payload.email.strip().lower() != DEMO_USER_EMAIL.lower() or payload.password != DEMO_USER_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo credentials")
    return LoginResponse(access_token=DEMO_TOKEN, user_email=DEMO_USER_EMAIL)


def require_demo_auth(authorization: str | None = Header(default=None)) -> str:
    """FastAPI dependency: expects `Authorization: Bearer <DEMO_TOKEN>`."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != DEMO_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return token
