from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import OrderDto
from ed_core.application.features.order.requests.queries import GetOrdersQuery


@request_handler(GetOrdersQuery, BaseResponse[list[OrderDto]])
class GetOrdersQueryHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: GetOrdersQuery) -> BaseResponse[list[OrderDto]]:
        async with self._uow.transaction():
            orders = await self._uow.order_repository.get_all()

        return BaseResponse[list[OrderDto]].success(
            "Orders fetched successfully.",
            [OrderDto.from_order(order) for order in orders],
        )
