from datetime import UTC, datetime

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.core.aggregate_roots import Consumer
from ed_domain.core.entities import Location
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos.consumer_dto import ConsumerDto
from ed_core.application.features.consumer.dtos.update_consumer_dto import (
    UpdateConsumerDto, UpdateLocationDto)
from ed_core.application.features.consumer.dtos.validators import \
    UpdateConsumerDtoValidator
from ed_core.application.features.consumer.requests.commands import \
    UpdateConsumerCommand
from ed_core.common.generic_helpers import get_new_id

LOG = get_logger()


@request_handler(UpdateConsumerCommand, BaseResponse[ConsumerDto])
class UpdateConsumerCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: UpdateConsumerCommand) -> BaseResponse[ConsumerDto]:
        dto_validator = UpdateConsumerDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            raise ApplicationException(
                Exceptions.ValidationException,
                "Update consumer failed.",
                dto_validator.errors,
            )

        dto = request.dto

        async with self._uow.transaction():
            consumer = await self._uow.consumer_repository.get(id=request.consumer_id)

            if consumer is None:
                raise ApplicationException(
                    Exceptions.NotFoundException,
                    "Consumer update failed.",
                    ["Consumer not found."],
                )

            if dto.location:
                location = await dto.location.update_location(
                    consumer.location.id, self._uow
                )
                consumer.location = location
                consumer.update_datetime = datetime.now(UTC)

            updated = await self._uow.consumer_repository.update(consumer.id, consumer)

        if not updated:
            raise ApplicationException(
                Exceptions.InternalServerException,
                "Consumer update failed.",
                ["Internal Server Error occured."],
            )

        return BaseResponse[ConsumerDto].success(
            "Consumer updated successfully.",
            ConsumerDto.from_consumer(consumer),
        )
