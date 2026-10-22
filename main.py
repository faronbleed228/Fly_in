import logging
import fly_in
from sys import stderr
import argparse


# mode="w" очищает и перезаписывает файл при каждом запуске
file_handler = logging.FileHandler("app.log", mode="w", encoding="utf-8")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[file_handler]  # Передаем только файл, без консольного хендлера
)


def main() -> int:

    parsarg = parse_arguments()

    parser = fly_in.Parsing(parsarg.map_path)
    try:
        parser.dispatcher()
    except fly_in.ParsingError as e:
        print(e, file=stderr)
        return 1

    graph = parser._graph
    zone_list = [zone for zone in graph._zone_dict.values()]
    drone_list = graph._drones_lst.copy()

    pathfinder = fly_in.Pathfinder(
        graph, zone_list, graph._connections_links, len(graph._drones_lst))
    try:
        pathfinder.main_circle()
    except fly_in.PathfindingError as e:
        print(e, file=stderr)
        return 1

    sim = fly_in.Simulation(graph)
    try:
        sim.run()
    except ValueError as e:
        print(e, file=stderr)
        return 1
    if parsarg.headless:
        return 0
    from fly_in.visualiser import Visualiser
    game_state = sim.gamestate_list
    try:
        visualiser = Visualiser(
            graph, zone_list, drone_list, game_state)
        visualiser.main_loop()
    except KeyboardInterrupt:
        visualiser.quit()
        raise KeyboardInterrupt
    return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-in: drone simulation")
    parser.add_argument("map_path", type=str, help="Path to map file (.txt)")
    parser.add_argument("--headless", action="store_true",
                        help="Run without importing or opening Pygame")
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted", file=stderr)
        raise SystemExit(130)
