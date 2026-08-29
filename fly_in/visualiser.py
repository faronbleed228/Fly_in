from .parsing import Graph
from .factories import Zone, Connection, Drone
from .simulation import Gamestate
import pygame
import sys
import logging

logger = logging.getLogger(__name__)


class Visualiser():
    def __init__(self, graph: Graph, zone_list: list[Zone],
                 drone_list: list[Drone], game_state: list[Gamestate]) -> None:
        """Initializes the Pygame-based GUI visualizer for the drone network.

        Args:
            graph: The network graph topology containing zones and connections.
            zone_list: List of all zones to be drawn.
            drone_list: List of drones in the simulation.
            game_state: Chronological sequence of simulation state snapshots.
        """
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
        self.scale_factor: float = 1.0

        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE)

        self.x_min = min(coord[0] for coord in self.graph._coordinates)
        self.y_min = min(coord[1] for coord in self.graph._coordinates)
        self.x_max = max(coord[0] for coord in self.graph._coordinates)
        self.y_max = max(coord[1] for coord in self.graph._coordinates)

        self.hide_name: bool = False
        self.is_playing = False
        self.cur_time: int
        self.last_turn_time: int
        self.turn_speed: int = 1000
        self.cur_turn = 0

        self.drone_id_font: pygame.font.Font
        self.drone_count_font: pygame.font.Font
        self.name_font: pygame.font.Font
        self.menu_font: pygame.font.Font

    def main_loop(self) -> None:
        """Initializes the Pygame context
        and runs the main interactive render loop."""
        pygame.init()
        clock = pygame.time.Clock()
        self.drone_count_font = pygame.font.Font('freesansbold.ttf', 20)
        self.drone_id_font = pygame.font.Font('freesansbold.ttf', 8)
        self.name_font = pygame.font.Font(
            'freesansbold.ttf', 11 * max(int(self.scale_factor), 1))
        self.menu_font = pygame.font.Font('freesansbold.ttf', 12)

        pygame.display.set_caption("Drone Simulation")

        while (True):
            self.event_handling()

            self.replay()

            self.screen.fill('azure3')
            self.draw_map()

            pygame.display.flip()
            clock.tick(60)

    def event_handling(self) -> None:
        """Handles user inputs including
        keyboard shortcuts and window resizing events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                width, height = event.size
                self.width = max(width, 1280)
                self.height = max(height, 720)
                self.scale_factor = min(
                    self.width / self.origin_width,
                    self.height / self.origin_height)
                if height < 720 or width < 1280:
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_playing = not self.is_playing
                    self.last_turn_time = pygame.time.get_ticks()
                elif event.key == pygame.K_n:
                    self.hide_name = not self.hide_name
                elif event.key == pygame.K_RIGHT:
                    if (self.cur_turn != len(self.game_state) - 1
                            and self.is_playing is False):
                        self.cur_turn += 1
                elif event.key == pygame.K_LEFT:
                    if self.cur_turn != 0 and self.is_playing is False:
                        self.cur_turn -= 1
                elif event.key == pygame.K_b:
                    self.cur_turn = 0
                elif event.key == pygame.K_DOWN:
                    self.turn_speed += 200
                elif event.key == pygame.K_UP and self.turn_speed != 200:
                    self.turn_speed -= 200

    def replay(self) -> None:
        """Advances the simulation turn
        automatically when replay mode is active."""
        if self.is_playing is True:
            self.cur_time = pygame.time.get_ticks()
            if self.cur_turn == len(self.game_state) - 1:
                self.is_playing = False
            elif self.cur_time - self.last_turn_time > self.turn_speed:
                self.cur_turn += 1
                self.last_turn_time = pygame.time.get_ticks()

    def draw_map(self) -> None:
        """Renders the entire scene including
        the control menu, links, zones, and drones."""
        self.draw_menu()
        self.draw_connections()
        self.draw_zones()
        self.render_drones()

    def to_screen(self, x: int, y: int) -> list[float]:
        """Maps graph space coordinates (x, y)
        to window screen pixel coordinates.

        Args:
            x: Raw X-coordinate in graph space.
            y: Raw Y-coordinate in graph space.

        Returns:
            A list containing normalized [screen_x, screen_y] coordinates.
        """
        if self.x_min == self.x_max:
            normalised_x = 0.5
        else:
            normalised_x = (x - self.x_min) / (self.x_max - self.x_min)
        if self.y_min == self.y_max:
            normalised_y = 0.5
        else:
            normalised_y = (y - self.y_min) / (self.y_max - self.y_min)
        ret_x = self.margin + normalised_x * (self.width - self.margin * 2)
        ret_y = self.height - self.margin - \
            normalised_y * (self.height - self.margin * 2)
        return ([ret_x, ret_y])

    def draw_menu(self) -> None:
        """Draws the hotkey control and navigation menu overlay."""
        line_height = self.menu_font.get_linesize()
        ofset = 0
        swichers_list = [["N - hide/show zone names"],
                         ["Arrow RIGHT - one step forward"],
                         ["Arrow LEFT - one step back"],
                         ["Space - start/stop replay"],
                         ["B - go to turn 0"], ["Arrow UP - speed up"],
                         ["Arrow DOWN - slow down"]]

        menu_surface = pygame.surface.Surface((200, 150), pygame.SRCALPHA)
        menu_surface.fill((108, 92, 120, 75))
        self.screen.blit(menu_surface, (0, 0))
        for line in swichers_list:
            line_str = str(line)
            line_str = line_str.strip("[']")
            self.put_text_outline(
                100, 10, line_str, self.menu_font, 0, ofset + line_height)
            ofset += 15

    def draw_zones(self) -> None:
        """Renders all zones as circles and optionally displays their names."""
        final_radius = self.base_r * self.scale_factor

        for zone in self.zone_list:
            start_end_scale = 0
            name_offset = 6
            x, y = self.to_screen(zone._x, zone._y)
            color = self.get_color(zone)

            if zone._hub_type == "start_hub" or zone._hub_type == "end_hub":
                start_end_scale = 15
                pygame.draw.circle(
                    self.screen, color, (x + self.zone_dist, y),
                    final_radius + start_end_scale)
            else:
                pygame.draw.circle(
                    self.screen, color, (x + self.zone_dist, y), final_radius)
            if self.hide_name is False:
                self.put_text_outline(int(x), int(y), zone._name,
                                      self.name_font,
                                      self.zone_dist,
                                      int(final_radius + name_offset +
                                          start_end_scale))

    def draw_connections(self) -> None:
        """Draws the connection links between zones as lines on the screen."""
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
        """Renders drones at their current
        positions for the active turn snapshot."""
        snapshot = self.game_state[self.cur_turn].state_dict.items()
        zone_capacity = {
            zone: 0 for zone in self.zone_list if zone
            is not self.start_zone and zone is not self.end_zone}
        start_count = 0
        end_count = 0

        for drone, pos in snapshot:
            if pos is self.start_zone:
                start_count += 1
            elif pos is self.end_zone:
                end_count += 1
            else:
                if isinstance(pos, Zone):
                    zone_capacity[pos] += 1
                elif isinstance(pos, Connection):
                    self.render_drone_connection(drone, pos)

        for drone, pos in snapshot:
            if pos is self.start_zone or pos is self.end_zone:
                continue
            elif isinstance(pos, Zone):
                self.render_drone_zone(drone, pos, zone_capacity[pos])
            elif isinstance(pos, Connection):
                pass

        start_x, start_y = self.to_screen(
            self.start_zone._x, self.start_zone._y)
        end_x, end_y = self.to_screen(self.end_zone._x, self.end_zone._y)
        self.put_text_outline(int(start_x), int(start_y), str(
            start_count), self.drone_count_font, self.zone_dist)
        self.put_text_outline(int(end_x), int(end_y), str(
            end_count), self.drone_count_font, self.zone_dist)

    def render_drone_connection(self, drone: Drone,
                                connection: Connection) -> None:
        """Draws a drone positioned in transit on a connection link.

        Args:
            drone: The drone in transit.
            connection: The connection link on which the drone is located.
        """
        zone_a = connection.zone_a
        zone_b = connection.zone_b
        zone_a_x, zone_a_y = self.to_screen(zone_a._x, zone_a._y)
        zone_b_x, zone_b_y = self.to_screen(zone_b._x, zone_b._y)
        x = zone_a_x + self.zone_dist + ((zone_a_x - zone_b_x) / 2 * -1)
        y = zone_a_y + ((zone_a_y - zone_b_y) / 2 * -1)
        pygame.draw.polygon(self.screen, "azure4", ((
            x - 10, y), (x, y - 10), (x + 10, y), (x, y + 10)))
        self.put_text_outline(int(x), int(y), drone._id,
                              self.drone_id_font, 0, 0)

    def render_drone_zone(self, drone: Drone,
                          zone: Zone, zone_cap: int) -> None:
        """Draws a drone positioned around a zone or
        an overflow indicator if capacity is exceeded.

        Args:
            drone: The drone to render.
            zone: The zone in which the drone is located.
            zone_cap: Remaining count of drones in this zone left to render.
        """
        directions = [[-1, 0], [0, -1], [1, 0]]
        zone_x, zone_y = self.to_screen(zone._x, zone._y)
        cur_radius = self.base_r * (self.scale_factor) + 15
        dron_counter = 0
        while zone_cap != 0:
            if dron_counter != 3:
                dir_x, dir_y = directions[dron_counter]
                x = self.zone_dist + zone_x + (dir_x * cur_radius)
                y = zone_y + (dir_y * cur_radius)

                pygame.draw.polygon(self.screen, "azure4", ((
                    x - 10, y), (x, y - 10), (x + 10, y), (x, y + 10)))
                self.put_text_outline(
                    int(x), int(y), drone._id, self.drone_id_font, 0, 0)
                dron_counter += 1
                zone_cap -= 1
            else:
                zone_text = "+" + str(zone_cap)
                self.put_text_outline(
                    int(zone_x), int(zone_y), zone_text,
                    self.menu_font, self.zone_dist, 0)
                return

    def get_color(self, zone: Zone) -> str:
        """Resolves the valid Pygame color identifier for a given zone.

        Args:
            zone: The zone whose display color is needed.

        Returns:
            A string representing a valid Pygame color name.
        """
        color = zone._color
        if color is None:
            color = 'black'
        try:
            pygame.Color(color)
        except ValueError:
            color = "black"
        return color

    def put_text_outline(self, x: int, y: int, input: str,
                         font: pygame.font.Font, x_offset: int = 0,
                         y_offset: int = 0) -> None:
        """Renders text with a dark outline for improved readability.

        Args:
            x: Target center X-coordinate.
            y: Target center Y-coordinate.
            input: Text string to render.
            font: Pygame Font object used for rendering.
            x_offset: Additional horizontal offset.
            y_offset: Additional vertical offset.
        """
        text = font.render(input, True, "white")
        outline = font.render(input, True, (40, 40, 40))

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

    def quit(self) -> None:
        pygame.quit()
