from enum import Enum
from typing import List, Union
from flumine.order.order import BaseOrder

class OrderPackageType(Enum):
    PLACE = "PLACE"
    CANCEL = "CANCEL"
    UPDATE = "UPDATE"
    REPLACE = "REPLACE"

class BaseOrderPackage:
    def __init__(self, package_type: OrderPackageType, orders: List[BaseOrder]):
        self.package_type = package_type
        self.orders = orders

    def __iter__(self):
        return iter(self.orders)

    def __len__(self):
        return len(self.orders)

    def __getitem__(self, index):
        return self.orders[index]

    def __setitem__(self, index, order):
        self.orders[index] = order

    def append(self, order: BaseOrder) -> None:
        self.orders.append(order)

    def extend(self, orders: List[BaseOrder]) -> None:
        self.orders.extend(orders)

    def remove(self, order: BaseOrder) -> None:
        self.orders.remove(order)

    def clear(self) -> None:
        self.orders.clear()

    @property
    def market_id(self) -> str:
        return self.orders[0].market_id if self.orders else None

    @property
    def selection_id(self) -> int:
        return self.orders[0].selection_id if self.orders else None

    @property
    def handicap(self) -> float:
        return self.orders[0].handicap if self.orders else None

    def __repr__(self):
        return "BaseOrderPackage({0}): {1}".format(self.package_type.value, len(self.orders))