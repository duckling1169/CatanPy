from game.enums import BuildingEnum
from game.building import Building
from game.enums import NodeEnum
from game.point import Point
from game.port import Port

class Node(Point):

    def __init__(self, x:int, y:int, type:NodeEnum):
        self.type = type
        self.icon = '·'
        self.neighbors = []
        self.tiles_touching = []
        self.building = Building(BuildingEnum.EMPTY, -1)
        self.port = None
        super().__init__(x, y)

    def set_building(self, building_type:BuildingEnum, player_id:int):
        if not self.is_empty() and not (building_type == BuildingEnum.CITY and self.building.type == BuildingEnum.SETTLEMENT):
            return False
        
        if building_type not in self.type.value:
            return False

        self.building = Building(building_type, player_id)
        self.icon = self.building.icon
        return True
    
    def is_empty(self):
        return self.building.type == BuildingEnum.EMPTY
    
    def get_player_id(self):
        return self.building.player_id if self.building is not BuildingEnum.EMPTY else -1
    
    def __str__(self):
        return super().__str__() + f' | {self.type}'
