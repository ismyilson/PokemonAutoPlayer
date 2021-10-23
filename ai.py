from image_processing import ImageProcessor
from shared import *
import abc
import enum


class MapFlag(enum.IntFlag):
    UNKNOWN = 1
    FREE = 2
    WALL = 4
    SPAWN = 8
    DOOR = 16
    PLAYER = 32


class AI(abc.ABC):
    @abc.abstractmethod
    def analyze_screen(self, screen) -> None:

        return

    @abc.abstractmethod
    def set_overlay(self, overlay_image) -> None:
        return

    @abc.abstractmethod
    def do_action(self):
        return


class MovementAI(AI):
    _CHAR_POS = (4, 7)

    _room_map: list
    _my_pos: tuple

    _route_to_pos: list

    def __init__(self):
        self._room_map = [[MapFlag.FREE + MapFlag.SPAWN + MapFlag.PLAYER]]
        self._my_pos = (0, 0)

        self._route_to_pos = []

    def analyze_screen(self, screen) -> None:
        tiles = ImageProcessor.make_tiles(screen, size=(128, 106))

        # Grab the non_wall_tiles
        non_wall_tiles = []
        for tile in tiles:
            colors = ImageProcessor.get_image_colors(tile[1])
            if not colors or not len(colors) == 1 or not colors[0][1] == (0, 0, 0):
                non_wall_tiles.append(tile)

        # Calculate the room that we see
        data = dict()
        max_y = int(max(non_wall_tiles, key=lambda x: int(x[0][1] / 106))[0][1] / 106)  # Max col
        min_y = int(min(non_wall_tiles, key=lambda x: int(x[0][1] / 106))[0][1] / 106)  # Min col
        max_x = int(max(non_wall_tiles, key=lambda x: int(x[0][0] / 128))[0][0] / 128)  # Max row
        min_x = int(min(non_wall_tiles, key=lambda x: int(x[0][0] / 128))[0][0] / 128)  # Min row

        if max_x >= self._CHAR_POS[1]:  # Direction.RIGHT
            val = max_x - self._CHAR_POS[1]
            diff = (len(self._room_map[0]) - 2) - self._my_pos[1]

            if diff <= val:
                data[Direction.RIGHT] = val
        if min_x <= self._CHAR_POS[1]:  # Direction.LEFT
            val = self._CHAR_POS[1] - min_x
            diff = self._my_pos[1] - val

            if diff <= val:
                data[Direction.LEFT] = val
        if max_y > self._CHAR_POS[0]:  # Direction.DOWN
            val = max_y - self._CHAR_POS[0]
            diff = (len(self._room_map) - 1) - self._my_pos[0]

            if diff <= val:
                data[Direction.DOWN] = val - 1
        if min_y < self._CHAR_POS[0]:  # Direction.UP
            val = self._CHAR_POS[0] - min_y
            diff = self._my_pos[0]

            if diff <= val:
                data[Direction.UP] = val

        for item in data.items():
            if self._direction_is_fully_discovered(item[0]):  # We already discovered this entire direction
                continue

            pos = Direction.add_to_pos(self._my_pos, item[0])
            for i in range(0, item[1]):
                val = self._get_map_value(pos)
                if val is None:
                    self._add_to_map(item[0], MapFlag.FREE)
                else:
                    if val & MapFlag.UNKNOWN:
                        self._set_map_value(pos, MapFlag.FREE)
                pos = Direction.add_to_pos(pos, item[0])

            if (item[0] == Direction.RIGHT or item[0] == Direction.LEFT) and item[1] < self._CHAR_POS[1]:
                if item[0] == Direction.RIGHT:
                    pos = (self._my_pos[0], self._my_pos[1] + item[1] + 1)
                else:
                    pos = (self._my_pos[0], self._my_pos[1] - item[1] - 1)

                if self._get_map_value(pos) is None:
                    self._add_to_map(item[0], MapFlag.WALL)
                else:
                    self._set_map_value(pos, MapFlag.WALL)

            if item[0] == Direction.UP and item[1] < self._CHAR_POS[0]:
                pos = (self._my_pos[0] - item[1], self._my_pos[1])
                if self._get_map_value(pos) is None:
                    self._add_to_map(item[0], MapFlag.WALL)
                else:
                    # Special case: when we see a wall up, the tile before it is also wall (unpassable)
                    self._set_map_value(pos, MapFlag.WALL)
                    self._set_map_value((pos[0] + 1, pos[1]), MapFlag.WALL)

            if item[0] == Direction.DOWN and item[1] < self._CHAR_POS[0]:
                pos = (self._my_pos[0] + item[1] + 1, self._my_pos[1])

                if self._get_map_value(pos) is None:
                    self._add_to_map(item[0], MapFlag.WALL)
                else:
                    self._set_map_value(pos, MapFlag.WALL)

        return

    def _add_to_map(self, direction, value):
        if direction == Direction.UP:
            self._room_map.insert(0, [MapFlag.UNKNOWN for col in self._room_map[0]])
            self._set_map_value((0, self._my_pos[1]), value)
        elif direction == Direction.DOWN:
            self._room_map.append([MapFlag.UNKNOWN for col in self._room_map[0]])
            self._set_map_value((len(self._room_map) - 1, self._my_pos[1]), value)
        elif direction == Direction.LEFT:
            for row in self._room_map:
                if row == self._room_map[self._my_pos[0]]:
                    self._room_map[self._my_pos[0]].insert(0, value)
                else:
                    row.insert(0, MapFlag.UNKNOWN)
        elif direction == Direction.RIGHT:
            for row in self._room_map:
                if row == self._room_map[self._my_pos[0]]:
                    self._room_map[self._my_pos[0]].append(value)
                else:
                    row.append(MapFlag.UNKNOWN)

        self._adjust_pos(direction)

    def _set_map_value(self, pos, value):
        self._room_map[pos[0]][pos[1]] = value

    def _get_map_value(self, pos):
        try:
            if pos[0] < 0 or pos[1] < 0:
                return None

            if pos[0] > len(self._room_map) or pos[1] > (len(self._room_map[0])):
                return None

            return self._room_map[pos[0]][pos[1]]
        except IndexError:
            return None

    def _adjust_pos(self, direction):
        if direction == Direction.UP:
            self._my_pos = (self._my_pos[0] + 1, self._my_pos[1])
        elif direction == Direction.LEFT:
            self._my_pos = (self._my_pos[0], self._my_pos[1] + 1)

    def _print_map(self):
        print('Current map:')
        to_print = []
        for row in self._room_map:
            row_data = []
            for cell in row:
                flags = list()
                for flag in MapFlag:
                    flags.append(flag.name) if cell & flag else None
                row_data.append('/'.join(flags).ljust(22))
            to_print.append(''.join(row_data))

        print('\n'.join(to_print))
        return

    def set_overlay(self, overlay_image) -> None:
        return

    def do_action(self):
        # If we have a current route to pos
        if len(self._route_to_pos) > 0:
            # Make sure we did not (accidentally) discover the position
            pos = self._my_pos
            for direction in self._route_to_pos:
                pos = Direction.add_to_pos(pos, direction)

            if self._get_map_value(pos) & MapFlag.UNKNOWN:
                # Make sure we can move to the direction
                direction = self._route_to_pos[0]
                if self._get_map_value(Direction.add_to_pos(self._my_pos, direction)) & MapFlag.FREE:
                    self._route_to_pos.pop(0)
                    self._move(direction)
                    return direction.value

            self._route_to_pos.clear()

        # If map isn't all discovered yet we try to find more stuff
        if not self._map_is_fully_discovered():
            pos = self._get_next_move_pos()
            print('Tracing route to:', pos)
            self._route_to_pos = self._trace_route_to(self._my_pos, pos)
            print('Route:', self._route_to_pos)

            direction = self._route_to_pos[0]
            self._route_to_pos.pop(0)
            self._move(direction)
            return direction.value

        return None

    def _map_is_fully_discovered(self) -> bool:
        # Map is discovered when we know all the walls
        for x in range(0, len(self._room_map)):
            for y in range(0, len(self._room_map[x])):
                if (x == 0 and y == 0) or (x == 0 and y == len(self._room_map[x]) - 1):  # Skip first row left and right corner
                    continue

                if (x == len(self._room_map) - 1 and y == 0) or (x == len(self._room_map) - 1 and y == len(self._room_map[x]) - 1):  # Skip last row left and right corner
                    continue

                if x == 0 or x == len(self._room_map) - 1:  # If first or last row, must be walls
                    if not self._get_map_value((x, y)) & MapFlag.WALL:
                        return False

                if y == 0 or y == len(self._room_map[x]):  # If first or last column, must be walls
                    if not self._get_map_value((x, y)) & MapFlag.WALL:
                        return False

                if self._get_map_value((x, y)) & MapFlag.UNKNOWN:  # Anything else, only req is not to be unknown
                    return False

        return True

    def _direction_is_fully_discovered(self, direction):
        pos = Direction.add_to_pos(self._my_pos, direction)
        val = self._get_map_value(pos)

        while val is not None:
            if val & MapFlag.UNKNOWN:
                return False

            if val & MapFlag.WALL:
                return True

            pos = Direction.add_to_pos(pos, direction)
            val = self._get_map_value(pos)

        return False

    def _get_next_move_pos(self):
        cur_pos = self._my_pos

        move_to = self._get_nearby_unknown(cur_pos, None, 0)
        if move_to:
            return move_to

        move_to = self._get_non_wall_border()
        if move_to:
            return move_to

    def _get_nearby_unknown(self, pos, coming_from, iteration):
        nearby = self._get_nearby(pos)
        nearby_useless = 0

        if self._get_map_value(pos) is None:
            return None

        if iteration >= 5:
            return None

        for nearby_pos, nearby_val in nearby:
            if not nearby_val:
                nearby_useless += 1
                continue

            if nearby_val & MapFlag.WALL:
                nearby_useless += 1
                continue

            if nearby_val & MapFlag.UNKNOWN and self._is_accessible(nearby_pos):
                return nearby_pos

        if nearby_useless == len(Direction):
            return None

        for direction in Direction:
            if direction == coming_from:
                continue

            iteration += 1
            val = self._get_nearby_unknown(Direction.add_to_pos(pos, direction), Direction.invert_direction(direction), iteration)
            if val is not None:
                return val

    def _get_nearby(self, pos):
        nearby = []

        for direction in Direction:
            new_pos = Direction.add_to_pos(pos, direction)
            nearby.append((new_pos, self._get_map_value(new_pos)))

        return nearby

    def _get_non_wall_border(self):
        for x in range(0, len(self._room_map)):
            for y in range(0, len(self._room_map[x])):
                if (x == 0 and y == 0) or (x == 0 and y == len(self._room_map[x]) - 1):  # Skip first row left and right corner
                    continue

                if (x == len(self._room_map) - 1 and y == 0) or (x == len(self._room_map) - 1 and y == len(self._room_map[x]) - 1):  # Skip last row left and right corner
                    continue

                val = self._get_map_value((x, y))
                if not val & MapFlag.WALL:
                    return x, y

        return None

    def _trace_route_to(self, from_pos, to_pos):
        route = []
        self._search_path(from_pos, to_pos, None, route, 0)
        route.reverse()

        return route

    def _search_path(self, cur_pos, to_pos, last_direction, route, iteration):
        print('Search path', cur_pos, to_pos)
        if cur_pos == to_pos:
            return True

        # First check if we have the point nearby
        for direction in Direction:
            new_pos = Direction.add_to_pos(cur_pos, direction)
            if to_pos == new_pos:
                route.append(direction)
                return True

        if iteration >= 5:
            return False

        # We do not have the point nearby so keep searching
        for direction in Direction:
            if direction == last_direction:
                continue

            new_pos = Direction.add_to_pos(cur_pos, direction)
            val = self._get_map_value(new_pos)

            if new_pos == to_pos:
                route.append(direction)
                return True

            if not val:
                continue

            if not val & MapFlag.FREE:
                continue

            iteration += 1
            if self._search_path(new_pos, to_pos, Direction.invert_direction(direction), route, iteration):
                route.append(direction)
                return True

        return False

    def _is_accessible(self, pos):
        for direction in Direction:
            new_pos = Direction.add_to_pos(pos, direction)
            val = self._get_map_value(new_pos)
            if val and val & MapFlag.FREE:
                return True

        return False

    def _move(self, direction):
        self._set_map_value(self._my_pos, self._get_map_value(self._my_pos) - MapFlag.PLAYER)
        self._my_pos = Direction.add_to_pos(self._my_pos, direction)
        self._set_map_value(self._my_pos, self._get_map_value(self._my_pos) + MapFlag.PLAYER)
