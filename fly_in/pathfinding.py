from .parsing import Graph
from .factories import Zone, Connection
import heapq
import logging

logger = logging.getLogger(__name__)


class Pathfinder():
    def __init__(self, graph: Graph, zone_list: list[Zone],
                 link_list: list[Connection], n_drones: int) -> None:
        self._graph = graph
        self._zone_list = zone_list
        self.start_zone: Zone
        self._end_zone: Zone
        self._link_list = link_list
        self._n_drones = n_drones
        self._distances: dict[str, float] = {}
        self.paths: dict[str, list[Zone]] = {}

    def pathfinder(self) -> list[Zone] | None:
        self.data_structure()
        self.paths[self.start_zone._name] = [self.start_zone]
        queue = [(0.0, self.start_zone._name)]
        cur_path = []
        while queue:
            cur_dist, cur_name = heapq.heappop(queue)
            cur_path = self.paths[cur_name]
            logger.debug(f"Cur pos {cur_name}")
            logger.debug(f"Current path is {cur_path}")
            if cur_name == self._end_zone._name:
                logger.debug("Found the end")
                return cur_path
            if cur_dist > self._distances[cur_name]:
                logger.debug(
                    f"Path for zone {cur_name} already exists with dist {self._distances[cur_name]})")
                continue
            else:
                cur_zone = cur_path[-1]
                neighbours = cur_zone.get_neighbours()
                for zone in neighbours:
                    new_distance = cur_dist + zone.get_movement_cost()
                    if new_distance < self._distances[zone._name]:
                        logger.debug(
                            f"New path to {zone._name} is {new_distance}")
                        self._distances[zone._name] = new_distance
                        new_path = cur_path.copy()
                        new_path.append(zone)
                        self.paths[zone._name] = new_path
                        heapq.heappush(queue,
                                       (new_distance, zone._name))

    def data_structure(self) -> None:
        for zone in self._zone_list:
            if zone._hub_type == "start_hub":
                self.start_zone = zone
                self._distances[zone._name] = 0
            elif zone._hub_type == "end_hub":
                self._end_zone = zone
                self._distances[zone._name] = float('inf')
            else:
                self._distances[zone._name] = float('inf')
