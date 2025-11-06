import os
import json
import hashlib
import binascii
import secrets

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

PBKDF2_ROUNDS = 100_000


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str, salt: str) -> str:
    """Return hex digest for password using provided salt."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ROUNDS)
    return binascii.hexlify(dk).decode("ascii")


def create_user(email: str, password: str) -> tuple[bool, str]:
    """Create a new user identified by email. Returns (success, message)."""
    if not email or not password:
        return False, "Email and password are required"

    # basic email validation
    if "@" not in email or "." not in email:
        return False, "Invalid email address"

    users = _load_users()
    if email in users:
        return False, "User already exists"

    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)
    users[email] = {
        "salt": salt,
        "hash": pwd_hash
    }
    _save_users(users)
    return True, "User created"


def verify_user(email: str, password: str) -> bool:
    """Verify an email/password pair. Returns True if valid."""
    users = _load_users()
    if email not in users:
        return False
    rec = users[email]
    salt = rec.get("salt")
    expected = rec.get("hash")
    if not salt or not expected:
        return False
    return _hash_password(password, salt) == expected


def list_users() -> list:
    users = _load_users()
    return list(users.keys())


def delete_user(email: str) -> bool:
    users = _load_users()
    if email in users:
        users.pop(email)
        _save_users(users)
        return True
    return False
