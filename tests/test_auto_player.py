import pytest

import auto_player


class TestAutoPlayer(object):
    _auto_player = None

    @pytest.fixture(autouse=True)
    def for_each_test(self):
        # Before
        self._auto_player = auto_player.AutoPlayer()
        # Run
        yield
        # After

    def test_start_should_start_new_game_when_save_not_exists(self, mocker):
        # Setup
        mock_game_save_exists = mocker.patch('file_manager.game_save_exists', return_value=False)
        mock_start_new_game = mocker.patch('auto_player.AutoPlayer._start_new_game')
        mock_load_game = mocker.patch('auto_player.AutoPlayer._load_game')

        # Exec
        self._auto_player.start()

        # Validate
        mock_start_new_game.assert_called_once()
        mock_load_game.assert_not_called()

    def test_start_should_load_game_when_save_exists(self, mocker):
        # Setup
        mock_game_save_exists = mocker.patch('file_manager.game_save_exists', return_value=True)
        mock_start_new_game = mocker.patch('auto_player.AutoPlayer._start_new_game')
        mock_load_game = mocker.patch('auto_player.AutoPlayer._load_game')

        # Exec
        self._auto_player.start()

        # Validate
        mock_start_new_game.assert_not_called()
        mock_load_game.assert_called_once()

    def test_start_new_game(self, mocker):
        # Setup
        expected_checkpoint = 1
        expected_needs_extra_checks = False

        mock_input_move = mocker.patch('input.move')
        mock_input_accept = mocker.patch('input.accept')

        # Exec
        self._auto_player._start_new_game()

        # Validate
        assert expected_checkpoint == self._auto_player._next_checkpoint
        assert expected_needs_extra_checks == self._auto_player._needs_extra_checks

    def test_get_game_data(self):
        # Setup
        expected_checkpoint = 5
        expected_map_identifier = 'test_map_identifier'
        expected_needs_extra_checks = True
        expected_data = [expected_checkpoint, expected_map_identifier, expected_needs_extra_checks]
        self._auto_player._next_checkpoint = expected_checkpoint
        self._auto_player._map_identifier = expected_map_identifier
        self._auto_player._needs_extra_checks = expected_needs_extra_checks

        # Exec
        data = self._auto_player._get_game_data()

        # Validate
        assert expected_data == data

    def test_save_game(self, mocker):
        # Setup
        data = [5, 'test_map_identifier', True]

        mock_get_game_data = mocker.patch('auto_player.AutoPlayer._get_game_data', return_value=data)
        mock_save_game_data = mocker.patch('file_manager.save_game_data')
        mock_input_save_game = mocker.patch('input.save_game')
        mock_input_start = mocker.patch('input.start')
        mock_input_cancel = mocker.patch('input.cancel')

        # Exec
        self._auto_player._save_game()

        # Validate
        mock_get_game_data.assert_called_once()
        mock_save_game_data.assert_called_once_with(data)
        mock_input_save_game.assert_called_once()
        mock_input_start.assert_called_once()
        mock_input_cancel.assert_called_once()

    def test_load_game(self, mocker):
        # Setup
        expected_checkpoint = 5
        expected_map_identifier = 'test_map_identifier'
        expected_needs_extra_checks = True
        save_file = [
            expected_checkpoint,
            expected_map_identifier,
            expected_needs_extra_checks
        ]

        mock_load_game_data = mocker.patch('file_manager.load_game_data', return_value=save_file)

        # Exec
        self._auto_player._load_game()

        # Validate
        assert expected_checkpoint == self._auto_player._next_checkpoint
        assert expected_map_identifier == self._auto_player._map_identifier
        assert expected_needs_extra_checks == self._auto_player._needs_extra_checks
