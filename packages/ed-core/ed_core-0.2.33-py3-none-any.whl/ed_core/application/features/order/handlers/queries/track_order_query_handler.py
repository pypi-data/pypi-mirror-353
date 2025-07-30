from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import TrackOrderDto
from ed_core.application.features.order.requests.queries import TrackOrderQuery


@request_handler(TrackOrderQuery, BaseResponse[TrackOrderDto])
class TrackOrderQueryHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: TrackOrderQuery) -> BaseResponse[TrackOrderDto]:
        raise NotImplementedError()
        async with self._uow.transaction():
            order = await self._uow.order_repository.get(id=request.order_id)
