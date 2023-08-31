from game.enums import ResourceEnum, BuildingEnum
from game.purchaseables import Building
from players.player import Player
from game.enums import NodeEnum
from game.node import Node
from game.point import Point
from settlegame import SettleGame

class AIPlayer(Player):

    def __init__(self, name:str, id:int):
        super().__init__(name, id)

    def get_tile_production_points(self, gb:SettleGame) -> dict:
        tile_production_points = {}
        for node in gb.tilemap.nodes:
            if node.type == NodeEnum.VERTEX:
                s = 0
                for touching in node.tiles_touching:
                    s += gb.tilemap.get_tile_from_id(touching).resource_points
                tile_production_points[s] = node
        return tile_production_points 
    
    def get_resource_points(self, gb:SettleGame) -> dict:
        resource_points = {}
        for tile in gb.tilemap.tiles:
            if tile.resource not in resource_points.keys():
                resource_points[tile.resource] = [tile]
            else:
                resource_points[tile.resource].append(tile)
        return resource_points 

    def place_city(self, gb:SettleGame) -> Node:
        city_upgraded = False
        while not city_upgraded:
            city_point = Point(12,10) # TODO

            if not city_point: # quit out
                return False
            
            city_vertex = gb.tilemap.get_node_from_point(city_point)
            
            if self.check_city_vertex(city_vertex):
                city_upgraded = city_vertex.set_building(BuildingEnum.TOWN, self.id)

        return city_vertex

    def place_settlement(self, gb:SettleGame, setup:bool = False) -> Node:
        settlement_placed = False
        while not settlement_placed:
            tile_production_points = self.get_tile_production_points(gb)
            points = list(tile_production_points.keys())
            points.sort(reverse=True)
            for point in points:
                settlement_vertex = tile_production_points[point]
                if self.check_settlement_vertex(settlement_vertex, setup):
                    settlement_placed = settlement_vertex.set_building(BuildingEnum.OUTPOST, self.id)
                    break

        return settlement_vertex
    
    def place_road(self, gb:SettleGame) -> Node:
        # TODO: Apply road to only the most recent settlement on setup
        road_edge = None
        road_placed = False
        while not road_placed:
            for node in gb.tilemap.nodes:
                if not node.is_empty() and node.building.player_id == self.id and node.building.type == BuildingEnum.OUTPOST:
                    for neighbor in node.neighbors:
                        road_edge = neighbor
                        if self.check_road_edge(road_edge):
                            road_placed = road_edge.set_building(BuildingEnum.ROAD, self.id)
                            break

        return road_edge

    def trade(self):
        return True

    def move_robber(self):
        return True

    def play_development_card(self):
        return True
    
    def play(self, gb:SettleGame):
        print(self)
        return True

    def __str__(self):
        self.resource_hand.sort()
        s = f'{self.name}\'s hand is:\n'
        for resource in self.resource_hand:
            s += f'\t{str(resource)}\n' 
        return s + '\n'
