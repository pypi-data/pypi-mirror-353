from datetime import UTC, datetime

from ed_domain.core.entities import Car
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id


class CreateCarDto(BaseModel):
    make: str
    model: str
    year: int
    color: str
    seats: int
    license_plate: str
    registration_number: str

    async def create_car(self, uow: ABCAsyncUnitOfWork) -> Car:
        created_car = await uow.car_repository.create(
            Car(
                id=get_new_id(),  # Example ID generation
                make=self.make,
                model=self.model,
                year=self.year,
                color=self.color,
                seats=self.seats,
                license_plate_number=self.license_plate,
                registration_number=self.registration_number,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )

        return created_car
