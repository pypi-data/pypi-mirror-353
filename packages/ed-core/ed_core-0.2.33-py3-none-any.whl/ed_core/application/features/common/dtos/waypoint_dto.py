from datetime import datetime

from ed_domain.core.aggregate_roots.waypoint import Waypoint, WaypointType
from pydantic import BaseModel

from ed_core.application.features.common.dtos.order_dto import OrderDto


class WaypointDto(BaseModel):
    order: OrderDto
    type: WaypointType
    eta: datetime
    sequence: int

    @classmethod
    def from_waypoint(cls, waypoint: Waypoint) -> "WaypointDto":
        return cls(
            order=OrderDto(**waypoint.order.__dict__),
            type=waypoint.waypoint_type,
            eta=waypoint.eta,
            sequence=waypoint.sequence,
        )
