from dataclasses import dataclass
from uuid import UUID

from rmediator.decorators import request
from rmediator.types import Request

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.driver.dtos import \
    StartOrderDeliveryResponseDto


@request(BaseResponse[StartOrderDeliveryResponseDto])
@dataclass
class StartOrderDeliveryCommand(Request):
    driver_id: UUID
    delivery_job_id: UUID
    order_id: UUID
