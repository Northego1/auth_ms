from datetime import datetime
import uuid
from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    LargeBinary,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship

from database.db_setup import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4()
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    hashed_password: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String, 
        unique=True,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    sessions = relationship( #o2m
        "UserSessionModel",
        back_populates='user'
    )


class UserSessionModel(Base):
    __tablename__ = 'user_session'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4()
    )
    user_id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=False,
        index=True
    )
    fingerprint_hash: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )
    refresh_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    session_num: Mapped[int] = mapped_column(Integer, nullable=False)


    user = relationship( #m2o
        "UserModel",
        back_populates='sessions'
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'session_num', name='user_session_unique'),
    )


class BlackListAccessJwtModel(Base):
    __tablename__ = 'black_list_access_jwt'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4()
        )
    access_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )
    expire_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )