from datetime import UTC, datetime

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.core.aggregate_roots import Consumer
from ed_domain.core.entities import Bill
from ed_domain.core.entities.bill import BillStatus
from ed_domain.core.entities.notification import NotificationType
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.abc_rabbitmq_producers import \
    ABCRabbitMQProducers
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.business.dtos.validators import \
    CreateOrderDtoValidator
from ed_core.application.features.business.requests.commands import \
    CreateOrderCommand
from ed_core.application.features.common.dtos import OrderDto
from ed_core.application.features.common.helpers import (
    create_or_get_consumer, get_business)
from ed_core.common.generic_helpers import get_new_id

LOG = get_logger()

BILL_AMOUNT = 10


@request_handler(CreateOrderCommand, BaseResponse[OrderDto])
class CreateOrderCommandHandler(RequestHandler):
    def __init__(
        self,
        uow: ABCAsyncUnitOfWork,
        api: ABCApi,
    ):
        self._uow = uow
        self._api = api

        self._error_message = ""

    async def handle(self, request: CreateOrderCommand) -> BaseResponse[OrderDto]:
        business_id = request.business_id
        dto_validator = CreateOrderDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            raise ApplicationException(
                Exceptions.ValidationException,
                "Failed to create order",
                dto_validator.errors,
            )

        async with self._uow.transaction():
            business = await get_business(business_id, self._uow, self._error_message)

            bill = await self._create_bill()
            consumer = await create_or_get_consumer(request.dto.consumer, self._uow)
            created_order = await request.dto.create_order(
                business,
                consumer,
                bill,
                self._uow,
            )

        await self._send_notification(consumer)

        return BaseResponse[OrderDto].success(
            "Order created successfully.",
            OrderDto.from_order(created_order),
        )

    async def _create_bill(self) -> Bill:
        return await self._uow.bill_repository.create(
            Bill(
                id=get_new_id(),
                amount_in_birr=BILL_AMOUNT,
                bill_status=BillStatus.PENDING,
                due_date=datetime.now(UTC),
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )

    async def _send_notification(self, consumer: Consumer) -> None:
        LOG.info(f"Sending notification to consumer {consumer.id}")
        await self._api.notification_api.send_notification(
            {
                "user_id": consumer.user_id,
                "notification_type": NotificationType.EMAIL,
                "message": f"Dear {consumer.first_name}, an order has been created for you. More information will be provided soon.",
            }
        )
        LOG.info("Notification sent successfully.")
