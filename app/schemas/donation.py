from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationBase(BaseModel):
    full_amount: int = Field(..., gt=0)
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: datetime


class DonationFullInfoDB(DonationDB):
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
    user_id: Optional[int] = None
