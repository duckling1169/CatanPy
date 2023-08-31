from settlegame import SettleGame
from game.enums import GrowthCardEnum
from game.enums import ResourceEnum, BuildingEnum, NodeEnum
from game.display_grid import DisplayGrid
from game.node import *
from collections import Counter

import random
class Player():

    def __init__(self, name:str, id:int):
        self.name = name
        self.id = id
        self.resource_hand = []
        self.buildings = []
        self.unplayed_dev_cards = []
        self.played_dev_cards = []
        self.exchange_rates = {
            ResourceEnum.SHEEP: 4,
            ResourceEnum.WOOD: 4,
            ResourceEnum.WHEAT: 4,
            ResourceEnum.ORE: 4,
            ResourceEnum.BRICK: 4
        }


    def place_buildings(self, gb:SettleGame, types:[BuildingEnum], receive_resources:bool=False) -> bool:
        match types:
            case [ BuildingEnum.ROAD, BuildingEnum.ROAD ]: # roadbuilder
                self.place_road(gb, True)
                gb.update_grid()
                print(gb)
                self.place_road(gb)
                return True
            case [ BuildingEnum.OUTPOST, BuildingEnum.ROAD ]: # setup
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
            case BuildingEnum.TOWN:
                return self.place_city(gb)
        return False

    def place_city(self, gb:SettleGame) -> Node:
        city_upgraded = False
        while not city_upgraded:
            city_point = self.get_location_from_user(BuildingEnum.TOWN.name.lower())

            if not city_point: # quit out
                return False
            
            city_vertex = gb.tilemap.get_node_from_point(city_point)
            
            if self.check_city_vertex(city_vertex):
                city_upgraded = city_vertex.set_building(BuildingEnum.TOWN, self.id)

        return city_vertex
    
    def place_settlement(self, gb:SettleGame, setup:bool = False) -> Node:
        settlement_placed = False
        while not settlement_placed:
            settlement_point = self.get_location_from_user(BuildingEnum.OUTPOST.name.lower())

            if not settlement_point: # quit out
                return False
            
            settlement_vertex = gb.tilemap.get_node_from_point(settlement_point)

            if self.check_settlement_vertex(settlement_vertex, setup):
                settlement_placed = settlement_vertex.set_building(BuildingEnum.OUTPOST, self.id)

        return settlement_vertex
    
    def place_road(self, gb:SettleGame) -> Node:
        road_placed = False
        while not road_placed:
            road_point = self.get_location_from_user(BuildingEnum.ROAD.name.lower())

            if not road_point: # quit out
                return False
            
            road_edge = gb.tilemap.get_node_from_point(road_point)

            if self.check_road_edge(road_edge):
                road_placed = road_edge.set_building(BuildingEnum.ROAD, self.id)

        return road_edge
    

    def check_city_vertex(self, city_vertex:Node) -> bool:
        # check if spot is existing settlement under this player's id
        if city_vertex == None: # print('Couldn\'t find that spot!')
            return False

        if city_vertex.building.type != BuildingEnum.SETTLEMENT: # print('Choose a settlement to upgrade.')
            return False

        if city_vertex.player_id != self.id: # print('That isn\'t your settlement.')
            return False

        return True

    def check_settlement_vertex(self, settlement_vertex:Node, setup:bool) -> bool:
        if settlement_vertex == None: # print('Couldn\'t find that spot!')
            return False
        
        neighbor_found = False
        for neighbor in settlement_vertex.neighbors:
            if neighbor.type == NodeEnum.VERTEX:
                if neighbor.has_building() and neighbor.building.type == BuildingEnum.OUTPOST or neighbor.building.type == BuildingEnum.TOWN:
                    neighbor_found = True
                    break
            elif neighbor.type == NodeEnum.EDGE:
                for other in neighbor.neighbors:
                    if other.type == NodeEnum.VERTEX:
                        if other.has_building() and other.building.type == BuildingEnum.OUTPOST or other.building.type == BuildingEnum.TOWN:
                            neighbor_found = True
                            break
        if neighbor_found: # print('That spot is too close to another building!')
            return False
        
        if not setup: # additional rules if not during setup phase
            for neighbor in settlement_vertex.neighbors:
                if not(not neighbor.has_building() and neighbor.player_id == self.id and \
                       neighbor.building.type == BuildingEnum.ROAD): # print('Need to be at least 2 roads away from another settlement.')
                    return False
                else:
                    for neighbor2 in neighbor.neighbors:
                        if not(neighbor2.has_building() and \
                            neighbor.player_id == self.id and neighbor2.building.type == BuildingEnum.ROAD): # print('Need to be at least 2 roads away from another settlement.')
                            return False                            
        return True

    def check_road_edge(self, road_edge:Node) -> bool:
        if road_edge == None: # print('Couldn\'t find that spot!')
            return False

        for neighbor in road_edge.neighbors: # can't build a road passed another player's settlement
            if not neighbor.has_building() and neighbor.building.type == BuildingEnum.OUTPOST and \
                neighbor.building.player_id != self.id: # print('That spot is too close to another player\'s settlement!')
                return False
        
        neighbor_found = False
        for neighbor in road_edge.neighbors: # need to build next to your own settlements or roads
            if not neighbor.has_building() and neighbor.building.type == BuildingEnum.OUTPOST and neighbor.building.player_id == self.id or\
                not neighbor.has_building() and neighbor.building.type == BuildingEnum.ROAD and neighbor.building.player_id == self.id:
                neighbor_found = True
                break

        if not neighbor_found: # print('You need to be closer to your own roads/settlements!')
            return False
        
        return True


    def get_location_from_user(self, name:str, can_quit:bool = True) -> Point:
        resp = input(f'Where do you want the {name} to go, {self.name} ({self.id})? (c,#) {"(q to quit)" if can_quit else ""}\n')
        if resp == 'q':
            return None

        try:
            x = DisplayGrid.xscale_to_int(resp.split(',')[0])
            y = int(resp.split(',')[1])
            return Point(x, y)
        except:
            return Point(-1, -1)


    def calculate_victory_points(self) -> int:
        victory_points = 0
        for building in self.buildings:
            victory_points += building.victory_points
        
        for dev_card in self.played_dev_cards:
            if dev_card.type == GrowthCardEnum.VICTORY_POINT:
                victory_points += 1
        
        # TODO: check largest army + longest road | update_x()?

        return victory_points


    def update_exchange_rates(self):
        # TODO: see if we need this
        return True

    def trade(self) -> bool:
        # trade with bank
        # - show current hand
        # - if port, use its exchange rate
        # - else all resources are 4:1
        # - select resource to give, then select resource to receive
        # - confirm trade

        # trade with player
        # - select resource to give, then select resource to receive
        # - allow each other player the chance to accept or refuse
        # - collect list of players that accepted and choose 1
        # - confirm trade
        return True

    def move_robber(self, gb:SettleGame) -> bool:
        # select a tile to move the thief to (x, y since there could be dupes)
        robber_moved = False
        tile = None
        while not robber_moved:
            tile_point = self.get_location_from_user('Thief', False)
            
            if not tile_point: # can't quit out
                print('Need to place the thief.')
                continue
                        
            tile = gb.tilemap.get_tile_from_point(tile_point)
            
            if tile.id != gb.thief.get_current_tile_id():
                gb.thief.move(tile.id)
                robber_moved = True

        player_ids = []
        for node in tile.nodes:
            if node.type == NodeEnum.VERTEX and node.has_building() and node.building.player_id != self.id:
                player_ids.append(node.building.player_id)

        # show all players with settlements/cities on that tile
        print('You can steal from one of these players:')
        players_to_steal_from = []
        player_ids_to_steal_from = []
        for id in list(set(player_ids)):
            print(f'\t{gb.players[id].name}: {len(gb.players[id].resource_hand)} resource cards.')
            players_to_steal_from.append(gb.players[id].name)
            player_ids_to_steal_from.append(id)
        print()

        # select 1 to rob (id since name could be dupes)
        got_player_name = False
        while not got_player_name:
            resp = input(f'Who do you want to steal from?\n')

            if resp not in players_to_steal_from:
                continue

            # take 1 random resource from their hand
            player_to_steal_from = gb.players[player_ids_to_steal_from[players_to_steal_from.index(resp)]]
            if player_to_steal_from.resource_hand: # if the player has at least 1 resource
                resource = random.choice(player_to_steal_from.resource_hand)
                player_to_steal_from.resource_hand.remove(resource)
                self.resource_hand.append(resource)
            return True

        return True

    def play_development_card(self, gb:SettleGame) -> bool:
        print('What card do you want to play?')
        for card, count in dict(Counter(self.unplayed_dev_cards).items()).items():
            print(f'\t{str(card.name)} ({count}): {card.type.value}')
        print()
        
        match(self.unplayed_dev_cards[0].type):
            case GrowthCardEnum.KNIGHT: 
                return self.move_robber(gb)
            case GrowthCardEnum.YEAR_OF_PLENTY: 
                buyable_resources = [re for re in ResourceEnum if re not in [ ResourceEnum.DESERT, ResourceEnum.EMPTY, ResourceEnum.THREE_FOR_ONE ] ]
                buyable_resource_names = [re.value.casefold() for re in ResourceEnum if re not in [ ResourceEnum.DESERT, ResourceEnum.EMPTY, ResourceEnum.THREE_FOR_ONE ] ]
                
                resp = ''
                while resp != 'q':
                    resp = input('What resources do you want? (Resource 1, Resource 2)\n')

                    if ',' not in resp:
                        continue

                    resources = resp.split(',')

                    if resources[0].strip().casefold() not in buyable_resource_names or resources[1].strip().casefold() not in buyable_resource_names:
                        continue
                
                    resource_1 = buyable_resources[buyable_resource_names.index(resources[0].strip().casefold())]
                    resource_2 = buyable_resources[buyable_resource_names.index(resources[1].strip().casefold())]

                    self.resource_hand.append(resource_1)
                    self.resource_hand.append(resource_2)

                    return True

                # - year of plenty - add any 2 resources to hand (player class)
                return True
            case GrowthCardEnum.MONOPOLY: 
                return self.place_buildings(gb, [BuildingEnum.ROAD, BuildingEnum.ROAD])
            case GrowthCardEnum.ROAD_BUILDER: 
                # - monopoly - select one resource to take from all player's hands (player? SettleGame?)
                return True

        return True
    
    def buy_development_card(self):
        # select quantity
        # check can afford
        # pull cards from deck and add to hand
        # if type == victory_point, move card to victory point hand
        return True
    
    def take_turn(self, gb:SettleGame) -> None:
        # * Can only play 1 growth card per turn
        # Before-roll options: Play growth card or roll 
        # Roll + give out resources OR if 7; move thief + steal from a player on that tile
        # After-roll options: Buy a purchaseable item or trade with bank or players

        print(self)
        return True

    def __str__(self):
        s = f'{self.name}\'s hand is:\n'
        for type, count in dict(Counter(self.resource_hand).items()).items():
            s += f'\t({str(count)}) {type.value}\n' 
        return s + '\n'
