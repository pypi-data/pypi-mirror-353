from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot
from ed_domain.core.entities.car import Car
from ed_domain.core.entities.location import Location


@dataclass
class Driver(BaseAggregateRoot):
    user_id: UUID
    first_name: str
    last_name: str
    profile_image: str
    phone_number: str
    current_location: Location
    residence_location: Location
    car: Car
    available: bool = False
    email: Optional[str] = None

    def update_availability(self, available: bool) -> None:
        self.available = available

    def update_current_location(self, new_location: Location) -> None:
        self.current_location = new_location

    def update_profile_image(self, new_image: str) -> None:
        self.profile_image = new_image

    def update_email(self, new_email: str) -> None:
        self.email = new_email

    def update_phone_number(self, new_phone_number: str) -> None:
        self.phone_number = new_phone_number
