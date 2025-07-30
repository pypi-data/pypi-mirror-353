from dataclasses import dataclass
from enum import StrEnum

from ed_domain.core.entities.base_entity import BaseEntity


class ApiKeyStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"


@dataclass
class ApiKey(BaseEntity):
    name: str
    description: str
    prefix: str
    key_hash: str
    status: ApiKeyStatus
