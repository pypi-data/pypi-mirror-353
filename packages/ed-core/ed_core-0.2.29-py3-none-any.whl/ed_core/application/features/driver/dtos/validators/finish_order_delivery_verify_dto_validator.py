from ed_domain.validation import ABCValidator, ValidationResponse
from ed_infrastructure.validation.default.otp_validator import OtpValidator

from ed_core.application.features.driver.dtos.finish_order_delivery_verify_dto import \
    FinishOrderDeliveryVerifyDto


class FinishOrderDeliveryVerifyDtoValidator(ABCValidator[FinishOrderDeliveryVerifyDto]):
    def __init__(self) -> None:
        self._otp_validator = OtpValidator()

    def validate(
        self,
        value: FinishOrderDeliveryVerifyDto,
        location: str = ABCValidator.DEFAULT_ERROR_LOCATION,
    ) -> ValidationResponse:
        return self._otp_validator.validate(value.otp, "body.otp")
