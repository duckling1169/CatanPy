from game.enums import BuildingEnum
from game.building import Building
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
        return f'Point({str(self.x)}, {DisplayGrid.convert_to_x_scale(self.y)})'

class Node(Point):

    def __init__(self, x, y, neighbors:[] = [], tile_ids:[int] = [], icon:str = '0'):
        self.neighbors = neighbors
        self.icon = icon
        self.tiles_touching = tile_ids.copy()
        self.building_type = BuildingEnum.EMPTY
        self.port = None # TODO
        super().__init__(x, y)

    def set_building(self, building_type:BuildingEnum, player_id:int):
        if self.building_type != BuildingEnum.EMPTY:
            return False
        
        self.building_type = Building(building_type, player_id)
        self.icon = self.building_type.icon
        return True
    
    def is_occupied(self):
        return self.building_type != BuildingEnum.EMPTY
    
    def get_player_id(self):
        return self.building_type.player_id if self.building_type is not BuildingEnum.EMPTY else -1
    
    def __str__(self):
        return super().__str__() + f' | {self.is_occupied()}'