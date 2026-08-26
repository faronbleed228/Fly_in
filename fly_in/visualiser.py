from .parsing import Graph
from .factories import Zone, Connection, Drone
from .simulation import Gamestate
import pygame
import sys
import logging

logger = logging.getLogger(__name__)


class Visualiser():
    def __init__(self, graph: Graph, zone_list: list[Zone], drone_list: list[Drone], game_state: list[Gamestate]) -> None:
        self.graph = graph
        self.zone_list = zone_list
        self.start_zone = graph._start_zone
        self.end_zone = graph.end_zone
        self.drone_list = drone_list
        self.game_state = game_state

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
        self.cur_turn = 0

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
            'freesansbold.ttf', 11 * max(int(self.scale_factor), 1))
        self.menu_font = pygame.font.Font('freesansbold.ttf', 12)

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
        self.render_drones()

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
        line_height = self.menu_font.get_linesize()
        ofset = 0
        swichers_list = [["N - hide/show zone names"],["Arrow right - one step forward"],["Arrow left - one step back"]]

        menu_surface = pygame.surface.Surface((200, 200), pygame.SRCALPHA)
        menu_surface.fill((108, 92, 120, 75))
        self.screen.blit(menu_surface, (0, 0))
        for line in swichers_list:
            line = str(line)
            line = line.strip("[']")
            self.put_text_outline(100,10,line, self.menu_font,0,ofset + line_height)
            ofset += 15

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
                self.put_text_outline(x,y,zone._name,self.name_font,self.zone_dist,(final_radius + name_offset + start_end_scale))

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

    def render_drones(self) -> None:
        snapshot = self.game_state[self.cur_turn].state_dict.items()
        zone_capacity = {zone:0 for zone in self.zone_list if zone is not self.start_zone and zone is not self.end_zone}
        start_count = 0
        end_count = 0
        for drone, pos in snapshot:
            if pos is self.start_zone:
                start_count+=1
            elif pos is self.end_zone:
                end_count+=1
            else:
                if isinstance(pos, Zone):
                    self.render_drone_zone(drone, pos, 4)
                elif isinstance(pos, Connection):
                    pass
        start_x, start_y = self.to_screen(self.start_zone._x, self.start_zone._y)
        end_x, end_y = self.to_screen(self.end_zone._x, self.end_zone._y)
        self.put_text_outline(start_x,start_y, str(start_count), self.drone_count_font, self.zone_dist)
        self.put_text_outline(end_x,end_y, str(end_count), self.drone_count_font, self.zone_dist)



    def render_drone_zone(self, drone:Drone,  zone:Zone, zone_cap:int) -> None:
        if zone_cap <4:
            pass
        else:
            zone_text = "+" + str(zone_cap)



    def get_color(self, zone: Zone) -> str:
        color = zone._color
        if color is None:
            color = 'black'
        try:
            pygame.Color(color)
        except ValueError:
            color = "black"
        return color

    def put_text_outline(self, x:int , y:int, input:str, font: pygame.font.Font, x_offset:int = 0,
                         y_offset:int = 0) -> None:
        text = font.render(input, True, "white")
        outline = font.render(input, True, (40,40,40))

        text_rect = text.get_rect(center=(x + x_offset, y + y_offset))

        for dx, dy in [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
                ]:

            outline_rect = text_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy

            self.screen.blit(outline, outline_rect)

        self.screen.blit(text, text_rect)
