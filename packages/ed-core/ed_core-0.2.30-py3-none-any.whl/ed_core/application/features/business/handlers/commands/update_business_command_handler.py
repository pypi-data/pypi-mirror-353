from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.business.dtos.validators import \
    UpdateBusinessDtoValidator
from ed_core.application.features.business.requests.commands import \
    UpdateBusinessCommand
from ed_core.application.features.common.dtos.business_dto import BusinessDto

LOG = get_logger()


@request_handler(UpdateBusinessCommand, BaseResponse[BusinessDto])
class UpdateBusinessCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: UpdateBusinessCommand) -> BaseResponse[BusinessDto]:
        dto_validator = UpdateBusinessDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[BusinessDto].error(
                "Update business failed.", dto_validator.errors
            )

        async with self._uow.transaction():
            business = await self._uow.business_repository.get(id=request.id)
            if business is None:
                raise ApplicationException(
                    Exceptions.NotFoundException,
                    "Business update failed.",
                    ["Business not found."],
                )

            await request.dto.update_business(business, self._uow)

        return BaseResponse[BusinessDto].success(
            "Business updated successfully.",
            BusinessDto.from_business(business),
        )
