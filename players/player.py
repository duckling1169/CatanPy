from game.enums import ResourceEnum, BuildingEnum, NodeEnum
from game.building import Building
from game.display_grid import DisplayGrid
from game.node import Point
from game.catanboard import CatanBoard

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

    def place_buildings(self, gb:CatanBoard, types:[BuildingEnum]):
        match types:
            case [ BuildingEnum.ROAD, BuildingEnum.ROAD ]: # roadbuilder
                self.place_road(gb, True)
                gb.update_grid()
                print(gb)
                self.place_road(gb)
                return True
            case [ BuildingEnum.SETTLEMENT, BuildingEnum.ROAD ]: # setup
                self.place_settlement(gb, True)
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
            
            # check if spot is existing settlement under this player's id
            if city_vertex == None:
                print('Couldn\'t find that spot!')
                continue

            if city_vertex.building.type != BuildingEnum.SETTLEMENT:
                print('Choose a settlement to upgrade.')
                continue

            if city_vertex.player_id != self.player_id:
                print('This isn\'t your settlement.')
                continue

            city_upgraded = city_vertex.set_building(BuildingEnum.CITY, self.player_id)

        return True

    def place_settlement(self, gb:CatanBoard, setup:bool = False):
        settlement_placed = False
        while not settlement_placed:
            settlement_point = self.get_location_from_user(BuildingEnum.SETTLEMENT)

            if not settlement_point: # quit out
                return False
            
            settlement_vertex = gb.tilemap.get_node_from_point(settlement_point)

            if settlement_vertex == None:
                print('Couldn\'t find that spot!')
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
                print('This spot is too close to another building!')
                continue
            
            if not setup: # additional rules if not during setup phase
                for neighbor in settlement_vertex.neighbors:
                    if not(not neighbor.is_empty() and neighbor.player_id == self.player_id and neighbor.building.type == BuildingEnum.ROAD):
                        print('Need to be at least 2 roads away from another settlement.')
                        continue
                    else:
                        for neighbor2 in neighbor.neighbors:
                            if not(neighbor2.is_occupied() and neighbor.player_id == self.player_id and neighbor2.building.type == BuildingEnum.ROAD):
                                print('Need to be at least 2 roads away from another settlement.')
                                continue

            settlement_placed = settlement_vertex.set_building(BuildingEnum.SETTLEMENT, self.player_id)

        return True
    
    def place_road(self, gb:CatanBoard):
        road_placed = False
        while not road_placed:
            road_point = self.get_location_from_user(BuildingEnum.ROAD)

            if not road_point:
                return False
            
            road_edge = gb.tilemap.get_node_from_point(road_point)

            if road_edge == None:
                print('Couldn\'t find that spot!')
                continue

            for neighbor in road_edge.neighbors: # can't build a road passed another player's settlement
                if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id != self.player_id:
                    print('This spot is too close to another player\'s settlement!')
                    continue
            
            neighbor_found = False
            for neighbor in road_edge.neighbors: # need to build next to your own settlements or roads
                if not neighbor.is_empty() and neighbor.building.type == BuildingEnum.SETTLEMENT and neighbor.building.player_id == self.player_id or\
                    not neighbor.is_empty() and neighbor.building.type == BuildingEnum.ROAD and neighbor.building.player_id == self.player_id:
                    neighbor_found = True
                    break

            if not neighbor_found:
                print('You need to be closer to your own roads/settlements!')
                continue
            
            road_placed = road_edge.set_building(BuildingEnum.ROAD, self.player_id)
        return True

    def get_location_from_user(self, type):
        resp = input(f'Where do you want your {type.name.lower()}, {self.name}? (#,c) (q to quit)\n')
        if resp == 'q':
            return None
        
        if ',' in resp:
            try:
                x = int(resp.split(',')[0])
                y = DisplayGrid.x_scale_convert(resp.split(',')[1])
                return Point(x, y)
            except:
                return Point(-1, -1)

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
