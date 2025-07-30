from uuid import UUID

from ed_domain.core.aggregate_roots import Business
from pydantic import BaseModel

from ed_core.application.features.common.dtos.location_dto import LocationDto


class BusinessDto(BaseModel):
    id: UUID
    business_name: str
    owner_first_name: str
    owner_last_name: str
    phone_number: str
    email: str
    location: LocationDto

    @classmethod
    def from_business(cls, business: Business) -> "BusinessDto":
        return cls(
            id=business.id,
            business_name=business.business_name,
            owner_first_name=business.owner_first_name,
            owner_last_name=business.owner_last_name,
            phone_number=business.phone_number,
            email=business.email,
            location=LocationDto(**business.location.__dict__),
        )
