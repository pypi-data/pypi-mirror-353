from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.aggregate_roots import Driver
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos import CreateLocationDto
from ed_core.application.features.driver.dtos.create_car_dto import \
    CreateCarDto
from ed_core.common.generic_helpers import get_new_id


class CreateDriverDto(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    profile_image: str
    phone_number: str
    email: str
    location: CreateLocationDto
    car: CreateCarDto

    async def create_driver(self, uow: ABCAsyncUnitOfWork) -> Driver:
        created_location = await self.location.create_location(uow)
        created_car = await self.car.create_car(uow)
        created_driver = await uow.driver_repository.create(
            Driver(
                id=get_new_id(),
                user_id=self.user_id,
                first_name=self.first_name,
                last_name=self.last_name,
                profile_image=self.profile_image,
                phone_number=self.phone_number,
                email=self.email,
                current_location=created_location,
                residence_location=created_location,
                car=created_car,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )

        return created_driver
