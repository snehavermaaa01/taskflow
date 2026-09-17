# app/auth.py

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from jose import jwt

from app.database import users_collection
from app.models import SignupRequest, LoginRequest


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# --------------------------------------------------
# PASSWORD SETTINGS
# --------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# --------------------------------------------------
# JWT SETTINGS
# --------------------------------------------------

SECRET_KEY = "taskflow-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# --------------------------------------------------
# PASSWORD HASHING
# --------------------------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# --------------------------------------------------
# CREATE ACCESS TOKEN
# --------------------------------------------------

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@router.post("/signup")
async def signup(data: SignupRequest):

    # Check whether email already exists
    existing_user = await users_collection.find_one(
        {"email": data.email}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    # Hash password before saving
    hashed_password = hash_password(data.password)

    user = {
        "name": data.name,
        "email": data.email,
        "password": hashed_password,
        "profile_image": None,
    }

    result = await users_collection.insert_one(user)

    return {
        "message": "Signup successful.",
        "user_id": str(result.inserted_id),
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post("/login")
async def login(data: LoginRequest):

    user = await users_collection.find_one(
        {"email": data.email}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    password_correct = verify_password(
        data.password,
        user["password"],
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
    })

    return {
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "profile_image": user.get("profile_image"),
        },
    }