from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    db_project = await charity_project_crud.get(project_id, session)
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Проект не найден'
        )

    return db_project


async def check_can_delete_project(
    db_project: CharityProject
):
    if db_project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В проект были внесены средства, удаление невозможно'
        )


async def check_can_update_project(
    db_project: CharityProject,
    charity_project: CharityProjectUpdate,
):
    if db_project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать'
        )

    if (charity_project.full_amount is not None and
            charity_project.full_amount == 0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Требуемая сумма не может быть равна 0'
        )

    if (charity_project.full_amount is not None and
            charity_project.full_amount < db_project.invested_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Требуемая сумма не может быть меньше внесённой'
        )


async def check_project_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    if project_name is not None:
        project_id = await charity_project_crud.get_by_attribute(
            'name', project_name, session
        )
        if project_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект с таким именем уже существует!',
            )
