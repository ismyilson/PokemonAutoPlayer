import ai
import file_manager
import input


class AutoPlayer:
    def start(self) -> None:
        # TEST
        from image_processing import ImageProcessor
        import time
        movement_ai = ai.MovementAI()

        movement_ai.analyze_screen(ImageProcessor.grab_full_screen())
        movement_ai._print_map()
        while True:
            input.move(movement_ai.do_action())
            movement_ai.analyze_screen(ImageProcessor.grab_full_screen())
            movement_ai._print_map()
            time.sleep(0.5)

        return

        if file_manager.game_save_exists():
            self._load_game()
        else:
            self._start_new_game()

    def _start_new_game(self) -> None:
        self._next_checkpoint = 1
        self._needs_extra_checks = False

        input.move('w')
        input.move('w')
        input.move('w')
        input.accept()

        # self._accept_until('images/game_start.png')

        # self._movement = Movement(self._next_checkpoint)

    def _get_game_data(self) -> list:
        data = list()

        data.append(self._next_checkpoint)
        data.append(self._map_identifier)
        data.append(self._needs_extra_checks)

        return data

    def _save_game(self) -> None:
        file_manager.save_game_data(self._get_game_data())

        input.save_game()
        input.start()
        input.cancel()

    def _load_game(self) -> None:
        data = file_manager.load_game_data()

        self._next_checkpoint = data[0]
        self._map_identifier = data[1]
        self._needs_extra_checks = data[2]

        # self._movement = Movement(self._next_checkpoint, data[1])
