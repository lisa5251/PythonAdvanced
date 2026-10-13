import sqlite3
import hashlib
import secrets
import hmac

from fastapi import APIRouter, HTTPException
from models.user import UserCreate, UserLogin
from database import get_connection

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_password):
    salt, saved_hash = stored_password.split("$", 1)

    calculated_hash = hash_password(
        password,
        salt
    ).split("$", 1)[1]

    return hmac.compare_digest(
        calculated_hash,
        saved_hash
    )


@router.post("/register")
def register(user: UserCreate):
    username = user.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty"
        )

    if len(username) > 50:
        raise HTTPException(
            status_code=400,
            detail="Username must be 50 characters or fewer"
        )

    if len(user.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters"
        )

    connection = get_connection()
    cursor = connection.cursor()

    password_hash = hash_password(user.password)

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        connection.commit()
        user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    finally:
        connection.close()

    return {
        "message": "Account created successfully",
        "id": user_id,
        "username": username
    }


@router.post("/login")
def login(user: UserLogin):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (user.username.strip(),)
    )

    existing_user = cursor.fetchone()
    connection.close()

    if (
        existing_user is None
        or not verify_password(
            user.password,
            existing_user["password_hash"]
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    return {
        "message": "Login successful",
        "id": existing_user["id"],
        "username": existing_user["username"]
    }