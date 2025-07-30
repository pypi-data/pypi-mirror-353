from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.aggregate_roots.delivery_job import DeliveryJobStatus
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto
from ed_core.application.features.delivery_job.requests.commands.claim_delivery_job_command import \
    ClaimDeliveryJobCommand


@request_handler(ClaimDeliveryJobCommand, BaseResponse[DeliveryJobDto])
class ClaimDeliveryJobCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: ClaimDeliveryJobCommand
    ) -> BaseResponse[DeliveryJobDto]:
        async with self._uow.transaction():
            delivery_job = await self._uow.delivery_job_repository.get(
                id=request.delivery_job_id
            )

            if not delivery_job:
                raise ApplicationException(
                    Exceptions.NotFoundException,
                    "Delivery job not claimed.",
                    [f"Delivery job with id {request.delivery_job_id} not found."],
                )

            delivery_job.assign_driver(request.driver_id)
            await self._uow.delivery_job_repository.update(
                delivery_job.id,
                delivery_job,
            )

        return BaseResponse[DeliveryJobDto].success(
            "Delivery job Claimed successfully.",
            DeliveryJobDto.from_delivery_job(delivery_job),
        )
