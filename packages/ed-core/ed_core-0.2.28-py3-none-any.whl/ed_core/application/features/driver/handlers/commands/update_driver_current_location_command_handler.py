from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos.driver_dto import DriverDto
from ed_core.application.features.common.dtos.validators.update_location_dto_validator import \
    UpdateLocationDtoValidator
from ed_core.application.features.driver.requests.commands import \
    UpdateDriverCurrentLocationCommand

LOG = get_logger()


@request_handler(UpdateDriverCurrentLocationCommand, BaseResponse[DriverDto])
class UpdateDriverCurrentLocationCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: UpdateDriverCurrentLocationCommand
    ) -> BaseResponse[DriverDto]:
        dto_validator = UpdateLocationDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[DriverDto].error(
                "Update driver current location failed.", dto_validator.errors
            )

        async with self._uow.transaction():
            driver = await self._uow.driver_repository.get(id=request.driver_id)
            if driver is None:
                raise ApplicationException(
                    Exceptions.NotFoundException,
                    "Driver update failed.",
                    ["Driver not found."],
                )

            driver.current_location = await request.dto.update_location(
                driver.current_location.id, self._uow
            )
            await self._uow.driver_repository.update(driver.id, driver)

        return BaseResponse[DriverDto].success(
            "Driver current location updated successfully.",
            DriverDto.from_driver(driver),
        )
