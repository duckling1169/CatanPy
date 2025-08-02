from game.enums import BuildingEnum
from game.purchaseables import Building
from game.enums import NodeEnum
from game.point import Point
from game.port import Port

class Node(Point):

    def __init__(self, x:int, y:int, type:NodeEnum):
        self.type = type
        self.icon = '·'
        self.neighbors = []
        self.tiles_touching = []
        self.building = Building(BuildingEnum.EMPTY)
        self.port = None
        super().__init__(x, y)

    def set_building(self, building_type:BuildingEnum, player_id:int) -> bool:
        if self.has_building() and not (building_type == BuildingEnum.TOWN and self.building.type == BuildingEnum.SETTLEMENT):
            return False
        
        if building_type not in self.type.value:
            return False

        self.building = Building(building_type, player_id)
        self.icon = self.building.icon
        return True
    
    def has_building(self) -> bool:
        return self.building.type != BuildingEnum.EMPTY
    
    def get_player_id(self) -> int:
        return self.building.player_id if self.has_building() else -1
    
    def __str__(self):
        return super().__str__() + f' | {self.type}'
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y and self.type == other.type
    
    def __hash__(self):
        return hash((self.x, self.y, self.type))
