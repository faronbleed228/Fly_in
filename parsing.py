from factories import ZoneFactory, Zone


class ParsingError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Graph():
    def __init__(self) -> None:
        self._zone_dict: dict[str, Zone] = {}
        self.zone_factory = ZoneFactory()
        self._start = False
        self._end = False

    def add_zone(self, data_dict: dict):
        if data_dict["name"] in self._zone_dict.keys():
            raise ParsingError("Hub name already exists on line")
        if data_dict["hub_type"] == "start_hub":
            self.check_start_end(True, False)
        if data_dict["hub_type"] == "end_hub":
            self.check_start_end(False, True)
        zone = self.zone_factory.create(data_dict)
        self._zone_dict[data_dict["name"]] = zone

    def check_start_end(self, start: bool, end: bool):
        if start is True and self._start is False:
            self._start = True
        elif end is True and self._end is False:
            self._end = True
        elif (start is True and self._start is True) or (end is True and self._end is True):
            raise ParsingError(
                "Map must have only one starting and ending point. line:")
        elif (start is False and end is False and (self._end is False or self._start is False)):
            raise ParsingError(
                "Map must have at least one starting and ending point(no line with one of them or both).")


class Parsing():
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name
        self._pars_dict = {
            "start_hub:": self.hub_validate,
            "end_hub:": self.hub_validate,
            "hub:": self.hub_validate,
            "connection:": self.connection_validate,
            "nb_drones:": self.nb_drones_validate
        }
        self.zone_list = ["restricted",
                          "normal",
                          "blocked",
                          "priority"]
        self._graph = Graph()
        self._nb_drones = 0

    def dispatcher(self):
        with open(self._file_name) as fd:
            for line_num, line in enumerate(fd, 1):
                line_lst = line.split()
                if not line_lst:
                    continue
                elif line.startswith("#"):
                    continue
                else:
                    func = self._pars_dict.get(line_lst[0], None)
                    if func is None:
                        raise ParsingError(
                            f"Unknown parsing block on line {line_num}")
            self._graph.check_start_end(False, False)

    def hub_validate(self, line_lst: list, line_num: int):
        hub_data_dict = {}

        def hub_metadat_validate():
            if line_lst[4].startswith("[") and line_lst[len(line_lst) - 1].endswith("]"):
                for line in line_lst[4:]:
                    line = line.strip("[]")
                    metadata_list = line.split("=")
                    if len(metadata_list) != 2:
                        raise ParsingError(
                            f"Hub metadata format error on line {line_num}")
                    if (metadata_list[0] != "color" and metadata_list[0] != "max_drones"
                            and metadata_list[0] != "zone"):
                        raise ParsingError(
                            f"Hub metadata type error on line {line_num}")
                    if metadata_list[0] == "max_drones":
                        max_drones = self.parse_pos_int(
                            metadata_list[1], f"Hub metadata(max_drones) error on line {line_num}", True)
                        hub_data_dict["max_drones"] = max_drones
                    elif metadata_list[0] == "zone":
                        if (metadata_list[1] not in self.zone_list):
                            raise ParsingError(
                                f"Hub zone type error on line {line_num}")
                        zone = metadata_list[1]
                        hub_data_dict["zone"] = zone
                    elif metadata_list[0] == "color":
                        color = metadata_list[1]
                        hub_data_dict["color"] = color
            else:
                raise ParsingError(
                    f"Hub metadata format([]) error on line {line_num}")
        if self._nb_drones == 0:
            raise ParsingError(
                f"Hub validation before nb_drones defined on line {line_num}")
        if (len(line_lst)) < 4:
            raise ParsingError(
                f"Wrong Hub format(lenght) on line {line_num}")
        elif " " in line_lst[1] or "-" in line_lst[1]:
            raise ParsingError(
                f"Wrong Hub Name format on line {line_num}")
        name = line_lst[1]
        hub_data_dict["name"] = name
        x = self.parse_pos_int(
            line_lst[2], f"Wrong Hub x,y Data Type format on line {line_num}")
        y = self.parse_pos_int(
            line_lst[3], f"Wrong Hub x,y Data Type format on line {line_num}")
        hub_data_dict["x"] = x
        hub_data_dict["y"] = y
        if len(line_lst) > 4:
            hub_metadat_validate()
        hub_data_dict["hub_type"] = line_lst[0]
        self._graph.add_zone(hub_data_dict)

    def parse_pos_int(self, raw: str, e_msg: str, only_pos: bool = False) -> int:
        try:
            num = int(raw)
        except ValueError:
            raise ParsingError(e_msg)
        else:
            if only_pos is True:
                if num <= 0:
                    raise ParsingError(e_msg)
        return num

    def connection_validate(self, line_lst: list, line_num: int) -> dict:
        con_data_dict = {}

        def metadata_validate():
            if line_lst[2].startswith("[") and line_lst[len(line_lst) - 1].endswith("]"):
                for data in line_lst[2:]:
                    data = data.strip("[]")
                    data = data.split("=")
                    if len(data) != 2:
                        raise ParsingError(
                            f"Connection metadata error on line {line_num}")
                    if data[0] != "max_link_capacity":
                        raise ParsingError(
                            f"Connection metadata error on line {line_num}")
                    max_link_capacity = self.parse_pos_int(
                        data[1], f"Connection metadata error on line {line_num}", True)
                    con_data_dict["max_link_capacity"] = max_link_capacity
            else:
                raise ParsingError(
                    f"Connection metadata error on line {line_num}")
        if self._nb_drones == 0:
            raise ParsingError(
                f"Connection validation before nb_drones defined on line {line_num}")
        if len(line_lst) < 2:
            raise ParsingError(f"Connection format error on line {line_num}")
        connection = line_lst[1].split("-")
        if len(connection) != 2:
            raise ParsingError(f"Connection format error on line {line_num}")
        con_data_dict["connection"] = line_lst[1]
        if len(line_lst) > 2:
            metadata_validate()
        return con_data_dict

    def nb_drones_validate(self, line_lst: list, line_num: int):
        if len(line_lst) != 2:
            raise ParsingError(
                f"Nb_drones format error on line {line_num}")
        nb_drones = self.parse_pos_int(
            line_lst[1], f"Nb_drones quantity error on line {line_num}", True)
        self._nb_drones = nb_drones


def test():
    parser = Parsing("01_linear_path.txt")
    try:
        parser.dispatcher()
    except ParsingError as e:
        print(e)


if __name__ == "__main__":
    test()
