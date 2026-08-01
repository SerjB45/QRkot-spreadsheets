from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import (DESCRIPTION_MIN_LENGTH, NAME_MAX_LENGTH,
                                NAME_MIN_LENGTH)


class CharityProjectBase(BaseModel):
    name: str = Field(
        ..., min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH
    )
    description: str = Field(..., min_length=DESCRIPTION_MIN_LENGTH)
    full_amount: int = Field(..., gt=0)


class CharityProjectCreate(CharityProjectBase):
    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    description: Optional[str] = Field(
        default=None, min_length=DESCRIPTION_MIN_LENGTH
    )
    full_amount: Optional[int] = Field(default=None, ge=0)

    model_config = ConfigDict(extra='forbid')
