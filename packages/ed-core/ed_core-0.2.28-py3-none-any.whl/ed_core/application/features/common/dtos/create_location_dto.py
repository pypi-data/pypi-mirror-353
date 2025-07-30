from datetime import UTC, datetime

from ed_domain.core.entities import Location
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id

CITY = "Addis Ababa"
COUNTRY = "Ethiopia"


class CreateLocationDto(BaseModel):
    address: str
    latitude: float
    longitude: float
    postal_code: str

    async def create_location(self, uow: ABCAsyncUnitOfWork) -> Location:
        created_location = await uow.location_repository.create(
            Location(
                id=get_new_id(),
                address=self.address,
                latitude=self.latitude,
                longitude=self.longitude,
                postal_code=self.postal_code,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                last_used=datetime.now(UTC),
                city=CITY,
                country=COUNTRY,
                deleted=False,
                deleted_datetime=datetime.now(UTC),
            )
        )

        return created_location
