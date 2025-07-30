from dataclasses import dataclass

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import ConsumerDto
from ed_core.application.features.consumer.requests.queries.get_consumer_query import \
    GetConsumerQuery


@request_handler(GetConsumerQuery, BaseResponse[ConsumerDto])
@dataclass
class GetConsumerQueryHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: GetConsumerQuery) -> BaseResponse[ConsumerDto]:
        async with self._uow.transaction():
            consumer = await self._uow.consumer_repository.get(id=request.consumer_id)

        if consumer is None:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Consumer couldn't be fetched.",
                [f"Consumer with id {request.consumer_id} does not exist."],
            )

        return BaseResponse[ConsumerDto].success(
            "Consumer fetched successfully.",
            ConsumerDto.from_consumer(consumer),
        )
