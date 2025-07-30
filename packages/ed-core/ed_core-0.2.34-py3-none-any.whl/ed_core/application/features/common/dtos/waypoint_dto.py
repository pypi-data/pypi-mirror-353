from datetime import datetime

from ed_domain.core.aggregate_roots.waypoint import Waypoint, WaypointType
from pydantic import BaseModel

from ed_core.application.features.common.dtos.order_dto import OrderDto


class WaypointDto(BaseModel):
    order: OrderDto
    type: WaypointType
    expected_arrival_time: datetime
    sequence: int

    @classmethod
    def from_waypoint(cls, waypoint: Waypoint) -> "WaypointDto":
        return cls(
            order=OrderDto.from_order(waypoint.order),
            type=waypoint.waypoint_type,
            expected_arrival_time=waypoint.expected_arrival_time,
            sequence=waypoint.sequence,
        )
