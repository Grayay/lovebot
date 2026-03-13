from datetime import datetime
from database import SessionLocal
from models.eventlog import EventLog


async def log_event(actor, module, event_type, object_id=0, before="", after=""):

    async with SessionLocal() as session:

        log = EventLog(
            ts=datetime.utcnow(),
            actor=actor,
            module=module,
            event_type=event_type,
            object_id=object_id,
            before=before,
            after=after
        )

        session.add(log)
        await session.commit()