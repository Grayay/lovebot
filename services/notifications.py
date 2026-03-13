from database import SessionLocal
from sqlalchemy import select

from models.goals import Goal, GoalStep
from models.discussions import DiscussionTopic
from models.memories import Memory
from models.shopping import HomeProduct

from config import ADMIN_ID, HER_ID


async def goals_reminder(bot):

    async with SessionLocal() as session:

        goals = await session.execute(select(Goal))
        goals = goals.scalars().all()

        for g in goals:

            steps = await session.execute(
                select(GoalStep).where(
                    GoalStep.goal_id == g.id,
                    GoalStep.status == "open"
                )
            )

            step = steps.scalars().first()

            if not step:
                continue

            text = (
                f"🎯 Напоминание о цели\n\n"
                f"{g.title}\n\n"
                f"Следующий шаг:\n{step.text}"
            )

            await bot.send_message(ADMIN_ID, text)
            await bot.send_message(HER_ID, text)


async def topics_morning_reminder(bot):

    async with SessionLocal() as session:

        topics = await session.execute(
            select(DiscussionTopic).where(
                DiscussionTopic.status == "open",
                DiscussionTopic.remind_next_morning == True
            )
        )

        topics = topics.scalars().all()

        for t in topics:

            await bot.send_message(
                t.author,
                f"💬 Нужно обсудить:\n\n{t.text}"
            )


async def memory_reminder(bot):

    async with SessionLocal() as session:

        result = await session.execute(select(Memory))
        memories = result.scalars().all()

        if not memories:
            return

        memory = memories[0]

        text = f"📖 Воспоминание\n\n{memory.text}"

        await bot.send_message(ADMIN_ID, text)
        await bot.send_message(HER_ID, text)


async def seed_home_products():

    base_products = [
        ("молоко", "delivery"),
        ("сыр", "delivery"),
        ("сметана", "delivery"),
        ("сосиски", "delivery"),
        ("творог", "delivery"),
        ("яйца", "delivery"),
        ("соленые огурцы", "delivery"),
        ("тунец", "delivery"),
        ("сыр фета", "delivery"),
        ("кисло-сладкий соус", "delivery"),
        ("хлеб", "store"),
        ("апельсины", "store"),
        ("салат", "delivery"),
        ("масло", "delivery"),
        ("булочки для хот-догов", "store"),
        ("картошка", "store"),
        ("питахая", "delivery"),
        ("какао", "delivery"),
        ("помидоры", "delivery"),
        ("чай", "delivery"),
        ("яблоки", "store"),
        ("чеснок", "store"),
        ("лук", "store"),
        ("кефир", "delivery"),
    ]

    async with SessionLocal() as session:

        result = await session.execute(select(HomeProduct))
        existing = result.scalars().first()

        if existing:
            return

        for name, cat in base_products:

            session.add(
                HomeProduct(
                    name=name,
                    category=cat
                )
            )

        await session.commit()