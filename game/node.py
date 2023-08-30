from game.enums import BuildingEnum
from game.building import Building
from game.enums import NodeEnum
import math

class Point:

    def __init__(self, x_init, y_init):
        self.x = x_init
        self.y = y_init

    def shift(self, x, y):
        self.x += x
        self.y += y

    @staticmethod
    def dist(p1_x, p1_y, p2_x, p2_y):
        return round(math.dist([p1_x, p1_y], [p2_x, p2_y]), 2)

    def __copy__(self):
        return Point(self.x, self.y)
    
    def __eq__(self, obj):
        return isinstance(obj, Point) and obj.x == self.x and obj.y == self.y
    
    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        from game.display_grid import DisplayGrid
        return f'Point({DisplayGrid.convert_to_x_scale(self.x)}, {str(self.y)})'

class Node(Point):

    def __init__(self, x, y, type:NodeEnum, neighbors:[] = [], tile_ids:[int] = [], icon:str = '0'):
        self.type = type
        self.neighbors = neighbors
        self.icon = icon
        self.tiles_touching = tile_ids.copy()
        self.building = Building(BuildingEnum.EMPTY, -1)
        self.port = None # TODO
        super().__init__(x, y)

    def set_building(self, building_type:BuildingEnum, player_id:int):
        if not self.is_empty() and not (building_type == BuildingEnum.CITY and self.building.type == BuildingEnum.SETTLEMENT):
            print('This spot is taken, sorry.')
            return False
        
        if building_type not in self.type.value:
            print('That\'s not a valid placement.')
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
