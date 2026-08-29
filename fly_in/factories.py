from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any
from enum import Enum
from collections import deque
import logging

logger = logging.getLogger(__name__)


class DroneState(Enum):
    ACTIVE = 0
    TRANSIT = 1
    ARRIVED = 2
    CONFIRMED = 3
    WAITING = 4


class Connection():
    def __init__(self, name: str, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int = 1) -> None:
        """Initializes a connection link between two zones.

        Args:
            name: Identifier/name of the connection link.
            zone_a: The first connected zone.
            zone_b: The second connected zone.
            max_link_capacity: Maximum number of drones
            allowed simultaneously on the link.
        """
        self._name = name
        self.zone_a = zone_a
        self.zone_b = zone_b
        self._max_link_capacity = max_link_capacity
        self._cur_link_capacity = 0
        self._drone_list: list[Drone] = []


class Zone(ABC):
    def __init__(self, name: str,
                 color: Optional[str], x: int,
                 y: int, max_drones: int, hub_type: str) -> None:
        """Initializes the base attributes of a zone.

        Args:
            name: Name of the zone.
            color: Optional color code/name for visual representation.
            x: X-coordinate of the zone location.
            y: Y-coordinate of the zone location.
            max_drones: Maximum capacity of drones inside the zone.
            hub_type: Type of the hub (e.g., 'start_hub',
            'end_hub', or standard).
        """
        self._name = name
        self._hub_type = hub_type
        self._color = color
        self._x = x
        self._y = y
        self._max_capacity = max_drones
        self._cur_capacity = 0
        self._drone_list: list[Drone] = []
        self._zone_connections: list[Connection] = []
        self._zone_blocked = False

    @abstractmethod
    def can_enter_zone(self) -> bool:
        """Checks if a drone can enter this
        zone based on its state and capacity.

        Returns:
            True if entry is permitted, False otherwise.
        """
        pass

    @abstractmethod
    def get_movement_cost(self) -> float:
        """Calculates the movement cost through this zone.

        Returns:
            The numeric movement cost.
        """
        pass

    def can_enter_link(self, link: Connection) -> bool:
        """Checks whether a given link currently
        has available capacity for entry.

        Args:
            link: The connection link to check.

        Returns:
            True if the link has free capacity, False otherwise.
        """
        if link._cur_link_capacity < link._max_link_capacity:
            return True
        return False

    def get_cur_link(self, drone: Drone) -> Connection:
        """Retrieves the active connection link
        between this zone and the drone's position.

        Args:
            drone: The drone whose current
            link/connection needs to be determined.

        Returns:
            The Connection instance linking
            the current zone and the drone's position.
        """
        drone_zone = drone._cur_pos
        if isinstance(drone_zone, Connection):
            return drone_zone
        for connection in self._zone_connections:
            for drone_zone_conection in drone_zone._zone_connections:
                if drone_zone_conection == connection:
                    return connection
        return connection

    def active_drones(self) -> bool:
        if self._hub_type == "start_hub" or self._hub_type == "end_hub":
            return False
        for drone in self._drone_list:
            if drone._state is DroneState.ACTIVE:
                return True
        return False

    def get_neighbours(self) -> list[Zone]:
        zone_list = []
        for link in self._zone_connections:
            if self is link.zone_a:
                zone_list.append(link.zone_b)
            else:
                zone_list.append(link.zone_a)
        return zone_list


class NormalZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)

    def can_enter_zone(self) -> bool:
        if self._hub_type == "start_hub" or self._hub_type == "end_hub":
            return True
        return self._cur_capacity < self._max_capacity

    def get_movement_cost(self) -> int:
        return 1


class RestrictedZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)

    def can_enter_zone(self) -> bool:
        if self._hub_type == "start_hub" or self._hub_type == "end_hub":
            return True
        return self._cur_capacity < self._max_capacity

    def get_movement_cost(self) -> float:
        return 2


class PriorityZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)

    def can_enter_zone(self) -> bool:
        if self._hub_type == "start_hub" or self._hub_type == "end_hub":
            return True
        return self._cur_capacity < self._max_capacity

    def get_movement_cost(self) -> float:
        return 0.5


class BlockedZone(Zone):
    def __init__(self, name: str, color: Optional[str],
                 x: int, y: int, max_drones: int, hub_type: str) -> None:
        super().__init__(name, color, x, y, max_drones, hub_type)

    def can_enter_zone(self) -> bool:
        return False

    def get_movement_cost(self) -> float:
        return float('inf')


class ZoneFactory():
    def __init__(self) -> None:
        self._zone_dict = {
            "restricted": RestrictedZone,
            "normal": NormalZone,
            "blocked": BlockedZone,
            "priority": PriorityZone
        }

    def create(self, data_dict: dict[str, Any]) -> Zone:
        name = data_dict["name"]
        hub_type = data_dict["hub_type"]
        x = data_dict["x"]
        y = data_dict["y"]
        color = data_dict.get("color", None)
        zone_type = data_dict.get("zone", "normal")
        max_drones = data_dict.get("max_drones", 1)
        zone: Zone
        match zone_type:
            case "restricted":
                zone = RestrictedZone(name, color, x, y, max_drones, hub_type)
            case "normal":
                zone = NormalZone(name, color, x, y, max_drones, hub_type)
            case "blocked":
                zone = BlockedZone(name, color, x, y, max_drones, hub_type)
            case "priority":
                zone = PriorityZone(name, color, x, y, max_drones, hub_type)
        return zone


class Drone():
    def __init__(self, id: str, cur_pos: Zone, end_hub: Zone) -> None:
        self._id = id
        self._cur_pos: Zone | Connection = cur_pos
        self._end_hub = end_hub
        self._state = DroneState.ACTIVE
        self._path: deque[Zone] = deque([])
        self._turns_left = 0
        self._waiting = 0

    def move_drone(self) -> None:
        zone = self._path.popleft()
        if isinstance(self._cur_pos, Zone):
            if self._cur_pos._hub_type != "start_hub":
                self._cur_pos._cur_capacity -= 1
            self._cur_pos._drone_list.remove(self)
            zone._drone_list.append(self)
            self._cur_pos = zone
            self._turns_left -= 1
            if zone._hub_type != self._end_hub._hub_type:
                zone._cur_capacity += 1

                self._state = DroneState.CONFIRMED
                self._waiting = 0
            else:
                self._state = DroneState.ARRIVED

    def move_drone_restricted(self, connection: Connection) -> None:
        if isinstance(self._cur_pos, Zone):
            logger.debug(
                f"Drone {self._id} entered connection {connection._name} "
                "and has to wait there")
            goal_zone = self._path[0]
            if self._cur_pos._hub_type != "start_hub":
                self._cur_pos._cur_capacity -= 1
            self._cur_pos._drone_list.remove(self)
            connection._drone_list.append(self)
            self._cur_pos = connection
            if goal_zone != self._end_hub:
                goal_zone._cur_capacity += 1
            self._state = DroneState.TRANSIT
        elif self._state is DroneState.TRANSIT:
            goal_zone = self._path.popleft()
            connection._drone_list.remove(self)
            goal_zone._drone_list.append(self)
            self._turns_left -= 1
            self._cur_pos = goal_zone
            logger.debug(
                f"Drone {self._id} left connection {connection._name} "
                f"and entered restricted zone {goal_zone}")
            if goal_zone != self._end_hub:
                self._state = DroneState.CONFIRMED
                self._waiting = 0
            else:
                self._state = DroneState.ARRIVED

    def check_drone_state(self, drone_list: list[Drone]) -> None:
        if self._state == DroneState.ARRIVED:
            drone_list.remove(self)
