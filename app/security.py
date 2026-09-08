from pwdlib import PasswordHash
from jose import jwt


password_hash = PasswordHash.recommended()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str
):
    return password_hash.verify(
        password,
        hashed_password
    )


def create_access_token(user_id: str):

    payload = {
        "user_id": user_id
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )