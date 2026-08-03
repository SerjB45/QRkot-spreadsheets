from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_projects_by_completion_rate(
        self, session: AsyncSession,
    ) -> list:
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        return projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
