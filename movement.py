from shared import *
from image_processing import ImageProcessor
import random
import hashlib
import input
import file_manager
import pickle


class RoomMap:
    _identifier: str
    _map: list
    _is_inside: bool

    def __init__(self):
        pass

    def _discover_around(self):
        orig_len_x = len(self._map)
        orig_len_y = len(self._map[0])

        if self._map[0] <= 0:
            self._add_new_row(True)
            self.my_pos = self._undo_move_pos(KEY_UP)
        if self.my_pos[0] + 1 >= orig_len_x:
            self._add_new_row(False)

        if self.my_pos[1] <= 0:
            self._add_new_col(True)
            self.my_pos = self._undo_move_pos(KEY_LEFT)
        if self.my_pos[1] + 1 >= orig_len_y:
            self._add_new_col(False)

    def _add_new_row(self, start):
        arr = ['n'] * len(self._map[0])
        if start:
            self._map.insert(0, arr)
        else:
            self._map.append(arr)

    def _add_new_col(self, start):
        val = 'n'
        if start:
            for i in range(0, len(self._map)):
                self._map[i].insert(0, val)
        else:
            for i in range(0, len(self._map)):
                self._map[i].append(val)

    def set_cell(self, pos, value):
        self._map[pos[0]][pos[1]] = value

    def _get_cell(self, pos):
        return self._map[pos[0]][pos[1]]

    def _is_known_position(self, pos):
        return self._get_cell(pos) != 'n'

    def _is_walkable(self, pos):
        return self._get_cell(pos) != 'w'

    def _is_wall(self, pos):
        return self._get_cell(pos) == 'w'

    def _is_spawn(self, pos):
        return self._get_cell(pos) == 's'

    def _is_door(self, pos):
        return self._get_cell(pos) == 'd'

    def _save(self):
        file_manager.save_map(self._identifier, self._map)

    def _print(self):
        print("Current map:")
        for x in self._map:
            for y in x:
                print(y, end=' ')
            print('')


class WallCollision:
    try_collide: bool
    direction = None

    def __init__(self, direction):
        self.direction = direction
        self.try_collide = False


class MovementAI:
    identifier: str
    _room_map = None

    _current_direction = None
    _is_inside: bool
    my_pos: tuple

    _wall_collision = None

    cur_route: list
    cur_route_step: int

    def __init__(self):
        self._current_direction = KEY_DOWN
        self.cur_route = list()
        self.cur_route_step = 0
        self._is_inside = True

    def setup(self, map_identifier=None):
        print('New AI started')

        if map_identifier is None:
            images = []
            for i in range(0, 10):
                images.append(ImageProcessor.grab_close_screen())

            used_image = None
            for image in images:
                image_hash = hashlib.md5(pickle.dumps(ImageProcessor.get_image_colors(image))).hexdigest()
                if file_manager.map_exists(image_hash):
                    self.identifier = image_hash
                    used_image = image
                    break

            if used_image is None:
                used_image = images[int(len(images) / 2) - 1]
                self.identifier = hashlib.md5(pickle.dumps(ImageProcessor.get_image_colors(used_image))).hexdigest()

            self._is_inside = self._check_is_inside(used_image)
        else:
            self.identifier = map_identifier

        was_inside = self._is_inside
        if self._load_map():
            print('Loaded known map:', self.identifier)
            found = False
            self.my_pos = (0, 0)
            for x in range(0, len(self._room_map)):
                for y in range(0, len(self._room_map[x])):
                    if self._room_map[x][y] == 's':
                        self.my_pos = (x, y)
                        found = True
                        break

                if found:
                    break
        else:
            print('Map unknown:', self.identifier)
            self._room_map = [['s']]

            self.my_pos = (0, 0)
            self._discover_around()

            if self._is_inside:
                if was_inside:
                    self._update_map('d', self._add_to_pos(self.my_pos, self._current_direction))
                else:
                    self._update_map('d', self._add_to_pos(self.my_pos, self._invert_direction(self._current_direction)))

        # NEEDS DETECTION FOR IN HOUSE OR OUTSIDE HOUSE
        self._current_direction = self._invert_direction(self._current_direction)

        self._wall_collision = None

    def next_move(self):
        if len(self.cur_route) > 0:
            self._current_direction = self.cur_route[self.cur_route_step]
            self.cur_route_step += 1
        else:
            self._check_map()

        self._move_pos()

        return self._current_direction

    def after_move(self):
        if not self.is_known_position(self.my_pos):
            self._discover_around()
            self._update_map('f')
            return 1

        if self._is_door(self.my_pos):
            return 2

        return 0

    def stuck(self):
        if self._wall_collision is None:
            self._wall_collision = WallCollision(self._current_direction)
        else:
            self._wall_collision.try_collide = False

        self._update_map('w')
        self.my_pos = self._undo_move_pos(self._current_direction)

    def map_changed(self):
        door_pos = self.my_pos

        if self._is_door(door_pos) or self._is_spawn(self.my_pos):
            return

        self._update_map('d')

    def trace_route_to(self, position):
        # Default map, skip
        if len(self._room_map) == 3 and len(self._room_map[0]) == 3:
            return []

        last_direction = self._invert_direction(self._current_direction)
        route = [last_direction]
        cur_pos = self._add_to_pos(position, last_direction)
        self._search_path(cur_pos, self._current_direction, route)

        route = [self._invert_direction(direction) for direction in route]
        route.reverse()

        return route

    def _search_path(self, cur_pos, last_direction, route):
        directions = [KEY_UP, KEY_LEFT, KEY_DOWN, KEY_RIGHT]
        directions.remove(last_direction)

        for direction in directions:
            new_pos = self._add_to_pos(cur_pos, direction)
            if not self.is_known_position(new_pos) or not self._is_walkable(new_pos):
                continue

            route.append(direction)
            if self._is_spawn(new_pos):
                return True

            self._search_path(new_pos, self._invert_direction(direction), route)
            return False

        return False

    def _check_map(self):
        # If we hit a wall in our direction
        if self._wall_collision is not None:
            if self._current_direction == self._invert_direction(self._wall_collision.direction):
                self._wall_collision = None
            elif self._wall_collision.try_collide:
                if not self.is_known_position(self._add_to_pos(self.my_pos, self._wall_collision.direction)):
                    self._current_direction = self._wall_collision.direction
                    self._wall_collision = None
                    return
                else:
                    self._wall_collision = None
            else:
                self._wall_collision.try_collide = True

        # If we can keep going
        pos_on_move = self._add_to_pos(self.my_pos, self._current_direction)
        if not self.is_known_position(pos_on_move):
            return

        # Attempt to select a direction we have not yet discovered
        directions = [KEY_UP, KEY_RIGHT, KEY_DOWN, KEY_LEFT]
        for direction in directions:
            pos = self.my_pos
            for i in range(0, 5):
                pos = self._add_to_pos(pos, direction)
                if self._is_wall(pos):
                    break

                if not self.is_known_position(pos):
                    self._current_direction = direction
                    return

        # Remove directions with walls
        for direction in directions:
            pos_on_move = self._add_to_pos(self.my_pos, direction)
            if self._is_wall(pos_on_move):
                directions.remove(direction)

        # Random direction
        print('Random direction')
        self._current_direction = directions[random.randrange(0, len(directions))]
        return

    def _move_pos(self):
        self.my_pos = self._add_to_pos(self.my_pos, self._current_direction)

    def _update_map(self, value, pos=None):
        if pos is None:
            self._room_map[self.my_pos[0]][self.my_pos[1]] = value
        else:
            self._room_map[pos[0]][pos[1]] = value
        self._save_map()

    def _load_map(self):
        self._room_map = file_manager.load_map(self.identifier)
        return len(self._room_map) > 0

    def _check_is_inside(self, image):
        return ImageProcessor.map_is_inside(image)

    def _undo_move_pos(self, direction):
        value = self._get_value_for(direction)
        return self.my_pos[0] + -value[0], self.my_pos[1] + -value[1]

    def _add_to_pos(self, pos, direction):
        value = self._get_value_for(direction)
        return pos[0] + value[0], pos[1] + value[1]

    def _invert_direction(self, direction):
        if direction == KEY_UP:
            return KEY_DOWN
        if direction == KEY_DOWN:
            return KEY_UP
        if direction == KEY_LEFT:
            return KEY_RIGHT
        if direction == KEY_RIGHT:
            return KEY_LEFT

        return KEY_UP

    def _get_value_for(self, direction):
        if direction == KEY_UP:
            return -1, 0
        if direction == KEY_DOWN:
            return 1, 0
        if direction == KEY_LEFT:
            return 0, -1
        if direction == KEY_RIGHT:
            return 0, 1

        return 0, 0


class Movement:
    _AI: MovementAI

    _current_checkpoint: int
    _routes_taken: dict
    _routes_to_take: dict

    skip_checks: bool

    def __init__(self, checkpoint, map_identifier=None):
        self._AI = MovementAI()
        self._AI.setup(map_identifier)
        self._current_checkpoint = checkpoint
        self._routes_taken = dict()
        self._routes_to_take = dict()

        self.skip_checks = False
        self._load_routes_to_checkpoint()

    def next_move(self):
        input.move(self._AI.next_move())
        ret = self._AI.after_move()

        if self._AI.cur_route_step >= len(self._AI.cur_route):
            self._change_route()
            return

        if ret == 0:  # Known position
            self.skip_checks = True
        elif ret == 1:  # Unknown position
            self.skip_checks = False
        elif ret == 2:  # Door
            self._add_route_taken()
            self.skip_checks = False

    def stuck(self):
        self._AI.stuck()

    def get_current_map(self):
        return self._AI.identifier

    def map_changed(self):
        if len(self._routes_to_take) < 1:
            self._add_route_taken()

        self._AI.map_changed()
        self._AI.setup()

        self._change_route()

    def checkpoint_reached(self, checkpoint):
        print('Reached checkpoint', checkpoint)

        if len(self._routes_to_take) < 1:
            self._add_route_taken()
            file_manager.save_routes_taken(checkpoint, self._routes_taken)

        self._routes_taken.clear()

        self._current_checkpoint = checkpoint + 1
        self._load_routes_to_checkpoint()

    def is_in_known_position(self):
        return self._AI.is_known_position(self._AI.my_pos)

    def _add_route_taken(self):
        if self._AI.identifier in self._routes_taken:
            return

        self._routes_taken[self._AI.identifier] = self._AI.trace_route_to(self._AI.my_pos)

    def _load_routes_to_checkpoint(self):
        self._routes_to_take = file_manager.load_routes_to_checkpoint(self._current_checkpoint)
        if self._routes_to_take:
            self._change_route()
        else:
            self._AI.cur_route.clear()
            self._AI.cur_route_step = 0
            self.skip_checks = False

    def _change_route(self):
        if len(self._routes_to_take) < 1:
            return

        if self._AI.identifier not in self._routes_to_take:
            self._AI.cur_route.clear()
            self._AI.cur_route_step = 0
            self.skip_checks = False
            return

        if self._AI.cur_route == self._routes_to_take[self._AI.identifier]:
            self._AI.cur_route.clear()
            self._AI.cur_route_step = 0
            self.skip_checks = False
            return

        self._AI.cur_route = self._routes_to_take[self._AI.identifier]
        self._AI.cur_route_step = 0
        self.skip_checks = True

        print('Route to checkpoint changed:', self._AI.cur_route)
