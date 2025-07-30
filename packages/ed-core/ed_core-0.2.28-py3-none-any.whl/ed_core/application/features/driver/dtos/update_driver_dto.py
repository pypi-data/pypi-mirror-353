from datetime import UTC, datetime
from typing import Optional

from ed_domain.core.aggregate_roots import Driver
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel, Field

from ed_core.application.features.common.dtos import CreateLocationDto


class UpdateDriverDto(BaseModel):
    profile_image: Optional[str] = Field(None)
    phone_number: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    location: Optional[CreateLocationDto] = Field(None)

    async def update_driver(self, driver: Driver, uow: ABCAsyncUnitOfWork) -> Driver:
        updated = False
        if self.location:
            updated = True
            created_location = await self.location.create_location(uow)
            driver.current_location = created_location

        if self.phone_number:
            updated = True
            driver.phone_number = self.phone_number

        if self.email:
            updated = True
            driver.email = self.email

        if updated:
            driver.update_datetime = datetime.now(UTC)

        await uow.driver_repository.update(driver.id, driver)

        return driver
