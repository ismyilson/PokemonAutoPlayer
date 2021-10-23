import pytest

import ai


class TestMovementAI(object):
    _movement_ai = None

    @pytest.fixture(autouse=True)
    def for_each_test(self):
        # Before
        self._movement_ai = ai.MovementAI()
        # Run
        yield
        # After

    @pytest.mark.parametrize('direction, value, pos', [
        [
            ai.Direction.UP,
            ai.MapFlag.FREE,
            (0, 0)
        ],
        [
            ai.Direction.RIGHT,
            ai.MapFlag.WALL,
            (0, 1)
        ],
        [
            ai.Direction.DOWN,
            ai.MapFlag.PLAYER,
            (1, 0)
        ],
        [
            ai.Direction.LEFT,
            ai.MapFlag.SPAWN,
            (0, 0)
        ],
    ])
    def test_movement_ai_add_to_map(self, direction, value, pos):
        # Setup

        # Exec
        self._movement_ai._add_to_map(direction, value)

        # Validate
        assert self._movement_ai._get_map_value(pos) == value

    @pytest.mark.parametrize('room_map, my_pos, direction, expected_ret', [
        [
            [
                [ai.MapFlag.FREE + ai.MapFlag.PLAYER, ai.MapFlag.FREE, ai.MapFlag.UNKNOWN]
            ],
            (0, 0),
            ai.Direction.RIGHT,
            False
        ],
        [
            [
                [ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE + ai.MapFlag.PLAYER]
            ],
            (0, 2),
            ai.Direction.LEFT,
            False
        ],
        [
            [
                [ai.MapFlag.FREE + ai.MapFlag.PLAYER],
            ],
            (0, 0),
            ai.Direction.DOWN,
            False
        ],
        [
            [
                [ai.MapFlag.WALL],
                [ai.MapFlag.FREE],
                [ai.MapFlag.FREE + ai.MapFlag.PLAYER]
            ],
            (2, 0),
            ai.Direction.UP,
            True
        ],

    ])
    def test_movement_ai_direction_is_fully_discovered(self, room_map, my_pos, direction, expected_ret):
        # Setup
        self._movement_ai._room_map = room_map
        self._movement_ai._my_pos = my_pos

        # Exec
        ret = self._movement_ai._direction_is_fully_discovered(direction)

        # Validate
        assert expected_ret == ret

    @pytest.mark.parametrize('room_map,expected_ret', [
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            False
        ],
        [
            [
                [ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
            ],
            False
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            True
        ]
    ])
    def test_movement_ai_map_is_fully_discovered(self, room_map, expected_ret):
        # Setup
        self._movement_ai._room_map = room_map

        # Exec
        ret = self._movement_ai._map_is_fully_discovered()

        # Validate
        assert expected_ret == ret

    @pytest.mark.parametrize('room_map,my_pos,expected_pos', [
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            (1, 1),
            (0, 1)
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.FREE, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            (1, 1),
            (0, 2)
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            (1, 1),
            (0, 2)
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN],
            ],
            (2, 1),
            (1, 1)
        ]
    ])
    def test_movement_ai_get_next_move_pos(self, room_map, my_pos, expected_pos):
        # Setup
        self._movement_ai._room_map = room_map
        self._movement_ai._my_pos = my_pos

        # Exec
        pos = self._movement_ai._get_next_move_pos()

        # Validate
        assert pos == expected_pos

    @pytest.mark.parametrize('room_map, from_pos, to_pos, expected_route', [
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            (1, 1),
            (1, 3),
            [ai.Direction.RIGHT, ai.Direction.RIGHT]
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.FREE],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
            ],
            (1, 1),
            (0, 3),
            [ai.Direction.RIGHT, ai.Direction.RIGHT, ai.Direction.UP]
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL],
                [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.FREE],
            ],
            (1, 1),
            (2, 3),
            [ai.Direction.RIGHT, ai.Direction.RIGHT, ai.Direction.DOWN]
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL],
                [ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.UNKNOWN, ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL],
            ],
            (1, 2),
            (0, 0),
            [ai.Direction.LEFT, ai.Direction.LEFT, ai.Direction.UP]
        ],
        [
            [
                [ai.MapFlag.UNKNOWN, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.UNKNOWN],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.WALL],
                [ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE],
                [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.WALL, ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.WALL],
                [ai.MapFlag.WALL, ai.MapFlag.FREE + ai.MapFlag.PLAYER, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.FREE, ai.MapFlag.WALL],
            ],
            (4, 1),
            (1, 1),
            [ai.Direction.RIGHT, ai.Direction.RIGHT, ai.Direction.RIGHT, ai.Direction.UP, ai.Direction.UP, ai.Direction.LEFT, ai.Direction.LEFT,
             ai.Direction.UP, ai.Direction.LEFT]
        ]
    ])
    def test_movement_ai_trace_route_to(self, room_map, from_pos, to_pos, expected_route):
        # Setup
        self._movement_ai._room_map = room_map
        self._movement_ai._my_pos = from_pos

        # Exec
        route = self._movement_ai._trace_route_to(from_pos, to_pos)

        # Validate
        assert route == expected_route

    def test_movement_ai_get_non_wall_border(self):
        # Setup
        self._movement_ai._room_map = [
            [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.WALL],
            [ai.MapFlag.WALL, ai.MapFlag.PLAYER + ai.MapFlag.FREE, ai.MapFlag.WALL],
            [ai.MapFlag.WALL, ai.MapFlag.FREE, ai.MapFlag.WALL],
        ]
        expected_ret = (0, 1)

        # Exec
        ret = self._movement_ai._get_non_wall_border()

        # Validate
        assert ret == expected_ret

    @pytest.mark.parametrize('room_map, pos, direction', [
        [
            [
                [ai.MapFlag.FREE + ai.MapFlag.PLAYER, ai.MapFlag.FREE]
            ],
            (0, 0),
            ai.Direction.RIGHT
        ],
        [
            [
                [ai.MapFlag.FREE],
                [ai.MapFlag.FREE + ai.MapFlag.PLAYER]
            ],
            (1, 0),
            ai.Direction.UP
        ]
    ])
    def test_movement_ai_move(self, room_map, pos, direction):
        # Setup
        expected_pos = ai.Direction.add_to_pos(pos, direction)
        self._movement_ai._room_map = room_map
        self._movement_ai._my_pos = pos

        # Exec
        self._movement_ai._move(direction)

        # Validate
        assert expected_pos == self._movement_ai._my_pos
        assert self._movement_ai._get_map_value(pos) | ai.MapFlag.PLAYER
        assert self._movement_ai._get_map_value(expected_pos) & ai.MapFlag.PLAYER
