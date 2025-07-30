from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.aggregate_roots import Consumer
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos.create_location_dto import \
    CreateLocationDto
from ed_core.common.generic_helpers import get_new_id


class CreateConsumerDto(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str
    location: CreateLocationDto

    async def create_consumer(self, uow: ABCAsyncUnitOfWork) -> Consumer:
        created_location = await self.location.create_location(uow)

        created_consumer = await uow.consumer_repository.create(
            Consumer(
                id=get_new_id(),
                user_id=self.user_id,
                first_name=self.first_name,
                last_name=self.last_name,
                phone_number=self.phone_number,
                email=self.email,
                profile_image_url="",
                location=created_location,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )

        return created_consumer
