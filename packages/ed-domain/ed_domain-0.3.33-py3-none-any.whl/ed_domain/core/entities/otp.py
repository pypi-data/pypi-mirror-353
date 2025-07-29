from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from ed_domain.core.entities.base_entity import BaseEntity


class OtpType(StrEnum):
    VERIFY_EMAIL = "VERIFY_EMAIL"
    VERIFY_PHONE_NUMBER = "VERIFY_PHONE_NUMBER"
    LOGIN = "LOGIN"
    PICK_UP = "PICK_UP"
    DROP_OFF = "DROP_OFF"


@dataclass
class Otp(BaseEntity):
    user_id: UUID
    value: str
    otp_type: OtpType
    expiry_datetime: datetime

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        return {
            **base_dict,
            "user_id": str(self.user_id),
            "value": self.value,
            "otp_type": self.otp_type.value,
            "expiry_datetime": self.expiry_datetime.isoformat(),
        }

    @classmethod
    def from_dict(cls, dict_value: dict) -> "Otp":
        base_entity = BaseEntity.from_dict(dict_value)
        return cls(
            **vars(base_entity),
            user_id=UUID(dict_value["user_id"]),
            value=dict_value["value"],
            otp_type=OtpType(dict_value["otp_type"]),
            expiry_datetime=datetime.fromisoformat(
                dict_value["expiry_datetime"]),
        )
