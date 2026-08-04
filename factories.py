import abc
from typing import Optional


class Zone(abc.ABC):
    def __init__(self, name: str, color: Optional[str], x: int, y: int) -> None:
        self._name = name
        self._color = color
        self._x = x
        self._y = y


class NormalZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class RestrictedZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class PriorityZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class BlockedZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int) -> None:
        super().__init__(name, color, x, y)


class ZoneFactory():
    def __init__(self) -> None:
        self._zone_dict = {
            "restricted:": RestrictedZone,
            "normal:": NormalZone,
            "blocked:": BlockedZone,
            "priority:": PriorityZone
        }

    def create(self, data_dict: dict) -> Zone:
        name = data_dict["name"]
        x = data_dict["x"]
        y = data_dict["y"]
        color = data_dict.get("color", None)
        zone_type = data_dict.get("zone", "normal:")
        max_drones = data_dict.get("max_drones", 1)
        zone = self._zone_dict[zone_type](name, color, x, y, max_drones)
        return zone
