from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class DateIdea(Base):
    __tablename__ = "date_ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author: Mapped[int] = mapped_column(Integer)

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, default="")
    link: Mapped[str] = mapped_column(String, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)