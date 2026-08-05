from parsing import Parsing, ParsingError
from simulation import Simulation


def main():
    parser = Parsing("01_linear_path.txt")
    try:
        parser.dispatcher()
    except ParsingError as e:
        print(e)
    graph = parser._graph
    print(graph._zone_dict)
    print(graph._drones_lst)
    print(graph._coordinates)
    sim = Simulation(graph)
    for drone in graph._drones_lst:
        print(drone._state)
    print(sim.check_simulation())
    sim.run()


if __name__ == "__main__":
    main()
