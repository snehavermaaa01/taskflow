# app/deps.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import jwt, JWTError
from bson import ObjectId

from app.database import users_collection
from app.auth import SECRET_KEY, ALGORITHM


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token.",
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    try:
        object_id = ObjectId(user_id)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID.",
        )

    user = await users_collection.find_one(
        {"_id": object_id}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user