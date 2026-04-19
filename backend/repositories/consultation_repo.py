from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models.consultation import Consultation


class ConsultationRepository:
    """法律咨询仓储"""

    @staticmethod
    async def save(session: AsyncSession, consultation: Consultation) -> Consultation:
        """保存咨询记录"""
        session.add(consultation)
        await session.flush()
        await session.refresh(consultation)
        return consultation

    @staticmethod
    async def get(session: AsyncSession, consultation_id: str) -> Consultation | None:
        """根据ID获取咨询记录"""
        return await session.get(Consultation, consultation_id)

    @staticmethod
    async def get_by_user(
        session: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> list[Consultation]:
        """获取用户的咨询记录列表"""
        stmt = select(Consultation)\
            .where(Consultation.user_id == user_id)\
            .order_by(desc(Consultation.created_at))\
            .limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def list_recent(session: AsyncSession, limit: int = 10) -> list[Consultation]:
        """获取最近咨询记录"""
        stmt = select(Consultation).order_by(desc(Consultation.created_at)).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()