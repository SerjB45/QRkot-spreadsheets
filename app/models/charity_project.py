from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import NAME_MAX_LENGTH
from app.core.db import Base, CommonMixin


class CharityProject(CommonMixin, Base):
    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
