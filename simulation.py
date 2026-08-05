from parsing import Graph
from factories import DroneState, Drone, Zone
from collections import deque


class Simulation():
    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._drone_list = graph._drones_lst
        self.log_list: list[str] = []

    def run(self) -> None:
        while (self.check_simulation() is False):
            self.turn(self._drone_list[0])
            break

    def check_simulation(self) -> bool:
        return all(drone._state is DroneState.ARRIVED for drone in self._drone_list)

    def turn(self, drone: Drone) -> None:
        next_zone = drone._path.popleft()
        cur_zone = drone._cur_pos
        log = drone._id + cur_zone._name + "-" + next_zone._name
        print(log)

    def test_path(self, drone: Drone, zone_dict: dict[str, Zone]) -> None:
        zone_list = deque([zone for zone in zone_dict.values()
                           if zone_dict.keys() != "start"])
        drone._path = zone_list
