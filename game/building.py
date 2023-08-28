from game.purchaseables import Purchaseables
from game.enums import ResourceEnum, BuildingEnum
from game.node import *

class Building(Purchaseables):

    def __init__(self, type:BuildingEnum, player_id:int):
        self.type = type
        self.player_id = player_id
        self.icon = type.value

        match type:
            case BuildingEnum.ROAD:
                self.victory_points = 0
                super().__init__('Building', [ ResourceEnum.BRICK, ResourceEnum.WOOD ])
            case BuildingEnum.SETTLEMENT:
                self.victory_points = 1
                super().__init__('Building', [ ResourceEnum.WHEAT, ResourceEnum.SHEEP, ResourceEnum.BRICK, ResourceEnum.WOOD ])
            case BuildingEnum.CITY:
                self.victory_points = 2
                super().__init__('Building', [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE ])

    def __str__(self):
        return str(self.player_id) if self.type == BuildingEnum.ROAD else self.icon + str(self.player_id)

                
                
