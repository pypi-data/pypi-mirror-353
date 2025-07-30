from ed_domain.common.logging import get_logger
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.business.dtos.validators import \
    CreateBusinessDtoValidator
from ed_core.application.features.business.requests.commands import \
    CreateBusinessCommand
from ed_core.application.features.common.dtos.business_dto import BusinessDto

LOG = get_logger()


@request_handler(CreateBusinessCommand, BaseResponse[BusinessDto])
class CreateBusinessCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(self, request: CreateBusinessCommand) -> BaseResponse[BusinessDto]:
        dto_validator = CreateBusinessDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[BusinessDto].error(
                "Create business failed.", dto_validator.errors
            )

        async with self._uow.transaction():
            business = await request.dto.create_business(self._uow)

        print(business)
        return BaseResponse[BusinessDto].success(
            "Business created successfully.",
            BusinessDto.from_business(business),
        )
