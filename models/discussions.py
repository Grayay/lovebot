from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class DiscussionTopic(Base):
    __tablename__ = "discussion_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String, default="open")

    remind_next_morning: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)