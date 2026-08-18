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
        self.penalty_dict: dict[Zone, float] = {
            zone: 0.0 for zone in self._zone_list}

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
                self.weight_penalty(cur_path)
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

    def weight_penalty(self, path: list[Zone]) -> None:
        for i in range(len(path) - 1):
            cur_zone = path[i]
            next_zone = path[i+1]
            if cur_zone._hub_type == "start_hub" or next_zone._hub_type == "end_hub":
                continue
            else:
                link = self.get_penalty_link(cur_zone, next_zone)
                if link is not None:
                    max_capacity = min(next_zone._max_capacity,
                                       link._max_link_capacity)
                    cur_penalty = self.penalty_dict[next_zone]
                    self.penalty_dict[next_zone] = (cur_penalty + 0.5) * 1.1

    def get_penalty_link(self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        for link in zone_a._zone_connections:
            if link.zone_b == zone_b or link.zone_a == zone_b:
                return link
        return None
