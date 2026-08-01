from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_can_delete_project,
                                check_can_update_project, check_project_exists,
                                check_project_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.invest import close_investment_project, invest_donations

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_charity_projects(
    session: SessionDep
):
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep
):
    await check_project_name_duplicate(charity_project.name, session)
    db_project = await charity_project_crud.create(charity_project, session)
    await invest_donations(session)
    await session.refresh(db_project)
    return db_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    charity_project: CharityProjectUpdate,
    session: SessionDep
):
    db_project = await check_project_exists(project_id, session)
    await check_can_update_project(db_project, charity_project)
    await check_project_name_duplicate(charity_project.name, session)

    db_project = await close_investment_project(charity_project, db_project)
    db_project = await charity_project_crud.update(
        db_project, charity_project, session
    )
    return db_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep
):
    db_project = await check_project_exists(project_id, session)
    await check_can_delete_project(db_project)
    return await charity_project_crud.remove(db_project, session)
