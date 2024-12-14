from datetime import datetime, timedelta, timezone
from re import S
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenPayloadSchema, AccessTokenSchema, RefreshTokenPayloadSchema, RefreshTokenSchema
from config import settings


mock_user = UserSchema(
    id="e325db35-6ab9-4945-9a81-e2b5466938a6",
    username="test_user",
    hashed_password=b"test_pass",
    email="test@email.com",
    is_active=True,
)

mock_access_token_payload = AccessTokenPayloadSchema(
    type=settings.jwt.access_type,
    sub=mock_user.username,
    user_id=mock_user.id,
    jti='e325db35-6ab9-4945-9a81-e2b5466938a5',
    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.jwt.access_expire),
    email=mock_user.email
)

mock_access_token = AccessTokenSchema(
    token=(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ik"
        "pvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
        ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV"
        "_adQssw5c"
    ), 
    payload=mock_access_token_payload
)

mock_refresh_token_payload = RefreshTokenPayloadSchema(
    type=settings.jwt.access_type,
    sub=mock_user.username,
    user_id=mock_user.id,
    jti='e325db35-6ab9-4945-9a81-e2b5466938a5',
    exp=datetime.now(timezone.utc) + timedelta(seconds=settings.jwt.access_expire),
)

mock_refresh_token = RefreshTokenSchema(
    token=(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ik"
        "pvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
        ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV"
        "_adQssw5d"
    ),
    payload=mock_refresh_token_payload 
)

