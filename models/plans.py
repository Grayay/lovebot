from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[int] = mapped_column(Integer)

    title: Mapped[str] = mapped_column(String)
    place: Mapped[str] = mapped_column(String, default="")
    note: Mapped[str] = mapped_column(String, default="")

    dt_start: Mapped[datetime] = mapped_column(DateTime)
    remind_at: Mapped[datetime] = mapped_column(DateTime)

    status: Mapped[str] = mapped_column(String, default="active")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)