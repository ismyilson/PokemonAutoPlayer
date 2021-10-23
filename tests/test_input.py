import pytest

import input


class TestInput(object):
    def test_input_focus(self, mocker):
        # Setup
        expected_x = 600
        expected_y = 600
        mock_move_to = mocker.patch('pyautogui.moveTo')
        mock_click = mocker.patch('pyautogui.click')

        # Exec
        input.focus()

        # Validate
        mock_move_to.assert_called_once_with(expected_x, expected_y)
        mock_click.assert_called_once()

    def test_input_accept(self, mocker):
        # Setup
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.accept()

        # Validate
        mock_press_key.assert_called_once_with(input.KEY_ACCEPT)

    def test_input_hold_accept(self, mocker):
        # Setup
        mock_key_down = mocker.patch('pyautogui.keyDown')

        # Exec
        input.hold_accept()

        # Validate
        mock_key_down.assert_called_once_with(input.KEY_ACCEPT)

    def test_input_stop_hold_accept(self, mocker):
        # Setup
        mock_key_up = mocker.patch('pyautogui.keyUp')

        # Exec
        input.stop_hold_accept()

        # Validate
        mock_key_up.assert_called_once_with(input.KEY_ACCEPT)

    def test_input_cancel(self, mocker):
        # Setup
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.cancel()

        # Validate
        mock_press_key.assert_called_once_with(input.KEY_CANCEL)

    def test_input_start(self, mocker):
        # Setup
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.start()

        # Validate
        mock_press_key.assert_called_once_with(input.KEY_START)

    def test_input_accelerate(self, mocker):
        # Setup
        mock_key_down = mocker.patch('pyautogui.keyDown')

        # Exec
        input.accelerate()

        # Validate
        mock_key_down.assert_called_once_with(input.KEY_ACCELERATE)

    def test_input_deaccelerate(self, mocker):
        # Setup
        mock_key_up = mocker.patch('pyautogui.keyUp')

        # Exec
        input.deaccelerate()

        # Validate
        mock_key_up.assert_called_once_with(input.KEY_ACCELERATE)

    @pytest.mark.parametrize('direction', [
        [
            input.KEY_UP
        ],
        [
            input.KEY_DOWN
        ],
        [
            input.KEY_LEFT
        ],
        [
            input.KEY_RIGHT
        ],
    ])
    def test_input_move(self, mocker, direction):
        # Setup
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.move(direction)

        # Validate
        mock_press_key.assert_called_once_with(direction)

    def test_input_key_up_all(self, mocker):
        # Setup
        mock_key_up = mocker.patch('pyautogui.keyUp')
        expected_calls = list()
        used_keys = [input.KEY_ACCEPT, input.KEY_CANCEL, input.KEY_START, input.KEY_ACCELERATE, input.KEY_UP, input.KEY_RIGHT, input.KEY_DOWN,
                     input.KEY_LEFT, input.KEY_CTRL_LEFT, input.KEY_S, input.KEY_L]
        for key in used_keys:
            expected_calls.append(mocker.call(key))

        # Exec
        input.key_up_all()

        # Validate
        assert len(expected_calls) == mock_key_up.call_count
        mock_key_up.assert_has_calls(expected_calls, any_order=True)

    def test_input_save_game(self, mocker):
        # Setup
        mock_hold = mocker.patch('pyautogui.hold')
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.save_game()

        # Validate
        mock_hold.assert_called_once_with(input.KEY_CTRL_LEFT)
        mock_press_key.assert_called_once_with(input.KEY_S)

    def test_input_load_game(self, mocker):
        # Setup
        mock_hold = mocker.patch('pyautogui.hold')
        mock_press_key = mocker.patch('input._press_key')

        # Exec
        input.load_game()

        # Validate
        mock_hold.assert_called_once_with(input.KEY_CTRL_LEFT)
        mock_press_key.assert_called_once_with(input.KEY_L)

    @pytest.mark.parametrize('key', [
        [
            input.KEY_UP
        ],
        [
            input.KEY_CTRL_LEFT
        ],
        [
            input.KEY_S
        ],
    ])
    def test_input_press_key(self, mocker, key):
        # Setup
        expected_wait_time = 0.05
        mock_key_down = mocker.patch('pyautogui.keyDown')
        mock_key_up = mocker.patch('pyautogui.keyUp')
        mock_time = mocker.patch('time.sleep')

        # Exec
        input._press_key(key)

        # Validate
        mock_key_down.assert_called_once_with(key)
        mock_time.assert_called_once_with(expected_wait_time)
        mock_key_up.assert_called_once_with(key)
