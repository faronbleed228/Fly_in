from .parsing import Graph
from .factories import DroneState, Drone, Zone
from collections import deque, defaultdict
import logging

logger = logging.getLogger(__name__)


class Simulation():
    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._drone_list = graph._drones_lst
        self.log_list: list[str] = []

    def run(self) -> None:
        while (self.check_simulation() is False):
            intent_dict = self.collect_intentions()
            self.move_logic(intent_dict)
            self.reset_drone_status()
            self.reset_link_status()
            log_output = " ".join(self.log_list)
            self.log_list.clear()
            print(log_output)

    def check_simulation(self) -> bool:
        return all(drone._state is DroneState.ARRIVED
                   for drone in self._drone_list)

    def collect_intentions(self) -> defaultdict[Zone, list[Drone]]:
        intent_dict: defaultdict[Zone, list[Drone]] = defaultdict(list)
        for drone in self._drone_list:
            target_zone = drone._path[0]
            intent_dict[target_zone].append(drone)
            logger.info(
                f"Added intention of drone: {drone._id} to zone: {target_zone._name}")
        return intent_dict

    def move_logic(self, intent_dict: defaultdict[Zone, list[Drone]]) -> None:
        def sort_drone(drone: Drone) -> tuple[int, int]:
            if drone._state is DroneState.TRANSIT:
                turns_left = -1
            else:
                turns_left = drone._turns_left
            return (turns_left, drone._waiting * -1)

        def clear_intention() -> None:
            for zone in done_zone:
                intent_dict.pop(zone)
            done_zone.clear()

        decision = True
        done_zone: list[Zone] = []
        while decision is True:
            decision = False
            for dest_zone, drone_list in intent_dict.items():
                logger.info(
                    f"Making decision for dest_zone: {dest_zone._name}")
                if dest_zone.active_drones() is False:
                    logger.info(
                        f"Zone: {dest_zone._name} doesnt have any active drones.")
                    decision = True
                    done_zone.append(dest_zone)
                    drone_list.sort(key=sort_drone)
                    for drone in drone_list:
                        self.turn_logic(drone, dest_zone)
                else:
                    logger.info(
                        f"Zone: {dest_zone._name} was skipped due to having active drones.")
            clear_intention()

    def turn_logic(self, drone: Drone, zone: Zone) -> None:
        cur_link = zone.get_cur_link(drone)
        if drone._state is DroneState.TRANSIT:
            cur_link._cur_link_capacity -= 1
            drone.move_drone_restricted(cur_link)
            self.log_append(drone, zone._name)
        elif (zone.can_enter_zone() is True
                and zone.can_enter_link(cur_link) is True):
            if zone.get_movement_cost() == 2:
                if (drone._state is DroneState.ACTIVE):
                    logger.info(
                        f"Drone:{drone._id} is confirmed and moved to {cur_link._name}(restricted_path)")
                    cur_link._cur_link_capacity += 1
                    drone.move_drone_restricted(cur_link)
                    self.log_append(drone, cur_link._name)
                else:
                    logger.info(f"Drone:{drone._id} is Waiting")
                    drone._state = DroneState.WAITING
                    drone._waiting += 1

            elif zone.get_movement_cost() != 2:
                logger.info(
                    f"Drone:{drone._id} is confirmed and moved via {cur_link._name}")
                cur_link._cur_link_capacity += 1
                drone.move_drone()
                self.log_append(drone, zone._name)
                logger.info(
                    f"Drone:{drone._id} has {drone._turns_left} turn left.")
        else:
            logger.info(f"Drone:{drone._id} is Waiting")
            drone._state = DroneState.WAITING
            drone._waiting += 1

    def log_append(self, drone: Drone, dest_zone: str) -> None:
        drone_id = drone._id
        self.log_list.append(f"{drone_id}-{dest_zone}")

    def reset_drone_status(self) -> None:
        for drone in self._drone_list:
            if (drone._state is DroneState.WAITING
                    or drone._state is DroneState.CONFIRMED):
                drone._state = DroneState.ACTIVE
            elif drone._state is DroneState.ARRIVED:
                self._drone_list.remove(drone)

    def reset_link_status(self) -> None:
        for link in self._graph._connections_links:
            link._cur_link_capacity = 0

