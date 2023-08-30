from game.enums import ResourceEnum, BuildingEnum
from game.building import Building
from players.player import Player
from game.catanboard import CatanBoard
from game.enums import NodeEnum
from game.node import Point

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

    def place_city(self, gb:CatanBoard):
        city_upgraded = False
        while not city_upgraded:
            city_point = Point(12,10) # TODO

            if not city_point: # quit out
                return False
            
            city_vertex = gb.tilemap.get_node_from_point(city_point)
            
            if self.check_city_vertex(city_vertex):
                city_upgraded = city_vertex.set_building(BuildingEnum.CITY, self.player_id)

        return city_vertex

    def place_settlement(self, gb:CatanBoard, setup:bool = False):
        settlement_placed = False
        while not settlement_placed:
            tile_production_points = self.get_tile_production_points(gb)
            points = list(tile_production_points.keys())
            points.sort(reverse=True)
            for point in points:
                settlement_vertex = tile_production_points[point]
                if self.check_settlement_vertex(settlement_vertex, setup):
                    settlement_placed = settlement_vertex.set_building(BuildingEnum.SETTLEMENT, self.player_id)
                    break

        return settlement_vertex
    
    def place_road(self, gb:CatanBoard):
        # TODO: Apply road to only the most recent settlement on setup
        road_edge = None
        road_placed = False
        while not road_placed:
            for node in gb.tilemap.nodes:
                if not node.is_empty() and node.building.player_id == self.player_id and node.building.type == BuildingEnum.SETTLEMENT:
                    for neighbor in node.neighbors:
                        road_edge = neighbor
                        if self.check_road_edge(road_edge):
                            road_placed = road_edge.set_building(BuildingEnum.ROAD, self.player_id)
                            break

        return road_edge

    # def trade(self):
    #     return True

    # def move_robber(self):
    #     return True

    # def play_development_card(self):
    #     return True
    
    # def play(self, gb:CatanBoard):
    #     print(self)
    #     return True

    # def __str__(self):
    #     self.resource_hand.sort()
    #     s = 'The hand is:\n'
    #     for resource in self.resource_hand:
    #         s += f'\t{str(resource)}\n' 
    #     return s + '\n'
