from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.aggregate_roots import Business
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos import CreateLocationDto
from ed_core.common.generic_helpers import get_new_id


class CreateBusinessDto(BaseModel):
    user_id: UUID
    business_name: str
    owner_first_name: str
    owner_last_name: str
    phone_number: str
    email: str
    location: CreateLocationDto

    async def create_business(self, uow: ABCAsyncUnitOfWork) -> Business:
        created_location = await self.location.create_location(uow)

        created_business = await uow.business_repository.create(
            Business(
                id=get_new_id(),
                user_id=self.user_id,
                business_name=self.business_name,
                owner_first_name=self.owner_first_name,
                owner_last_name=self.owner_last_name,
                phone_number=self.phone_number,
                email=self.email,
                location=created_location,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=datetime.now(UTC),
            )
        )

        return created_business
