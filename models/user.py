# ruff: noqa
# pyright: ignore-all

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from utils.hash_password import hash_password
from models.base_model import BaseModel, Base


class User(BaseModel, Base):
    """ User Class """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(
        nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    corporate_name: Mapped[str] = mapped_column(nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    reset_token: Mapped[str] = mapped_column(nullable=True)
    disabled: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(nullable=False, default="user")
    token_created_at: Mapped[datetime] = mapped_column(nullable=True)

    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan")
    projects: Mapped[list["ProjectMember"] ]= relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=True)
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    invitations: Mapped[list["ProjectInvitation"]] = relationship(
        back_populates="invited_user", cascade="all, delete-orphan")
    files: Mapped[list["UploadedFile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        """
            instantiation of new User Class
        """
        if kwargs:
            if 'password' in kwargs:
                hashed_pwd = hash_password(kwargs['password'])
                kwargs['password'] = hashed_pwd
        super().__init__(*args, **kwargs)
