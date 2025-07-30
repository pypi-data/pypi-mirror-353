from datetime import UTC, datetime

from ed_domain.core.entities import Parcel
from ed_domain.core.entities.parcel import ParcelSize
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id


class CreateParcelDto(BaseModel):
    size: ParcelSize
    length: float
    width: float
    height: float
    weight: float
    fragile: bool

    async def create_parcel(self, uow: ABCAsyncUnitOfWork) -> Parcel:
        return await uow.parcel_repository.create(
            Parcel(
                id=get_new_id(),
                size=self.size,
                length=self.length,
                width=self.width,
                height=self.height,
                weight=self.weight,
                fragile=self.fragile,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )
