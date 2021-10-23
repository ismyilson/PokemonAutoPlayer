import requests

api_url = 'https://pokeapi.co/api/v2/pokemon/'


def lookup_pokemon(name):
    with open('data/pokemon_list') as file:
        if name not in file.read():
            return None

    r = requests.get(api_url + name)
    if r.status_code != 200:
        return None

    return r.text
