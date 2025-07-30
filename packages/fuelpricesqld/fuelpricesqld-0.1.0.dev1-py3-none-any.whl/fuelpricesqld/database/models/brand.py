import sqlalchemy as sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fuelpricesqld.database.models.base import Base
from fuelpricesqld.database.models.country import Country


class Brand(Base):
    __tablename__ = "brands"

    brand_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.VARCHAR(30), unique=True)

    country_id: Mapped[int] = mapped_column(sql.ForeignKey("countries.country_id"))
    country: Mapped[Country] = relationship()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(brand_id={self.brand_id!r}, name={self.name!r})"
        )
