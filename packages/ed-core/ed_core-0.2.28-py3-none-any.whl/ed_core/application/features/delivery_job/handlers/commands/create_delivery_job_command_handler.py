from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto
from ed_core.application.features.delivery_job.requests.commands.create_delivery_job_command import \
    CreateDeliveryJobCommand


@request_handler(CreateDeliveryJobCommand, BaseResponse[DeliveryJobDto])
class CreateDeliveryJobCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: CreateDeliveryJobCommand
    ) -> BaseResponse[DeliveryJobDto]:
        async with self._uow.transaction():
            delivery_job = await request.dto.create_delivery_job(self._uow)

        return BaseResponse[DeliveryJobDto].success(
            "Delivery job created successfully.",
            DeliveryJobDto.from_delivery_job(delivery_job),
        )
