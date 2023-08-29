from game.enums import ResourceEnum, BuildingEnum
from game.building import Building
from players.player import Player
from game.catanboard import CatanBoard

class AIPlayer(Player):

    def __init__(self, name:str, id:int):
        super().__init__(name, id)

    def update_exchange_rates(self):
        # TODO: need to see if we have a port
        return True

    def place_buildings(self, gb:CatanBoard, types:[BuildingEnum]):
        return True

    def place_settlement(self):
        return True

    def place_road(self):
        return True

    def place_city(self):
        return True

    def trade(self):
        return True

    def move_robber(self):
        return True

    def play_development_card(self):
        return True

    def __str__(self):
        self.resource_hand.sort()
        s = 'The hand is:\n'
        for resource in self.resource_hand:
            s += f'\t{str(resource)}\n' 
        return s + '\n'
