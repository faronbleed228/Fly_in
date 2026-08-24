from .parsing import Graph
from .factories import Zone, Connection
import pygame
import sys
import logging

logger = logging.getLogger(__name__)


class Visualiser():
    def __init__(self, graph: Graph, zone_list: list[Zone]) -> None:
        self.graph = graph
        self.zone_list = zone_list

        self.width = 1280
        self.height = 720
        self.origin_width = 1280
        self.origin_height = 720

        self.margin = 200
        self.zone_dist = 30

        self.base_r = max(min(150/len(zone_list), 30), 10)
        self.scale_factor = 1

        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE)

        self.x_min = min(coord[0] for coord in self.graph._coordinates)
        self.y_min = min(coord[1] for coord in self.graph._coordinates)
        self.x_max = max(coord[0] for coord in self.graph._coordinates)
        self.y_max = max(coord[1] for coord in self.graph._coordinates)

    def main_loop(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
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

            self.screen.fill('azure3')
            self.draw_map()

            pygame.display.flip()
            clock.tick(60)

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

    def draw_map(self) -> None:
        self.draw_connections()
        self.draw_zones()

    def draw_zones(self) -> None:

        final_radius = self.base_r * self.scale_factor
        font = pygame.font.Font(
            'freesansbold.ttf', 10 * max(int(self.scale_factor), 1))
        for zone in self.zone_list:
            logger.info(f"Drawing zone {zone._name}")
            x, y = self.to_screen(zone._x, zone._y)
            logger.info(f"x:{x}, y:{y}")
            color = self.get_color(zone)
            logger.info(f"Color: {color}")
            label_surface = font.render(zone._name, True, 'white')
            pygame.draw.circle(
                self.screen, color, (x + self.zone_dist, y), final_radius)
            rect = label_surface.get_rect()
            rect.center = (int(x + self.zone_dist), int(y + final_radius + 6))
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

    def get_color(self, zone: Zone) -> str:
        color = zone._color
        if color is None:
            color = 'black'
        try:
            pygame.Color(color)
        except ValueError:
            color = "black"
        return color
