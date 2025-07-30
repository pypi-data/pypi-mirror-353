from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ed_domain.core.aggregate_roots.order import Order
from ed_domain.core.entities.base_entity import BaseEntity


class WaypointStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class WaypointType(StrEnum):
    PICK_UP = "pick_up"
    DROP_OFF = "drop_off"


@dataclass
class Waypoint(BaseEntity):
    order: Order
    eta: datetime
    sequence: int
    waypoint_type: WaypointType
    waypoint_status: WaypointStatus
