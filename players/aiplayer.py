from game.enums import ResourceEnum, BuildingEnum
from game.building import Building
from players.player import Player
from game.catanboard import CatanBoard
from game.enums import NodeEnum

class AIPlayer(Player):

    def __init__(self, name:str, id:int):
        super().__init__(name, id)

    def get_tile_production_points(self, gb:CatanBoard):
        tile_production_points = {}
        for node in gb.tilemap.nodes:
            if node.type == NodeEnum.VERTEX:
                s = 0
                for touching in node.tiles_touching:
                    s += gb.tilemap.get_tile_from_id(touching).resource_points
                tile_production_points[s] = node
        return tile_production_points 
    
    def get_resource_points(self, gb:CatanBoard):
        resource_points = {}
        for tile in gb.tilemap.tiles:
            if tile.resource not in resource_points.keys():
                resource_points[tile.resource] = [tile]
            else:
                resource_points[tile.resource].append(tile)
        return resource_points 

    def update_exchange_rates(self):
        # TODO: need to see if we have a port
        return True

    def place_buildings(self, gb:CatanBoard, types:[BuildingEnum]):
        # tile_production_points = self.get_tile_production_points(gb)
        # points = list(tile_production_points.keys())
        # points.sort(reverse=True)
        # for amount in points[:4]:
        #     node = tile_production_points[amount]
        #     print(node, amount)
        # print()

        # resource_points = self.get_resource_points(gb)
        # for resource, l in resource_points.items():
        #     for i in l:
        #         print(i)
        #     print()

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
