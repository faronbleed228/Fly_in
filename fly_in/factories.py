from __future__ import annotations
import abc
from typing import Optional
from enum import Enum
from collections import deque


class DroneState(Enum):
    ACTIVE = 0
    TRANSIT = 1
    ARRIVED = 2


class Zone(abc.ABC):
    def __init__(self, name: str,
                 color: Optional[str], x: int,
                 y: int, max_drones: int, hub_type: str) -> None:
        self._name = name
        self._hub_type = hub_type
        self._color = color
        self._x = x
        self._y = y
        self._max_capacity = max_drones
        self._cur_capacity = 0

        self._zone_connections: list[Connection] = []

    def can_enter_zone(self) -> bool:
        if self._hub_type == "start_hub" or self._hub_type == "end_hub":
            return True
        return self._cur_capacity < self._max_capacity


class Connection():
    def __init__(self, name: str, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int) -> None:
        self._name = name
        self.zone_a = zone_a
        self.zone_b = zone_b
        self._max_link_capacity = max_link_capacity
        self._cur_link_capacity = 0


class NormalZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)


class RestrictedZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)


class PriorityZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)


class BlockedZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)


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
        hub_type = data_dict["hub_type"]
        x = data_dict["x"]
        y = data_dict["y"]
        color = data_dict.get("color", None)
        zone_type = data_dict.get("zone", "normal:")
        max_drones = data_dict.get("max_drones", 1)
        zone = self._zone_dict[zone_type](
            name, color, x, y, max_drones, hub_type)
        return zone


class Drone():
    def __init__(self, id: str, cur_pos: Zone, end_hub: Zone) -> None:
        self._id = id
        self._cur_pos = cur_pos
        self._end_hub = end_hub
        self._state = DroneState.ACTIVE
        self._path: deque[Zone] = deque([])
        self._turns_left = 0

    def move_drone(self) -> None:
        zone = self._path.popleft()
        if self._cur_pos._hub_type != "start_hub":
            self._cur_pos._cur_capacity -= 1
        self._cur_pos = zone
        if zone != self._end_hub:
            zone._cur_capacity += 1
        else:
            self._state = DroneState.ARRIVED

    def check_drone_state(self, drone_list: list[Drone]) -> None:
        if self._state == DroneState.ARRIVED:
            drone_list.remove(self)
