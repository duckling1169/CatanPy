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

    def place_buildings(self, gb:CatanBoard, types:[BuildingEnum], receive_resources:bool=False):
        match types:
            case [ BuildingEnum.ROAD, BuildingEnum.ROAD ]: # roadbuilder
                self.place_road(gb, True)
                gb.update_grid()
                print(gb)
                self.place_road(gb)
                return True
            case [ BuildingEnum.SETTLEMENT, BuildingEnum.ROAD ]: # setup
                settlement_vertex = self.place_settlement(gb, True)
                if receive_resources:
                    for id in settlement_vertex.tiles_touching:
                        self.resource_hand.append(gb.tilemap.get_tile_from_id(id).resource)
                gb.update_grid()
                print(gb)
                self.place_road(gb)
                return True
            case _: # all other cases
                if len(types) > 1:
                    return False

        building = types[0]
        if not building.cost in self.resource_hand: # cannot afford the building
            return False

        match building:
            case BuildingEnum.ROAD:
                return self.place_road(gb)
            case BuildingEnum.SETTLEMENT:
                return self.place_settlement(gb)
            case BuildingEnum.CITY:
                return self.place_city(gb)
        return False

    def place_city(self, gb:CatanBoard):
        city_upgraded = False
        while not city_upgraded:
            city_point = Point(12,10) # TODO

            if not city_point: # quit out
                return False
            
            city_vertex = gb.tilemap.get_node_from_point(city_point)
            
            # check if spot is existing settlement under this player's id
            if city_vertex == None:
                continue

            if city_vertex.building.type != BuildingEnum.SETTLEMENT:
                continue

            if city_vertex.player_id != self.player_id:
                continue

            city_upgraded = city_vertex.set_building(BuildingEnum.CITY, self.player_id)
        return city_vertex

    def place_settlement(self, gb:CatanBoard, setup:bool = False):
        settlement_placed = False
        while not settlement_placed:
            tile_production_points = self.get_tile_production_points(gb)
            points = list(tile_production_points.keys())
            points.sort(reverse=True)
            settlement_vertex = tile_production_points[points[0]] # highest point value

            if settlement_vertex == None:
                continue
            
            neighbor_found = False
            for neighbor in settlement_vertex.neighbors:
                if neighbor.type == NodeEnum.VERTEX:
                    if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT or neighbor.building.type == BuildingEnum.CITY:
                        neighbor_found = True
                        break
                elif neighbor.type == NodeEnum.EDGE:
                    for other in neighbor.neighbors:
                        if other.type == NodeEnum.VERTEX:
                            if not other.is_empty() and other.building.type == BuildingEnum.SETTLEMENT or other.building.type == BuildingEnum.CITY:
                                neighbor_found = True
                                break
            if neighbor_found:
                continue
            
            if not setup: # additional rules if not during setup phase
                for neighbor in settlement_vertex.neighbors:
                    if not(not neighbor.is_empty() and neighbor.player_id == self.player_id and neighbor.building.type == BuildingEnum.ROAD):
                        continue
                    else:
                        for neighbor2 in neighbor.neighbors:
                            if not(neighbor2.is_occupied() and neighbor.player_id == self.player_id and neighbor2.building.type == BuildingEnum.ROAD):
                                continue

            settlement_placed = settlement_vertex.set_building(BuildingEnum.SETTLEMENT, self.player_id)
        return settlement_vertex
    
    def place_road(self, gb:CatanBoard):
        road_placed = False
        while not road_placed:
            road_point = Point(12,10) # TODO

            if not road_point:
                return False
            
            road_edge = gb.tilemap.get_node_from_point(road_point)

            if road_edge == None:
                continue

            for neighbor in road_edge.neighbors: # can't build a road passed another player's settlement
                if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id != self.player_id:
                    continue
            
            neighbor_found = False
            for neighbor in road_edge.neighbors: # need to build next to your own settlements or roads
                if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id == self.player_id or\
                    not neighbor.is_empty() and neighbor.building.type == BuildingEnum.ROAD and neighbor.building.player_id == self.player_id:
                    neighbor_found = True
                    break

            if not neighbor_found:
                continue
            
            road_placed = road_edge.set_building(BuildingEnum.ROAD, self.player_id)
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
