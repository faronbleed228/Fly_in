import abc
from typing import Optional


class ZoneError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Zone(abc.ABC):
    def __init__(self, name: str, color: Optional[str], x: int, y: int) -> None:
        self._name = name
        self._color = color
        self._x = x
        self._y = y


class NormalZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int = 1) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class RestrictedZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int = 1) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class PriorityZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int, max_drones: int = 1) -> None:
        super().__init__(name, color, x, y)
        self._max_drones = max_drones


class BlockedZone(Zone):
    def __init__(self, name: str, color: Optional[str], x: int, y: int) -> None:
        super().__init__(name, color, x, y)


class ZoneFactory():
    def __init__(self) -> None:
        self._zone_dict = {
            "restricted": RestrictedZone,
            "normal": NormalZone,
            "blocked": BlockedZone,
            "priority": PriorityZone
        }
        self._coord_list = [[]]
        self._name_list = []

    def create(self, name: str,
               x: int, y: int, metadata: dict[str, int]) -> Zone:


def test():
    matadata = {
        "zone": "normal",
        "color": "green",
        "max_drone": 1

    }
    factory = ZoneFactory()
    try:
        factory.validate("zone1", 10, 10, matadata)
    except ZoneError as e:
        print(e)


if __name__ == "__main__":
    test()
