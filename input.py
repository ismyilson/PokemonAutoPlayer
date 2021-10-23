from shared import *
import pyautogui
import time

# For key_up_all
used_keys = [
    KEY_ACCEPT,
    KEY_CANCEL,
    KEY_START,
    KEY_ACCELERATE,
    KEY_UP,
    KEY_RIGHT,
    KEY_DOWN,
    KEY_LEFT,
    KEY_CTRL_LEFT,
    KEY_S,
    KEY_L
]


def focus():
    pyautogui.moveTo(600, 600)
    pyautogui.click()


def accept():
    _press_key(KEY_ACCEPT)


def hold_accept():
    pyautogui.keyDown(KEY_ACCEPT)


def stop_hold_accept():
    pyautogui.keyUp(KEY_ACCEPT)


def cancel():
    _press_key(KEY_CANCEL)


def start():
    _press_key(KEY_START)


def accelerate():
    pyautogui.keyDown(KEY_ACCELERATE)


def deaccelerate():
    pyautogui.keyUp(KEY_ACCELERATE)


def move(direction):
    _press_key(direction)


'''
def type_player_name():
    for item in PLAYER_NAME_SEQUENCE:
        pyautogui.keyDown(item)
        pyautogui.keyUp(item)

    start()
    accept()
'''


def key_up_all():
    for key in used_keys:
        pyautogui.keyUp(key)


def save_game():
    with pyautogui.hold(KEY_CTRL_LEFT):
        _press_key(KEY_S)


def load_game():
    with pyautogui.hold(KEY_CTRL_LEFT):
        _press_key(KEY_L)


def _press_key(key):
    pyautogui.keyDown(key)
    time.sleep(0.05)
    pyautogui.keyUp(key)
