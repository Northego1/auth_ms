import bcrypt

from timer import timer


def hash_password(
        password: str
) -> bytes:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )


def check_password(
        hashed_password_from_db: bytes,
        hashed_password_from_request: bytes
) -> bool:
    return bcrypt.checkpw(
        hashed_password_from_request,
        hashed_password_from_db
    )

