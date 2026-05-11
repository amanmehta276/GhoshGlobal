import os, jwt, datetime
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY    = os.getenv("SECRET_KEY", "change-this-in-production-please")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ghosh@admin123")
ALGORITHM     = "HS256"
TOKEN_EXPIRE_HOURS = 12

security = HTTPBearer()

def create_token() -> str:
    """Create a JWT token valid for TOKEN_EXPIRE_HOURS hours."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": "admin", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(password: str) -> bool:
    return password == ADMIN_PASSWORD

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """FastAPI dependency — call this on any protected route."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
