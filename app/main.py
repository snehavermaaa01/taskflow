from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from fastapi.middleware.cors import CORSMiddleware

from .database import (
    users_collection,
    check_database
)

from .schemas import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


app = FastAPI(
    title="TaskFlow API",
    description="FastAPI + MongoDB Task Management API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "TaskFlow API is running"
    }


@app.get("/health")
def health():
    if check_database():
        return {
            "api": "ok",
            "database": "MongoDB connected"
        }

    return {
        "api": "ok",
        "database": "MongoDB disconnected"
    }


# =========================
# SIGNUP
# =========================

@app.post(
    "/auth/signup",
    response_model=UserResponse,
    status_code=201
)
def signup(data: SignupRequest):

    existing_user = users_collection.find_one({
        "email": data.email
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_username = users_collection.find_one({
        "username": data.username
    })

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = {
        "email": data.email,
        "username": data.username,
        "hashed_password": hash_password(data.password)
    }

    result = users_collection.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "email": user["email"],
        "username": user["username"]
    }


# =========================
# LOGIN
# =========================

@app.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(data: LoginRequest):

    user = users_collection.find_one({
        "email": data.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        str(user["_id"])
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# AUTHENTICATION
# =========================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    from bson import ObjectId

    try:
        user = users_collection.find_one({
            "_id": ObjectId(user_id)
        })
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID"
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# =========================
# CURRENT USER
# =========================

@app.get(
    "/users/me",
    response_model=UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):

    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "username": current_user["username"]
    }