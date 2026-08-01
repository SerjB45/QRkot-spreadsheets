from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.schemas.charity_project import CharityProjectUpdate


async def invest_donations(session: AsyncSession) -> None:
    query_uninvested_donations = select(Donation).where(
        Donation.fully_invested.is_not(True)
    ).order_by(Donation.create_date)

    result = await session.execute(query_uninvested_donations)
    donations = result.scalars().all()

    for donation in donations:
        remaining_amount = donation.full_amount - donation.invested_amount

        if remaining_amount <= 0:
            continue

        query_open_projects = select(CharityProject).where(
            CharityProject.fully_invested.is_not(True)
        ).order_by(CharityProject.create_date)

        projects_result = await session.execute(query_open_projects)
        projects = projects_result.scalars().all()

        for project in projects:
            project_remaining = project.full_amount - project.invested_amount

            if project_remaining <= 0:
                continue

            investment_amount = min(remaining_amount, project_remaining)

            donation.invested_amount += investment_amount
            project.invested_amount += investment_amount

            remaining_amount -= investment_amount

            if donation.invested_amount >= donation.full_amount:
                donation.fully_invested = True
                donation.close_date = datetime.now(timezone.utc)

            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now(timezone.utc)

            if remaining_amount <= 0:
                break

    await session.commit()


async def close_investment_project(
    charity_project: CharityProjectUpdate,
    db_project: CharityProject
) -> CharityProject:
    updated_fields = charity_project.model_dump(exclude_unset=True)

    final_full_amount = updated_fields.get(
        'full_amount', db_project.full_amount
    )

    will_be_closed = (
        final_full_amount <= db_project.invested_amount and
        not db_project.fully_invested
    )

    if will_be_closed:
        db_project.fully_invested = True
        db_project.close_date = datetime.now(timezone.utc)

        flag_modified(db_project, 'fully_invested')
        flag_modified(db_project, 'close_date')
    return db_project
