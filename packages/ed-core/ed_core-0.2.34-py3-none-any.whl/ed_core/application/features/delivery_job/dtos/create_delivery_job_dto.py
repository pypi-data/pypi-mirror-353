from datetime import UTC, datetime

from ed_domain.core.aggregate_roots import DeliveryJob
from ed_domain.core.aggregate_roots.delivery_job import DeliveryJobStatus
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.delivery_job.dtos.create_waypoint_dto import \
    CreateWaypointDto
from ed_core.common.generic_helpers import get_new_id


class CreateDeliveryJobDto(BaseModel):
    waypoints: list[CreateWaypointDto]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
    estimated_payment: float
    estimated_completion_time: datetime

    async def create_delivery_job(self, uow: ABCAsyncUnitOfWork) -> DeliveryJob:
        created_delivery_job = await uow.delivery_job_repository.create(
            DeliveryJob(
                id=get_new_id(),
                waypoints=[
                    (await waypoint.create_waypoint(uow)) for waypoint in self.waypoints
                ],
                estimated_distance_in_kms=self.estimated_distance_in_kms,
                estimated_time_in_minutes=self.estimated_time_in_minutes,
                status=DeliveryJobStatus.IN_PROGRESS,
                estimated_payment_in_birr=self.estimated_payment,
                estimated_completion_time=self.estimated_completion_time,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )

        return created_delivery_job
