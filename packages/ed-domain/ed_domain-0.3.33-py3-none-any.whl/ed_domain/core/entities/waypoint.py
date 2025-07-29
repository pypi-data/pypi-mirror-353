from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

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
    order_id: UUID
    eta: datetime
    sequence: int
    type: WaypointType
    waypoint_status: WaypointStatus

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "order_id": str(self.order_id),
            "eta": self.eta.isoformat(),
            "sequence": self.sequence,
            "type": self.type.value,
            "waypoint_status": self.waypoint_status.value,
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Waypoint":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            order_id=UUID(dict_value["order_id"]),
            eta=datetime.fromisoformat(dict_value["eta"]),
            sequence=dict_value["sequence"],
            type=WaypointType(dict_value["type"]),
            waypoint_status=WaypointStatus(dict_value["waypoint_status"]),
        )
