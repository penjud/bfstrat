from flumine.order.orderpackage import OrderPackageType, BaseOrder

class ControlError(Exception):
    pass

class BaseControl:
    NAME = None

    def __init__(self, flumine, events_manager):
        self.flumine = flumine
        self.events_manager = events_manager
        self._validate_control()

    def _validate_control(self):
        if self.NAME is None:
            raise ControlError("NAME attribute must be set")

    def start(self) -> None:
        self.events_manager.register_event(self.NAME, self)

    def stop(self) -> None:
        self.events_manager.unregister_event(self.NAME, self)

    def process_order_package(self, order_package: BaseOrder) -> None:
        self._process_order_package(order_package)

    def _process_order_package(self, order_package: BaseOrder) -> None:
        if order_package.package_type == OrderPackageType.PLACE:
            self._process_place_order_package(order_package)
        elif order_package.package_type == OrderPackageType.CANCEL:
            self._process_cancel_order_package(order_package)
        elif order_package.package_type == OrderPackageType.UPDATE:
            self._process_update_order_package(order_package)
        elif order_package.package_type == OrderPackageType.REPLACE:
            self._process_replace_order_package(order_package)
        else:
            raise ControlError(
                "order_package.package_type {} is unknown".format(order_package.package_type)
            )

    def _process_place_order_package(self, order_package: BaseOrder) -> None:
        for order in order_package:
            self._validate_place_order(order)
            self.flumine.handler_queue.put(order)

    def _process_cancel_order_package(self, order_package: BaseOrder) -> None:
        for order in order_package:
            self._validate_cancel_order(order)
            self.flumine.handler_queue.put(order)

    def _process_update_order_package(self, order_package: BaseOrder) -> None:
        for order in order_package:
            self._validate_update_order(order)
            self.flumine.handler_queue.put(order)

    def _process_replace_order_package(self, order_package: BaseOrder) -> None:
        for order in order_package:
            self._validate_replace_order(order)
            self.flumine.handler_queue.put(order)

    def _validate_place_order(self, order) -> None:
        pass

    def _validate_cancel_order(self, order) -> None:
        pass

    def _validate_update_order(self, order) -> None:
        pass

    def _validate_replace_order(self, order) -> None:
        pass