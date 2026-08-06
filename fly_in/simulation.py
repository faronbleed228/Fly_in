from .parsing import Graph
from .factories import DroneState, Drone, Zone
from collections import deque


class Simulation():
    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._drone_list = graph._drones_lst
        self.log_list: list[str] = []

    def run(self) -> None:
        while (self.check_simulation() is False):
            for drone in self._drone_list:
                self.turn(drone)
            print()

    def turn(self, drone: Drone) -> None:
        dest_zone = drone._path[0]
        if (dest_zone.can_enter_zone() is True):
            drone.move_drone()
            self.log_output(drone._id, dest_zone._name)
            drone.check_drone_state(self._drone_list)

    def check_simulation(self) -> bool:
        return all(drone._state is DroneState.ARRIVED
                   for drone in self._drone_list)

    def log_output(self, drone_id: str, dest: str) -> None:
        print(drone_id + "-" + dest, end=" ")

    def test_path(self, drone: Drone, zone_dict: dict[str, Zone]) -> None:
        zone_list = deque([zone for zone in zone_dict.values()
                           if zone._hub_type != "start_hub"])
        drone._path = zone_list
