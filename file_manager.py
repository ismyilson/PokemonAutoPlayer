import os
import pickle


PATH_GAME_DATA = 'data/game.sav'


def save_game_data(data) -> None:
    with open(PATH_GAME_DATA, 'wb+') as file:
        for d in data:
            pickle.dump(d, file)


def load_game_data() -> list:
    data = list()
    try:
        with open(PATH_GAME_DATA, 'rb') as file:
            while True:
                data.append(pickle.load(file))
    except (FileNotFoundError, EOFError):
        return data


def game_save_exists() -> bool:
    return os.path.isfile(PATH_GAME_DATA)


'''
def save_map(identifier, room_map):
    with open('maps/' + identifier + '.map', 'wb+') as file:
        pickle.dump(room_map, file)


def load_map(identifier) -> list:
    try:
        with open('maps/' + identifier + '.map', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def map_exists(identifier) -> bool:
    return os.path.isfile('maps/' + identifier + '.map')


def save_routes_taken(checkpoint, routes):
    with open('routes/checkpoint_' + str(checkpoint) + '.cpr', 'wb+') as file:
        pickle.dump(routes, file)


def load_routes_to_checkpoint(checkpoint) -> dict:
    try:
        with open('routes/checkpoint_' + str(checkpoint) + '.cpr', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return dict()
'''
