from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.entities.otp import OtpType
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from ed_domain.utils.otp.abc_otp_generator import ABCOtpGenerator
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.common.helpers import (create_otp,
                                                         get_consumer,
                                                         get_order,
                                                         send_notification)
from ed_core.application.features.driver.dtos import \
    StartOrderDeliveryResponseDto
from ed_core.application.features.driver.requests.commands import \
    StartOrderDeliveryCommand


@request_handler(StartOrderDeliveryCommand, BaseResponse[StartOrderDeliveryResponseDto])
class StartOrderDeliveryCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork, api: ABCApi, otp: ABCOtpGenerator):
        self._uow = uow
        self._api = api
        self._otp = otp

        self._success_message = "Order delivery initiated successfully."
        self._error_message = "Order delivery was not initiated successfully."

    async def handle(
        self, request: StartOrderDeliveryCommand
    ) -> BaseResponse[StartOrderDeliveryResponseDto]:
        async with self._uow.transaction():
            order = await get_order(request.order_id, self._uow, self._error_message)
            if request.driver_id != order.driver_id:
                raise ApplicationException(
                    Exceptions.BadRequestException,
                    "Order not picked up.",
                    ["Bad request. Order driver is different."],
                )

            consumer_id = order.consumer.id
            consumer = await get_consumer(consumer_id, self._uow, self._error_message)

            otp = await create_otp(
                request.driver_id, OtpType.DROP_OFF, self._uow, self._otp
            )

        await send_notification(
            consumer.user_id,
            f"Your OTP for accepting the order: {order.id} is {otp}.",
            self._api.notification_api,
            self._error_message,
        )

        return BaseResponse[StartOrderDeliveryResponseDto].success(
            self._success_message,
            StartOrderDeliveryResponseDto(
                order_id=order.id,
                driver_id=request.driver_id,
                consumer_id=order.consumer.id,
            ),
        )
