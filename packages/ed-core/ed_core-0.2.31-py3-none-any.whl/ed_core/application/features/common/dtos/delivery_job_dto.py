from datetime import datetime
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.delivery_job import (DeliveryJob,
                                                         DeliveryJobStatus)
from ed_domain.core.value_objects.money import Money
from pydantic import BaseModel

from ed_core.application.features.common.dtos.driver_dto import DriverDto
from ed_core.application.features.common.dtos.waypoint_dto import WaypointDto


class DeliveryJobDto(BaseModel):
    id: UUID
    waypoints: list[WaypointDto]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
    driver: Optional[DriverDto]
    status: DeliveryJobStatus
    estimated_payment: Money
    estimated_completion_time: datetime

    @classmethod
    def from_delivery_job(
        cls,
        delivery_job: DeliveryJob,
    ) -> "DeliveryJobDto":
        assert delivery_job.waypoints, "Waypoints cannot be emp"

        return cls(
            id=delivery_job.id,
            waypoints=[
                WaypointDto.from_waypoint(**waypoint.__dict__)
                for waypoint in delivery_job.waypoints
            ],
            estimated_distance_in_kms=delivery_job.estimated_distance_in_kms,
            estimated_time_in_minutes=delivery_job.estimated_time_in_minutes,
            driver=DriverDto(**delivery_job.driver.__dict__),
            status=delivery_job.status,
            estimated_payment=delivery_job.estimated_payment,
            estimated_completion_time=delivery_job.estimated_completion_time,
        )
