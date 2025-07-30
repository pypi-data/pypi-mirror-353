from datetime import datetime
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.delivery_job import (DeliveryJob,
                                                         DeliveryJobStatus)
from ed_domain.core.value_objects.money import Money
from pydantic import BaseModel

from ed_core.application.features.common.dtos.waypoint_dto import WaypointDto


class DeliveryJobDto(BaseModel):
    id: UUID
    waypoints: list[WaypointDto]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
    driver: Optional[UUID]
    status: DeliveryJobStatus
    estimated_payment_in_birr: float
    estimated_completion_time: datetime

    @classmethod
    def from_delivery_job(
        cls,
        delivery_job: DeliveryJob,
    ) -> "DeliveryJobDto":
        return cls(
            id=delivery_job.id,
            waypoints=[
                WaypointDto.from_waypoint(waypoint)
                for waypoint in delivery_job.waypoints
            ],
            estimated_distance_in_kms=delivery_job.estimated_distance_in_kms,
            estimated_time_in_minutes=delivery_job.estimated_time_in_minutes,
            driver=delivery_job.driver_id,
            status=delivery_job.status,
            estimated_payment_in_birr=delivery_job.estimated_payment_in_birr,
            estimated_completion_time=delivery_job.estimated_completion_time,
        )
