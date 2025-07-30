from datetime import UTC, datetime
from typing import Optional

from ed_domain.core.aggregate_roots import Business
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel, Field

from ed_core.application.features.common.dtos import CreateLocationDto


class UpdateBusinessDto(BaseModel):
    phone_number: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    location: Optional[CreateLocationDto] = Field(None)

    async def update_business(
        self, business: Business, uow: ABCAsyncUnitOfWork
    ) -> Business:
        updated = False
        if self.location:
            updated = True
            created_location = await self.location.create_location(uow)
            business.location = created_location

        if self.phone_number:
            updated = True
            business.phone_number = self.phone_number

        if self.email:
            updated = True
            business.email = self.email

        if updated:
            business.update_datetime = datetime.now(UTC)

        await uow.business_repository.update(business.id, business)

        return business
