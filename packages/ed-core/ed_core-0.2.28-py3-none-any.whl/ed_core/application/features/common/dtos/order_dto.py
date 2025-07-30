from datetime import datetime
from uuid import UUID

from ed_domain.core.aggregate_roots.order import Order, OrderStatus, Parcel
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos import BusinessDto, ConsumerDto
from ed_core.application.features.common.dtos.bill_dto import BillDto


class OrderDto(BaseModel):
    id: UUID
    business: BusinessDto
    consumer: ConsumerDto
    latest_time_of_delivery: datetime
    parcel: Parcel
    order_status: OrderStatus
    bill: BillDto

    @classmethod
    def from_order(cls, order: Order) -> "OrderDto":
        return cls(
            id=order.id,
            business=BusinessDto.from_business(order.business),
            consumer=ConsumerDto.from_consumer(order.consumer),
            latest_time_of_delivery=order.latest_time_of_delivery,
            parcel=order.parcel,
            order_status=order.order_status,
            bill=BillDto(**order.bill.__dict__),
        )
