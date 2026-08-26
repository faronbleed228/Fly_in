import logging
import fly_in


# mode="w" очищает и перезаписывает файл при каждом запуске
file_handler = logging.FileHandler("app.log", mode="w", encoding="utf-8")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[file_handler]  # Передаем только файл, без консольного хендлера
)


def main():

    parser = fly_in.Parsing("maps/easy/01_linear_path.txt")
    try:
        parser.dispatcher()
    except fly_in.ParsingError as e:
        print(e)

    graph = parser._graph
    zone_list = [zone for zone in graph._zone_dict.values()]
    drone_list = graph._drones_lst.copy()

    pathfinder = fly_in.Pathfinder(
        graph, zone_list, graph._connections_links, len(graph._drones_lst))
    try:
        pathfinder.main_circle()
    except fly_in.PathfindingError as e:
        print(e)

    sim = fly_in.Simulation(graph)
    sim.run()
    game_state = sim.gamestate_list

    visualiser = fly_in.Visualiser(graph, zone_list, drone_list, game_state)
    #visualiser.main_loop()


def print_zone_data(zone_dict: dict[str, fly_in.Zone]):
    for zone in zone_dict.values():
        print("Name:", zone._name)
        print("Hub_type:", zone._hub_type)
        print("Cur Capacity:", zone._cur_capacity)
        print("Color:", zone._color)
        print("Max Capacity:", zone._max_capacity)
        print("X:", zone._x)
        print("Y:", zone._y)
        print("Connections:", zone._zone_connections)
        print()


def print_connection_data(con_list: list[fly_in.Connection]):
    for connection in con_list:
        print("Name:", connection._name)
        print("Name hub_a:", connection.zone_a._name)
        print("Name hub_b:", connection.zone_b._name)
        print("Max link Capacity:", connection._max_link_capacity)
        print("Cur Link Capacity:", connection._cur_link_capacity)
        print()


if __name__ == "__main__":
    logging.info("Main modul is up")
    main()
