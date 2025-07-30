from uuid import UUID

from pydantic import BaseModel


class StartOrderPickUpDto(BaseModel):
    order_id: UUID
    driver_id: UUID
    business_id: UUID
