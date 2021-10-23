import json


class Combat:
    name = None
    level = None
    type1 = None
    type2 = None
    health = None

    def __init__(self, json_data, level):
        self._load_data(json_data)
        self.level = level
        self._print_data()

    def set_health(self, health):
        self.health = health
        if self.health <= 0:
            print("Enemy died")

    def _load_data(self, json_data):
        data = json.loads(json_data)
        self.name = data['name']
        self.type1 = data['types'][0]['type']['name']
        self.type2 = data['types'][1]['type']['name'] if len(data['types']) > 1 else None
        self.health = 100

    def _print_data(self):
        print("Combat started vs", self.name)
        print("Level:", self.level)
        print("Types:", self.type1, self.type2)
