from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import TIMEZONE
from services.reports import weekly_report, monthly_report
from services.notifications import goals_reminder, topics_morning_reminder, memory_reminder

scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def start_scheduler(bot):

    # Напоминания по целям
    scheduler.add_job(
        goals_reminder,
        CronTrigger(day_of_week="mon,thu", hour=10, minute=0),
        args=[bot]
    )

    # Утренние темы обсуждения
    scheduler.add_job(
        topics_morning_reminder,
        CronTrigger(hour=9, minute=0),
        args=[bot]
    )

    # Отчет по тратам (воскресенье)
    scheduler.add_job(
        weekly_report,
        CronTrigger(day_of_week="sun", hour=10, minute=0),
        args=[bot]
    )

    # Отчет по тратам (ежемесячно)
    scheduler.add_job(
        monthly_report,
        CronTrigger(day="last", hour=10, minute=0),
        args=[bot]
    )

    # Воспоминания раз в месяц
    scheduler.add_job(
        memory_reminder,
        CronTrigger(day=1, hour=10, minute=0),
        args=[bot]
    )

    scheduler.start()

    return scheduler


async def stop_scheduler(scheduler):
    scheduler.shutdown()
