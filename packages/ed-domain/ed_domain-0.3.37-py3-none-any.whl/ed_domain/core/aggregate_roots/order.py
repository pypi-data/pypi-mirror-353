from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from ed_domain.core.aggregate_roots.base_aggregate_root import \
    BaseAggregateRoot
from ed_domain.core.aggregate_roots.business import Business
from ed_domain.core.aggregate_roots.consumer import Consumer
from ed_domain.core.aggregate_roots.driver import Driver
from ed_domain.core.entities.bill import Bill, BillStatus
from ed_domain.core.entities.parcel import Parcel


class OrderStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PICKED_UP = "picked_up"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Order(BaseAggregateRoot):
    consumer: Consumer
    business: Business
    latest_time_of_delivery: datetime
    bill: Bill
    parcel: Parcel
    order_status: OrderStatus
    driver: Optional[Driver] = None

    def update_status(self, new_status: OrderStatus) -> None:
        if new_status not in OrderStatus:
            raise ValueError(f"Invalid order status: {new_status}")

        self.order_status = new_status

    def update_bill_status(self, new_status: str) -> None:
        if new_status not in BillStatus:
            raise ValueError(f"Invalid bill status: {new_status}")

        self.bill.bill_status = BillStatus(new_status)

    def assign_driver(self, driver_id: UUID) -> None:
        if self.order_status != OrderStatus.PENDING:
            raise ValueError(
                "Cannot assign driver to an order that is not pending.")
        self.driver_id = driver_id
        self.update_status(OrderStatus.IN_PROGRESS)

    def complete_order(self) -> None:
        if self.order_status != OrderStatus.IN_PROGRESS:
            raise ValueError(
                "Cannot complete an order that is not in progress.")
        self.update_status(OrderStatus.COMPLETED)

    def cancel_order(self) -> None:
        if self.order_status in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}:
            raise ValueError(
                "Cannot cancel an order that is already completed or cancelled."
            )
        self.update_status(OrderStatus.CANCELLED)
