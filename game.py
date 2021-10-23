from shared import *
from image_processing import ImageProcessor, Image
from movement import Movement
import file_manager
import input
import time
import atexit


class Game:
    _current_frame: Image
    _current_frame_cropped: Image

    _movement: Movement
    _next_checkpoint: int
    needs_extra_checks: bool

    # current_combat: Combat
    # in_combat: bool

    def __init__(self):
        print("Game init")

        atexit.register(input.key_up_all)
        input.focus()

    def start(self):
        print("Game start")

        if file_manager.save_exists():
            self._load_existing()
        else:
            self._start_new()

        self._start_loop()

    def _start_new(self):
        self._next_checkpoint = 1
        self.needs_extra_checks = False

        input.move('w')
        input.move('w')
        input.move('w')
        input.accept()

        self._accept_until('images/game_start.png')

        self._movement = Movement(self._next_checkpoint)

    def _load_existing(self):
        data = self._load_game()
        self._next_checkpoint = data[0]
        self.needs_extra_checks = True
        self._movement = Movement(self._next_checkpoint, data[1])

    def _start_loop(self):
        while True:
            self._loop()
            self._after_loop()

    def _loop(self):
        self.current_frame = ImageProcessor.grab_full_screen()
        self.current_frame_cropped = ImageProcessor.grab_close_screen()

        # Chatting
        if self._is_chatting():
            input.accept()
            return

        '''
        # Input
        if self._is_waiting_input():
            input.type_player_name()
            return

        # Combat
        \'''
        if self._is_in_combat():
            if not self.in_combat:
                # Get Pokemon name
                image = ImageGrab.grab(bbox=(155, 170, 680, 220))
                image = image.convert('L')
                image = image.filter(ImageFilter.BLUR)
                image = image.filter(ImageFilter.SMOOTH)
                image = image.filter(ImageFilter.SMOOTH_MORE)

                data = None
                combat_resize_y = 75
                while data is None:
                    mod_image = image.resize(size=(845, combat_resize_y))
                    name = pytesseract.image_to_string(mod_image,
                                                       config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    name = name.strip().lower()
                    data = pkmapi.lookup_pokemon(name)
                    combat_resize_y += 1

                image = ImageGrab.grab(bbox=(745, 165, 790, 225))
                image = image.point(lambda p: p > 100 and 255)
                image = image.filter(ImageFilter.BLUR)
                image = image.filter(ImageFilter.SMOOTH)
                image = image.filter(ImageFilter.SMOOTH_MORE)
                image = image.resize(size=(256, 260))
                level = pytesseract.image_to_string(image, config='--psm 13').strip()

                self.in_combat = True
                self.current_combat = Combat(data, level)

            image = self.current_frame.crop(box=(417, 207, 798, 208))
            for k, v in image.getcolors():
                if v == COLOR_COMBAT_ENEMY_HEALTH:
                    self.current_combat.set_health(100 - ((k / 381) * 100))
                    break

            return
        \'''
        '''

        # Playing
        # Move
        self._movement.next_move()

    def _after_loop(self):
        if self._movement.skip_checks:
            return

        self._check_frames()

        # Check if things are moving (not us)
        image1 = ImageProcessor.grab_close_screen()
        time.sleep(0.1)
        image2 = ImageProcessor.grab_close_screen()

        if ImageProcessor.are_same_image(image1, image2):
            self.needs_extra_checks = False
        else:
            self.needs_extra_checks = True

    def _check_frames(self):
        if self.needs_extra_checks:
            checks = 128
        else:
            checks = 20

        map_changed = False
        for i in range(0, checks):
            image = ImageProcessor.grab_close_screen()

            # Check if changing maps
            if not map_changed and ImageProcessor.is_black_image(image):
                input.accelerate()
                time.sleep(0.3)
                input.deaccelerate()
                map_changed = True
                continue

            # Check if at checkpoint
            if self._is_at_checkpoint(image):
                if map_changed:
                    self._movement.map_changed()

                self._on_checkpoint_reached(self._next_checkpoint)
                break

            # We do the map change here because we break after it, we want to check checkpoint first
            if map_changed:
                self._movement.map_changed()
                break

            # Check if stuck
            if ImageProcessor.are_same_image(self.current_frame_cropped, image):
                self._movement.stuck()
                break

    def _accept_until(self, image_path):
        dest_image = Image.open(image_path)
        self.accept_until_image = dest_image

        input.accelerate()

        current_frame = ImageProcessor.grab_close_screen()
        while not ImageProcessor.are_same_image(current_frame, dest_image):
            input.accept()
            current_frame = ImageProcessor.grab_close_screen()

        input.deaccelerate()

    def _is_chatting(self):
        image = self.current_frame.crop(box=(650, 720, 651, 721))
        return self._image_is_color(image, COLOR_CHATTING)

    def _is_waiting_input(self):
        return self.current_frame.getpixel((10, 10)) == COLOR_INPUT

    def _is_in_combat(self):
        return self.current_frame.getpixel((730, 130)) == COLOR_COMBAT

    def _image_is_color(self, image, color):
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                if image.getpixel((x, y)) != color:
                    return False

        return True

    def _is_at_checkpoint(self, frame):
        checkpoint_image = Image.open('images/checkpoint_' + str(self._next_checkpoint) + '.png', 'r')
        return ImageProcessor.are_same_image(frame, checkpoint_image)

    def _on_checkpoint_reached(self, checkpoint):
        self._movement.checkpoint_reached(checkpoint)

        input.accelerate()

        if checkpoint == 2:  # Clock
            input.move(KEY_UP)
            input.accept()
            time.sleep(0.1)
            input.accept()
            time.sleep(0.1)
            input.accept()
            time.sleep(0.1)
            input.accept()
            input.move(KEY_UP)
            input.accept()

        try:
            self._accept_until('images/checkpoint_' + str(checkpoint) + '_end.png')
        except FileNotFoundError:
            pass

        input.deaccelerate()

        self._next_checkpoint += 1
        self._save_game()

    def _save_game(self):
        print('Saving game')
        file_manager.save_game(self._next_checkpoint, self._movement.get_current_map())

        input.save_game()
        input.start()
        input.cancel()

    def _load_game(self):
        print('Loading game')

        input.load_game()
        input.start()
        input.cancel()

        return file_manager.load_game()

    def _reset_menu(self, option):
        input.start()

        for i in range(0, option):
            input.move(KEY_UP)

        input.cancel()
