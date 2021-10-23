import enum


COLOR_CHATTING = (0, 248, 152)  # Chatting
COLOR_INPUT = (16, 112, 224)  # Input
COLOR_COMBAT = (248, 248, 216)  # Combat
COLOR_COMBAT_ENEMY_HEALTH = (80, 104, 88)  # Combat health

KEY_UP = 'w'
KEY_DOWN = 's'
KEY_RIGHT = 'd'
KEY_LEFT = 'a'
KEY_ACCEPT = 'z'
KEY_CANCEL = 'x'
KEY_ACCELERATE = 'space'
KEY_START = 'enter'
KEY_CTRL_LEFT = 'ctrlleft'
KEY_S = 's'
KEY_L = 'l'


class Direction(enum.Enum):
    UP = KEY_UP
    DOWN = KEY_DOWN
    RIGHT = KEY_RIGHT
    LEFT = KEY_LEFT

    @staticmethod
    def add_to_pos(pos, direction) -> tuple:
        if direction == Direction.UP:
            pos = (pos[0] - 1, pos[1])
        elif direction == Direction.DOWN:
            pos = (pos[0] + 1, pos[1])
        elif direction == Direction.RIGHT:
            pos = (pos[0], pos[1] + 1)
        elif direction == Direction.LEFT:
            pos = (pos[0], pos[1] - 1)

        return pos

    @staticmethod
    def invert_direction(direction):
        if direction == Direction.UP:
            return Direction.DOWN
        if direction == Direction.DOWN:
            return Direction.UP
        if direction == Direction.LEFT:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.LEFT

        return None


PLAYER_NAME = 'BOTTO'
PLAYER_NAME_SEQUENCE = [KEY_RIGHT, KEY_ACCEPT, KEY_RIGHT, KEY_DOWN, KEY_DOWN, KEY_ACCEPT, KEY_DOWN, KEY_LEFT, KEY_LEFT, KEY_ACCEPT, KEY_ACCEPT, KEY_RIGHT, KEY_RIGHT,
                        KEY_UP, KEY_ACCEPT]
