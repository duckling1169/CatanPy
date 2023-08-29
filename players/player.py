from game.enums import ResourceEnum, BuildingEnum
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

    def place_buildings(self, gb:CatanBoard, types:[BuildingEnum], setup_phase:bool):
        for type in types:
            building = Building(type, self.player_id)
            if not building.cost in self.resource_hand and not setup_phase: # cannot afford the building
                print('You cannot afford that!')
                continue
            
            settle_point = None
            good_resp = False
            while not good_resp:
                resp = input(f'Where do you want your settlement, {self.name}? (#,c)')
                if ',' in resp:
                    try:
                        x = int(resp.split(',')[0])
                        y = DisplayGrid.x_scale_convert(resp.split(',')[1])
                        settle_point = Point(x, y)
                    except:
                        pass 

                settle_corner = gb.tilemap.get_corner_from_point(settle_point)
                if settle_corner.is_occupied():
                    print('This spot is already taken!')
                    continue

                for neighbor in settle_corner.neighbors:
                    if neighbor.is_occupied() and neighbor.building_type == BuildingEnum.SETTLEMENT or neighbor.building_type == BuildingEnum.CITY:
                        print('This spot is too close to another building!')
                        continue
                
                if not setup_phase:
                    for neighbor in settle_corner.neighbors:
                        if not(neighbor.is_occupied() and neighbor.player_id == self.player_id and neighbor.building_type == BuildingEnum.ROAD):
                            print('Need to be at least 2 roads away from another settlement.')
                            continue
                        else:
                            for neighbor2 in neighbor.neighbors:
                                if not(neighbor2.is_occupied() and neighbor.player_id == self.player_id and neighbor2.building_type == BuildingEnum.ROAD):
                                    print('Need to be at least 2 roads away from another settlement.')
                                    continue

                print('Success!')
                good_resp = True

            if setup_phase == 0: # during setup offer to place a settlement THEN a road
                True
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
