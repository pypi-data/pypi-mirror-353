from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto
from ed_core.application.features.delivery_job.requests.commands import \
    CancelDeliveryJobCommand


@request_handler(CancelDeliveryJobCommand, BaseResponse[DeliveryJobDto])
class CancelDeliveryJobCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: CancelDeliveryJobCommand
    ) -> BaseResponse[DeliveryJobDto]:
        async with self._uow.transaction():
            delivery_job = await self._uow.delivery_job_repository.get(
                id=request.delivery_job_id
            )

            if delivery_job is None:
                raise ApplicationException(
                    Exceptions.NotFoundException,
                    "Delivery job cancelling failed..",
                    [f"Delivery job with id {request.delivery_job_id} not found."],
                )

            delivery_job.cancel_job()

            updated = await self._uow.delivery_job_repository.update(
                delivery_job.id, delivery_job
            )

        if not updated:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job cancelling failed..",
                ["Internal server error occured."],
            )

        return BaseResponse[DeliveryJobDto].success(
            "Delivery job Canceled successfully.",
            DeliveryJobDto.from_delivery_job(delivery_job),
        )
