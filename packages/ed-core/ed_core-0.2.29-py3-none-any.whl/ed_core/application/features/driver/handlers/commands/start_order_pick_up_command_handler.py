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
                                                         get_business,
                                                         get_order,
                                                         send_notification)
from ed_core.application.features.driver.dtos import StartOrderPickUpDto
from ed_core.application.features.driver.requests.commands import \
    StartOrderPickUpCommand


@request_handler(StartOrderPickUpCommand, BaseResponse[StartOrderPickUpDto])
class StartOrderPickUpCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork, api: ABCApi, otp: ABCOtpGenerator):
        self._uow = uow
        self._api = api
        self._otp = otp

        self._success_message = "Order picked up initiated successfully."
        self._error_message = "Order pick up was not  successfully."

    async def handle(
        self, request: StartOrderPickUpCommand
    ) -> BaseResponse[StartOrderPickUpDto]:
        async with self._uow.transaction():
            order = await get_order(request.order_id, self._uow, self._error_message)
            if request.driver_id != order.driver_id:
                raise ApplicationException(
                    Exceptions.BadRequestException,
                    "Order not picked up.",
                    ["Bad request. Order driver is different."],
                )

            business_id = order.business.id
            business = await get_business(business_id, self._uow, self._error_message)

            otp = await create_otp(
                request.driver_id, OtpType.DROP_OFF, self._uow, self._otp
            )

        await send_notification(
            business.user_id,
            f"Your OTP for the pick up of order: {order.id} is {otp}.",
            self._api.notification_api,
            self._error_message,
        )

        return BaseResponse[StartOrderPickUpDto].success(
            self._success_message,
            StartOrderPickUpDto(
                order_id=order.id,
                driver_id=request.driver_id,
                business_id=order.business.id,
            ),
        )
