from .parsing import Graph
from .factories import DroneState, Drone, Zone, Connection
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class Gamestate():
    def __init__(self, drone_list: list[Drone]) -> None:
        """Initializes a game state snapshot
        recording current positions of drones.

        Args:
            drone_list: List of all drones to track in this state snapshot.
        """
        self.drone_list = drone_list

        self.state_dict: dict[Drone, Connection | Zone] = self.save_state()

    def save_state(self) -> dict[Drone, Connection | Zone]:
        """Captures and returns the current positions of all tracked drones.

        Returns:
            A mapping of each Drone instance to its current Zone or Connection.
        """
        ret: dict[Drone, Connection | Zone] = {}
        for drone in self.drone_list:
            ret[drone] = drone._cur_pos
        return ret


class Simulation():
    def __init__(self, graph: Graph) -> None:
        """Initializes the simulation
        controller with the network graph and drones.

        Args:
            graph: The network graph
            containing zones, links, and initialized drones.
        """
        self._graph = graph
        self._drone_list = graph._drones_lst
        self._total_drone_list = graph._drones_lst.copy()
        self.log_list: list[str] = []
        self.gamestate_list: list[Gamestate] = []

    def run(self) -> None:
        """Runs the main turn-by-turn simulation
        loop until all drones reach destination."""
        while (self.check_simulation() is False):
            self.gamestate_list.append(Gamestate(self._total_drone_list))
            intent_dict = self.collect_intentions()
            self.move_logic(intent_dict)
            self.reset_drone_status()
            self.reset_link_status()
            log_output = " ".join(self.log_list)
            self.log_list.clear()
            print(log_output)
        self.gamestate_list.append(Gamestate(self._total_drone_list))

    def check_simulation(self) -> bool:
        """Checks if the simulation has completed.

        Returns:
            True if all drones have reached their destination (state ARRIVED),
            False otherwise.
        """
        return all(drone._state is DroneState.ARRIVED
                   for drone in self._drone_list)

    def collect_intentions(self) -> defaultdict[Zone, list[Drone]]:
        """Collects the next desired target
        zones for all currently active drones.

        Returns:
            A dictionary grouping drones by their intended destination Zone.
        """
        intent_dict: defaultdict[Zone, list[Drone]] = defaultdict(list)
        for drone in self._drone_list:
            target_zone = drone._path[0]
            intent_dict[target_zone].append(drone)
            logger.info(
                f"Added intention of drone: {drone._id} "
                f"to zone: {target_zone._name}")
        return intent_dict

    def move_logic(self, intent_dict: defaultdict[Zone, list[Drone]]) -> None:
        """Resolves drone movement intentions
        for the current turn based on availability.

        Args:
            intent_dict: Mapping of target zones
            to lists of drones intending to move there.
        """
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
                        f"Zone: {dest_zone._name} "
                        "doesnt have any active drones.")
                    decision = True
                    done_zone.append(dest_zone)
                    drone_list.sort(key=sort_drone)
                    for drone in drone_list:
                        self.turn_logic(drone, dest_zone)
                else:
                    logger.info(
                        f"Zone: {dest_zone._name} was "
                        "skipped due to having active drones.")
            clear_intention()

    def turn_logic(self, drone: Drone, zone: Zone) -> None:
        """Processes the turn action for a
        single drone trying to enter a target zone.

        Args:
            drone: The drone attempting the movement.
            zone: The target zone the drone wants to enter.
        """
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
                        f"Drone:{drone._id} is confirmed and "
                        f"moved to {cur_link._name}(restricted_path)")
                    cur_link._cur_link_capacity += 1
                    drone.move_drone_restricted(cur_link)
                    self.log_append(drone, cur_link._name)
                else:
                    logger.info(f"Drone:{drone._id} is Waiting")
                    drone._state = DroneState.WAITING
                    drone._waiting += 1

            elif zone.get_movement_cost() != 2:
                logger.info(
                    f"Drone:{drone._id} is confirmed "
                    f"and moved via {cur_link._name}")
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
        """Appends a drone move event to the turn log.

        Args:
            drone: The drone that performed the movement.
            dest_zone: Name of the destination zone or link.
        """
        drone_id = drone._id
        self.log_list.append(f"{drone_id}-{dest_zone}")

    def reset_drone_status(self) -> None:
        """Resets the state of waiting and
        confirmed drones to ACTIVE for the next turn,
        and removes arrived drones from the active pool.
        """
        i = 0
        while i != len(self._drone_list):
            drone = self._drone_list[i]
            if (drone._state is DroneState.WAITING
                    or drone._state is DroneState.CONFIRMED):
                drone._state = DroneState.ACTIVE
                i += 1
            elif drone._state is DroneState.ARRIVED:
                self._drone_list.remove(drone)
                i = 0
            elif (drone._state is DroneState.TRANSIT
                  or drone._state is DroneState.ACTIVE):
                i += 1

    def reset_link_status(self) -> None:
        """Resets the current link occupation
        capacities back to zero at the end of the turn."""
        for link in self._graph._connections_links:
            link._cur_link_capacity = 0
