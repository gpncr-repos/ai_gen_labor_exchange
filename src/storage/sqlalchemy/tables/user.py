from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interfaces.base_alchemy_model import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_company: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    jobs: Mapped[list["Job"]] = relationship(  # noqa
        back_populates="user", cascade="all, delete-orphan"
    )
    responses: Mapped[list["Response"]] = relationship(  # noqa
        back_populates="user", cascade="all, delete-orphan"
    )
