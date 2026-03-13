from datetime import datetime, timedelta

from sqlalchemy import select

from database import SessionLocal
from models.expenses import Expense

from config import ADMIN_ID, HER_ID


def _week_start_utc() -> datetime:
    """Start of 7 days ago (UTC)."""
    return datetime.utcnow() - timedelta(days=7)


def _month_start_utc() -> datetime:
    """Start of current month (UTC)."""
    now = datetime.utcnow()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def _build_report(user_id: int, period_label: str, start_dt: datetime) -> str:
    """Build personalized report for one user. Never reveals partner's personal expenses."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Expense).where(Expense.created_at >= start_dt)
        )
        expenses = list(result.scalars().all())

    self_sum = sum(e.amount for e in expenses if e.author_id == user_id and e.type == "self")
    couple_sum = sum(e.amount for e in expenses if e.type in ("couple", "joint"))

    lines = [
        f"💸 Финансы {period_label}",
        "",
        f"👤 Вы потратили на себя: {self_sum} ₽",
        f"❤️ На нас: {couple_sum} ₽",
    ]
    return "\n".join(lines)


async def weekly_report(bot):
    """Send personalized weekly expense report to both users."""
    start = _week_start_utc()

    admin_text = await _build_report(ADMIN_ID, "за неделю", start)
    her_text = await _build_report(HER_ID, "за неделю", start)

    await bot.send_message(ADMIN_ID, admin_text)
    await bot.send_message(HER_ID, her_text)


async def monthly_report(bot):
    """Send personalized monthly expense report to both users."""
    start = _month_start_utc()

    admin_text = await _build_report(ADMIN_ID, "за месяц", start)
    her_text = await _build_report(HER_ID, "за месяц", start)

    await bot.send_message(ADMIN_ID, admin_text)
    await bot.send_message(HER_ID, her_text)
