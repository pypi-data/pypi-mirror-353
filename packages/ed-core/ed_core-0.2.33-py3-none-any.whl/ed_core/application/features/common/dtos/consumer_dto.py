from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.consumer import Consumer
from pydantic import BaseModel

from ed_core.application.features.common.dtos import LocationDto


class ConsumerDto(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: Optional[str]
    location: LocationDto

    @classmethod
    def from_consumer(cls, consumer: Consumer) -> "ConsumerDto":

        return cls(
            id=consumer.id,
            first_name=consumer.first_name,
            last_name=consumer.last_name,
            phone_number=consumer.phone_number,
            email=consumer.email,
            location=LocationDto(**consumer.location.__dict__),
        )
