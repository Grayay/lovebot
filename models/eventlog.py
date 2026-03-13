from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class EventLog(Base):
    __tablename__ = "event_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    actor: Mapped[int] = mapped_column(Integer)

    module: Mapped[str] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String)

    object_id: Mapped[int] = mapped_column(Integer)

    before: Mapped[str] = mapped_column(String, default="")
    after: Mapped[str] = mapped_column(String, default="")