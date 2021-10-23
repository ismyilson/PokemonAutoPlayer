import pytest
import os

import file_manager


class TestFileManager(object):
    @pytest.fixture(autouse=True)
    def for_each_test(self):
        # Before
        os.makedirs(os.path.dirname(file_manager.PATH_GAME_DATA))
        # Run
        yield
        # After
        os.rmdir(os.path.dirname(file_manager.PATH_GAME_DATA))

    def test_file_manager_save_game_data(self):
        # Setup
        game_data = []

        # Exec
        file_manager.save_game_data(game_data)

        # Validate
        assert os.path.isfile(file_manager.PATH_GAME_DATA)

        os.remove(file_manager.PATH_GAME_DATA)

    def test_file_manager_load_game_data(self):
        # Setup
        expected_checkpoint = 5
        expected_map_identifier = 'test_map_identifier'
        expected_needs_extra_checks = True
        game_data = [
            expected_checkpoint,
            expected_map_identifier,
            expected_needs_extra_checks
        ]

        file_manager.save_game_data(game_data)

        # Exec
        data = file_manager.load_game_data()

        # Validate
        assert expected_checkpoint in data
        assert expected_map_identifier in data
        assert expected_needs_extra_checks in data

        os.remove(file_manager.PATH_GAME_DATA)

    def test_file_manager_game_save_exists_should_return_false_when_not_exists(self):
        # Exec
        ret = file_manager.game_save_exists()

        # Validate
        assert ret is False

    def test_file_manager_game_save_exists_should_return_true_when_exists(self):
        # Setup
        game_data = []
        file_manager.save_game_data(game_data)

        # Exec
        ret = file_manager.game_save_exists()

        # Validate
        assert ret is True

        os.remove(file_manager.PATH_GAME_DATA)
