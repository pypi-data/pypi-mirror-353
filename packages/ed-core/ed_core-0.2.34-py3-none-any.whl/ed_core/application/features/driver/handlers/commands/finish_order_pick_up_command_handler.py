from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.aggregate_roots.order import OrderStatus
from ed_domain.core.aggregate_roots.waypoint import WaypointStatus
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.common.helpers import (get_order,
                                                         get_order_waypoint)
from ed_core.application.features.driver.requests.commands import \
    FinishOrderPickUpCommand


@request_handler(FinishOrderPickUpCommand, BaseResponse[None])
class FinishOrderPickUpCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork, api: ABCApi):
        self._uow = uow
        self._api = api

        self._success_message = "Order picked up successfully."
        self._error_message = "Order was not picked up successfully."

    async def handle(self, request: FinishOrderPickUpCommand) -> BaseResponse[None]:
        async with self._uow.transaction():
            order = await get_order(request.order_id, self._uow, self._error_message)
            waypoint = await get_order_waypoint(
                order.id, request.delivery_job_id, self._uow, self._error_message
            )

            if request.driver_id != order.driver_id:
                raise ApplicationException(
                    Exceptions.BadRequestException,
                    self._error_message,
                    ["Bad request. Order driver is different."],
                )

            # Update db
            order.update_status(OrderStatus.PICKED_UP)
            waypoint.update_status(WaypointStatus.DONE)

            # Update db
            await self._uow.order_repository.update(order.id, order)
            await self._uow.waypoint_repository.update(waypoint.id, waypoint)

        return BaseResponse[None].success(self._success_message, None)
