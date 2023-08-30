from game.enums import ResourceEnum, BuildingEnum, NodeEnum
from game.display_grid import DisplayGrid
from game.node import *
from game.catanboard import CatanBoard
from collections import Counter

class Player():

    def __init__(self, name:str, id:int):
        self.name = name
        self.player_id = id
        self.victory_points = 0
        self.resource_hand = []
        self.buildings = []
        self.active_development_cards = []
        self.played_development_cards = []
        self.exchange_rates = {
            ResourceEnum.SHEEP: 4,
            ResourceEnum.WOOD: 4,
            ResourceEnum.WHEAT: 4,
            ResourceEnum.ORE: 4,
            ResourceEnum.BRICK: 4
        }

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
                    print('Only one building at a time!')
                    return False

        building = types[0]
        if not building.cost in self.resource_hand: # cannot afford the building
            print('You cannot afford that!')
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
            city_point = self.get_location_from_user(BuildingEnum.SETTLEMENT)

            if not city_point: # quit out
                return False
            
            city_vertex = gb.tilemap.get_node_from_point(city_point)
            
            if self.check_city_vertex(city_vertex):
                city_upgraded = city_vertex.set_building(BuildingEnum.CITY, self.player_id)

        return city_vertex
    
    def place_settlement(self, gb:CatanBoard, setup:bool = False):
        settlement_placed = False
        while not settlement_placed:
            settlement_point = self.get_location_from_user(BuildingEnum.SETTLEMENT)

            if not settlement_point: # quit out
                return False
            
            settlement_vertex = gb.tilemap.get_node_from_point(settlement_point)

            if self.check_settlement_vertex(settlement_vertex, setup):
                settlement_placed = settlement_vertex.set_building(BuildingEnum.SETTLEMENT, self.player_id)

        return settlement_vertex
    
    def place_road(self, gb:CatanBoard):
        road_placed = False
        while not road_placed:
            road_point = self.get_location_from_user(BuildingEnum.ROAD)

            if not road_point:
                return False
            
            road_edge = gb.tilemap.get_node_from_point(road_point)

            if self.check_road_edge(road_edge):
                road_placed = road_edge.set_building(BuildingEnum.ROAD, self.player_id)

        return road_edge
    

    def check_city_vertex(self, city_vertex:Node, feedback:bool = False):
        # check if spot is existing settlement under this player's id
        if city_vertex == None:
            if feedback:
                print('Couldn\'t find that spot!')
            return False

        if city_vertex.building.type != BuildingEnum.SETTLEMENT:
            if feedback:
                print('Choose a settlement to upgrade.')
            return False

        if city_vertex.player_id != self.player_id:
            if feedback:
                print('That isn\'t your settlement.')
            return False

        return True

    def check_settlement_vertex(self, settlement_vertex:Node, setup:bool, feedback:bool = False):
        if settlement_vertex == None:
            if feedback:
                print('Couldn\'t find that spot!')
            return False
        
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
            if feedback:
                print('That spot is too close to another building!')
            return False
        
        if not setup: # additional rules if not during setup phase
            for neighbor in settlement_vertex.neighbors:
                if not(not neighbor.is_empty() and neighbor.player_id == self.player_id and neighbor.building.type == BuildingEnum.ROAD):
                    if feedback:
                        print('Need to be at least 2 roads away from another settlement.')
                    return False
                else:
                    for neighbor2 in neighbor.neighbors:
                        if not(neighbor2.is_occupied() and neighbor.player_id == self.player_id and neighbor2.building.type == BuildingEnum.ROAD):
                            if feedback:
                                print('Need to be at least 2 roads away from another settlement.')
                            return False                            
        return True

    def check_road_edge(self, road_edge:Node, feedback:bool = False):
        if road_edge == None:
            if feedback:
                print('Couldn\'t find that spot!')
            return False

        for neighbor in road_edge.neighbors: # can't build a road passed another player's settlement
            if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id != self.player_id:
                if feedback:
                    print('That spot is too close to another player\'s settlement!')
                return False
        
        neighbor_found = False
        for neighbor in road_edge.neighbors: # need to build next to your own settlements or roads
            if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id == self.player_id or\
                not neighbor.is_empty() and neighbor.building.type == BuildingEnum.ROAD and neighbor.building.player_id == self.player_id:
                neighbor_found = True
                break

        if not neighbor_found:
            if feedback:
                print('You need to be closer to your own roads/settlements!')
            return False
        
        return True


    def get_location_from_user(self, type):
        resp = input(f'Where do you want your {type.name.lower()}, {self.name}? (c,#) (q to quit)\n')
        if resp == 'q':
            return None
        
        if ',' in resp:
            try:
                x = DisplayGrid.x_scale_convert(resp.split(',')[0])
                y = int(resp.split(',')[1])
                return Point(x, y)
            except:
                return Point(-1, -1)


    def trade(self):
        return True

    def move_robber(self):
        return True

    def play_development_card(self):
        return True
    
    def play(self, gb:CatanBoard):
        # Before-roll options: Play Development card or roll 

        # Roll + give out resources OR if 7; move Robber + steal from a player on that tile

        # After-roll options: Buy a purchaseable item or trade with bank or players

        print(self)
        return True

    def __str__(self):
        s = f'{self.name}\'s hand is:\n'
        for type, count in dict(Counter(self.resource_hand).items()).items():
            s += f'\t({str(count)}) {type.value}\n' 
        return s + '\n'
