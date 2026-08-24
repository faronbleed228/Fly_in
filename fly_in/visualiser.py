from .parsing import Graph
from .factories import Zone, Connection, Drone
import pygame
import sys
import logging

logger = logging.getLogger(__name__)


class Visualiser():
    def __init__(self, graph: Graph, zone_list: list[Zone], drone_list: list[Drone], log_list: list[str]) -> None:
        self.graph = graph
        self.zone_list = zone_list
        self.start_zone = graph._start_zone
        self.drone_list = drone_list
        self.log_list = log_list

        self.width = 1280
        self.height = 720
        self.origin_width = 1280
        self.origin_height = 720

        self.margin = 200
        self.zone_dist = 30

        self.base_r = max(min(150/len(zone_list), 30), 15)
        self.scale_factor = 1

        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE)

        self.x_min = min(coord[0] for coord in self.graph._coordinates)
        self.y_min = min(coord[1] for coord in self.graph._coordinates)
        self.x_max = max(coord[0] for coord in self.graph._coordinates)
        self.y_max = max(coord[1] for coord in self.graph._coordinates)

        self.hide_name: bool = False

        self.drone_id_font: pygame.font.Font
        self.drone_count_font: pygame.font.Font
        self.name_font: pygame.font.Font
        self.menu_font: pygame.font.Font

    def main_loop(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        self.drone_count_font = pygame.font.Font('freesansbold.ttf', 20)
        self.drone_id_font = pygame.font.Font('freesansbold.ttf', 5)
        self.name_font = pygame.font.Font(
            'freesansbold.ttf', 10 * max(int(self.scale_factor), 1))
        self.menu_font = pygame.font.Font('freesansbold.ttf', 30)

        pygame.display.set_caption("Drone Simulation")

        while (True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    width, height = event.size
                    self.width = max(width, 640)
                    self.height = max(height, 480)
                    self.scale_factor = min(
                        self.width / self.origin_width, self.height / self.origin_height)
                    if height < 480 or width < 640:
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.hide_name = not self.hide_name

            self.screen.fill('azure3')
            self.draw_map()

            pygame.display.flip()
            clock.tick(60)

    def draw_map(self) -> None:
        self.draw_menu()
        self.draw_connections()
        self.draw_zones()
        self.render_drones(True)

    def to_screen(self, x: int, y: int) -> list[float]:
        if self.x_min == self.x_max:
            normalised_x = 0.5
        else:
            normalised_x = (x - self.x_min) / (self.x_max - self.x_min)
        if self.y_min == self.y_max:
            normalised_y = 0.5
        else:
            normalised_y = (y - self.y_min) / (self.y_max - self.y_min)
        logger.info(
            f"Normalised_y:{normalised_y}, Normalised_x: {normalised_x}")
        ret_x = self.margin + normalised_x * (self.width - self.margin * 2)
        ret_y = self.height - self.margin - \
            normalised_y * (self.height - self.margin * 2)
        return ([ret_x, ret_y])

    def draw_menu(self) -> None:
        menu_surface = pygame.surface.Surface((200, 200), pygame.SRCALPHA)
        menu_surface.fill((108, 92, 120, 75))
        self.screen.blit(menu_surface, (0, 0))
        controls_surface = self.menu_font.render(
            "N - hide/show zone names\nArrow right - one step forward\nArrow left - one step back", True, "black")
        self.screen.blit(controls_surface, (10, 10))

    def draw_zones(self) -> None:

        final_radius = self.base_r * self.scale_factor

        for zone in self.zone_list:
            start_end_scale = 0
            name_offset = 6
            logger.info(f"Drawing zone {zone._name}")
            x, y = self.to_screen(zone._x, zone._y)
            logger.info(f"x:{x}, y:{y}")
            color = self.get_color(zone)
            logger.info(f"Color: {color}")

            if zone._hub_type == "start_hub" or zone._hub_type == "end_hub":
                start_end_scale = 15
                pygame.draw.circle(
                    self.screen, color, (x + self.zone_dist, y), final_radius + start_end_scale)
            else:
                pygame.draw.circle(
                    self.screen, color, (x + self.zone_dist, y), final_radius)
            if self.hide_name is False:
                label_surface = self.name_font.render(
                    zone._name, True, 'white')
                rect = label_surface.get_rect()
                rect.center = (int(x + self.zone_dist),
                               int(y + final_radius + name_offset + start_end_scale))
                self.screen.blit(label_surface, rect)

    def draw_connections(self) -> None:

        done_links: list[Connection] = []
        for zone in self.zone_list:
            for connection in zone._zone_connections:
                if connection in done_links:
                    continue
                else:
                    done_links.append(connection)
                    start_x, start_y = self.to_screen(
                        connection.zone_a._x, connection.zone_a._y)
                    end_x, end_y = self.to_screen(
                        connection.zone_b._x, connection.zone_b._y)

                    pygame.draw.line(self.screen, 'darkgrey',
                                     (start_x+self.zone_dist,
                                      start_y),
                                     (end_x + self.zone_dist,
                                      end_y),)

    def render_drones(self, start: bool) -> None:
        x, y = self.to_screen(self.start_zone._x, self.start_zone._y)
        offset = 3
        if start is True:
            number = len(self.drone_list)

            drone_count = self.drone_count_font.render(
                str(number), True, "white")
            rect = drone_count.get_rect()
            rect.center = (int(x + self.zone_dist), int(y))
            self.screen.blit(drone_count, rect)

        for drone in self.graph._drones_lst:
            drone_label = self.drone_id_font.render(drone._id, True, "black")
            rect = drone_label.get_rect()
            rect.center = (int(x), int(y))
            drone_coords = ([x + offset, y + offset], [x+2 + offset])
            pygame.draw.rect(self.screen, "darkgrey", ([]))

    def get_color(self, zone: Zone) -> str:
        color = zone._color
        if color is None:
            color = 'black'
        try:
            pygame.Color(color)
        except ValueError:
            color = "black"
        return color
