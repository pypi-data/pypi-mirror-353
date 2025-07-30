from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.aggregate_roots import Waypoint
from ed_domain.core.aggregate_roots.waypoint import (WaypointStatus,
                                                     WaypointType)
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id


class CreateWaypointDto(BaseModel):
    order_id: UUID
    expected_arrival_time: datetime
    actual_arrival_time: datetime
    sequence: int
    waypoint_type: WaypointType
    waypoint_status: WaypointStatus

    async def create_waypoint(self, uow: ABCAsyncUnitOfWork) -> Waypoint:
        order = await uow.order_repository.get(id=self.order_id)
        assert order is not None

        return await uow.waypoint_repository.create(
            Waypoint(
                id=get_new_id(),
                order=order,
                expected_arrival_time=self.expected_arrival_time,
                actual_arrival_time=self.actual_arrival_time,
                sequence=self.sequence,
                waypoint_type=self.waypoint_type,
                waypoint_status=self.waypoint_status,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                deleted_datetime=None,
            )
        )
