from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.entities import Location
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id

CITY = "Addis Ababa"
COUNTRY = "Ethiopia"


class UpdateLocationDto(BaseModel):
    address: str
    latitude: float
    longitude: float
    postal_code: str

    async def update_location(
        self, location_id: UUID, uow: ABCAsyncUnitOfWork
    ) -> Location:
        updated_location = Location(
            id=location_id,
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
            deleted_datetime=None,
        )

        await uow.location_repository.update(location_id, updated_location)

        return updated_location
