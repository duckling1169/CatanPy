from game.enums import BuildingEnum
from game.building import Building

class Point:

    def __init__(self, x_init, y_init):
        self.x = x_init
        self.y = y_init

    def shift(self, x, y):
        self.x += x
        self.y += y

    def __copy__(self):
        return Point(self.x, self.y)

    def __str__(self):
        return f'Point({str(self.x)}, {str(self.y)})'

class Node(Point):

    def __init__(self, x, y, tile_ids:[int] = [], icon:str = '0'):
        self.icon = icon
        self.building = BuildingEnum.EMPTY
        self.is_port = False
        self.tiles_touching = tile_ids.copy()
        # port = Port()  TO_DO
        super().__init__(x, y)

    def set_building(self, player_id:int, building_type:BuildingEnum):
        self.building = Building(building_type, player_id)
    
    def get_resources_touching(self):
        resources = []
        for tile in self.tiles_touching:
            resources.append(tile.resource)
        return resources
    
    def is_occupied(self):
        return self.building != BuildingEnum.EMPTY
    
    def get_player_id(self):
        return self.building.player_id if self.building is not BuildingEnum.EMPTY else -1