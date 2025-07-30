from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import OrderDto
from ed_core.application.features.driver.requests.queries import \
    GetDriverOrdersQuery


@request_handler(GetDriverOrdersQuery, BaseResponse[list[OrderDto]])
class GetDriverOrdersQueryHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: GetDriverOrdersQuery
    ) -> BaseResponse[list[OrderDto]]:
        async with self._uow.transaction():
            orders = await self._uow.order_repository.get_all(
                driver_id=request.driver_id
            )

        return BaseResponse[list[OrderDto]].success(
            "Driver orders fetched successfully.",
            [OrderDto.from_order(order) for order in orders],
        )
