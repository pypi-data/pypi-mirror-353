from uuid import UUID

from pydantic import BaseModel


class StartOrderDeliveryResponseDto(BaseModel):
    order_id: UUID
    driver_id: UUID
    consumer_id: UUID
