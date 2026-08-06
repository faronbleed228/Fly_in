import fly_in


def main():
    parser = fly_in.Parsing("01_linear_path.txt")
    try:
        parser.dispatcher()
    except fly_in.ParsingError as e:
        print(e)
    graph = parser._graph
    # print_zone_data(graph._zone_dict)
    # print_connection_data(graph._connections_links)
    sim = fly_in.Simulation(graph)
    for drone in graph._drones_lst:
        sim.test_path(drone, graph._zone_dict)
    sim.run()


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
    main()
