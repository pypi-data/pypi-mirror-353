from datetime import UTC, datetime

from ed_domain.core.aggregate_roots import Business, Consumer
from ed_domain.core.aggregate_roots.order import Order, OrderStatus
from ed_domain.core.entities import Bill
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.business.dtos.create_parcel_dto import \
    CreateParcelDto
from ed_core.application.features.common.dtos.create_consumer_dto import \
    CreateConsumerDto
from ed_core.common.generic_helpers import get_new_id


class CreateOrderDto(BaseModel):
    consumer: CreateConsumerDto
    latest_time_of_delivery: datetime
    parcel: CreateParcelDto

    async def create_order(
        self,
        business: Business,
        consumer: Consumer,
        bill: Bill,
        uow: ABCAsyncUnitOfWork,
    ) -> Order:
        created_parcel = await self.parcel.create_parcel(uow)

        return await uow.order_repository.create(
            Order(
                id=get_new_id(),
                business=business,
                consumer=consumer,
                bill=bill,
                latest_time_of_delivery=self.latest_time_of_delivery,
                parcel=created_parcel,
                order_status=OrderStatus.PENDING,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )
