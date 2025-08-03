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

        building_type = types[0]
        # Check if player can afford the building
        from game.purchaseables import Building
        temp_building = Building(building_type)
        
        # Count resources in hand
        from collections import Counter
        hand_count = Counter(self.resource_hand)
        cost_count = Counter(temp_building.cost)
        
        # Check if we have enough of each required resource
        for resource, needed in cost_count.items():
            if hand_count.get(resource, 0) < needed:
                print(f'You cannot afford that! Need {needed} {resource.value}, have {hand_count.get(resource, 0)}')
                return False

        # Deduct cost from hand
        for resource in temp_building.cost:
            self.resource_hand.remove(resource)
        
        match building_type:
            case BuildingEnum.ROAD:
                return self.place_road(gb)
            case BuildingEnum.OUTPOST:
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
        if city_vertex == None:
            print('Couldn\'t find that spot!')
            return False

        if not city_vertex.has_building() or city_vertex.building.type != BuildingEnum.OUTPOST:
            print('Choose a settlement to upgrade.')
            return False

        if city_vertex.building.player_id != self.id:
            print('That isn\'t your settlement.')
            return False

        return True

    def check_settlement_vertex(self, settlement_vertex:Node, setup:bool) -> bool:
        if settlement_vertex == None:
            print('Couldn\'t find that spot!')
            return False
        
        if settlement_vertex.has_building():
            print('That spot is already occupied!')
            return False
        
        if settlement_vertex.type != NodeEnum.VERTEX:
            print('Settlements can only be placed on vertices!')
            return False
        
        # Check distance rule - no settlements within 2 edges (1 vertex) of each other
        for neighbor in settlement_vertex.neighbors:
            if neighbor.type == NodeEnum.VERTEX and neighbor.has_building():
                if neighbor.building.type in [BuildingEnum.OUTPOST, BuildingEnum.TOWN]:
                    print('That spot is too close to another building!')
                    return False
        
        # During regular play, must be connected to own road
        if not setup:
            connected_to_own_road = False
            for neighbor in settlement_vertex.neighbors:
                if neighbor.type == NodeEnum.EDGE and neighbor.has_building():
                    if neighbor.building.type == BuildingEnum.ROAD and neighbor.building.player_id == self.id:
                        connected_to_own_road = True
                        break
            
            if not connected_to_own_road:
                print('Settlement must be connected to your road!')
                return False
                            
        return True

    def check_road_edge(self, road_edge:Node) -> bool:
        if road_edge == None:
            print('Couldn\'t find that spot!')
            return False

        if road_edge.has_building():
            print('That spot already has a road!')
            return False

        if road_edge.type != NodeEnum.EDGE:
            print('Roads can only be placed on edges!')
            return False

        # Check if we can connect to our own network
        connected_to_own_network = False
        for neighbor in road_edge.neighbors:
            if neighbor.has_building() and neighbor.building.player_id == self.id:
                if neighbor.building.type in [BuildingEnum.OUTPOST, BuildingEnum.TOWN, BuildingEnum.ROAD]:
                    # Check if there's a blocking settlement
                    if neighbor.type == NodeEnum.VERTEX and neighbor.building.type in [BuildingEnum.OUTPOST, BuildingEnum.TOWN]:
                        # Can't build through another player's settlement
                        blocking_settlement = False
                        for other_neighbor in neighbor.neighbors:
                            if other_neighbor != road_edge and other_neighbor.has_building():
                                if other_neighbor.building.player_id != self.id and other_neighbor.building.type in [BuildingEnum.OUTPOST, BuildingEnum.TOWN]:
                                    blocking_settlement = True
                                    break
                        if not blocking_settlement:
                            connected_to_own_network = True
                            break
                    else:
                        connected_to_own_network = True
                        break

        if not connected_to_own_network:
            print('You need to connect to your own roads or settlements!')
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


    def calculate_victory_points(self, gb:SettleGame=None) -> int:
        victory_points = 0
        
        # Count buildings (settlements = 1, cities = 2)
        building_points = 0
        if hasattr(self, 'buildings') and self.buildings:
            for building in self.buildings:
                building_points += building.victory_points
        else:
            # Calculate from nodes on the board
            if gb:
                for node in gb.tilemap.nodes:
                    if node.has_building() and node.building.player_id == self.id:
                        if node.building.type == BuildingEnum.OUTPOST:
                            building_points += 1
                        elif node.building.type == BuildingEnum.TOWN:
                            building_points += 2
        
        victory_points += building_points
        
        # Count victory point cards
        for dev_card in self.played_dev_cards:
            if dev_card.type == GrowthCardEnum.VICTORY_POINT:
                victory_points += 1
        
        # Check for largest army (3+ knights played)
        knights_played = sum(1 for card in self.played_dev_cards if card.type == GrowthCardEnum.KNIGHT)
        if gb and knights_played >= 3:
            largest_army = True
            for other_player in gb.players:
                if other_player != self:
                    other_knights = sum(1 for card in other_player.played_dev_cards if card.type == GrowthCardEnum.KNIGHT)
                    if other_knights >= knights_played:
                        largest_army = False
                        break
            if largest_army:
                victory_points += 2
        
        # Check for longest road (5+ connected roads)
        if gb:
            longest_road_length = self.calculate_longest_road(gb)
            if longest_road_length >= 5:
                longest_road = True
                for other_player in gb.players:
                    if other_player != self:
                        other_road_length = other_player.calculate_longest_road(gb)
                        if other_road_length >= longest_road_length:
                            longest_road = False
                            break
                if longest_road:
                    victory_points += 2

        return victory_points
    
    def calculate_longest_road(self, gb:SettleGame) -> int:
        """Calculate the longest continuous road for this player"""
        # Find all road nodes belonging to this player
        road_nodes = []
        for node in gb.tilemap.nodes:
            if (node.has_building() and node.building.player_id == self.id and 
                node.building.type == BuildingEnum.ROAD):
                road_nodes.append(node)
        
        if not road_nodes:
            return 0
        
        # Use DFS to find longest path
        max_length = 0
        for start_node in road_nodes:
            visited = set()
            length = self._dfs_longest_road(start_node, road_nodes, visited, gb)
            max_length = max(max_length, length)
        
        return max_length
    
    def _dfs_longest_road(self, current_node, road_nodes, visited, gb:SettleGame) -> int:
        """DFS helper for calculating longest road"""
        visited.add(current_node)
        max_length = 1
        
        for neighbor in current_node.neighbors:
            # Check if neighbor is a road belonging to this player and not visited
            if (neighbor in road_nodes and neighbor not in visited):
                # Check if path is not blocked by opponent's settlement
                blocked = False
                for intermediate in current_node.neighbors:
                    if (intermediate.type == NodeEnum.VERTEX and intermediate.has_building() and
                        intermediate.building.player_id != self.id and 
                        intermediate.building.type in [BuildingEnum.OUTPOST, BuildingEnum.TOWN]):
                        # Check if this settlement blocks the path to neighbor
                        if neighbor in intermediate.neighbors:
                            blocked = True
                            break
                
                if not blocked:
                    length = 1 + self._dfs_longest_road(neighbor, road_nodes, visited.copy(), gb)
                    max_length = max(max_length, length)
        
        return max_length


    def update_exchange_rates(self):
        # TODO: see if we need this
        return True

    def trade(self, gb:SettleGame) -> bool:
        """Handle trading with bank or other players"""
        print("Trade options:")
        print("1. Trade with bank")
        print("2. Trade with players")
        print("3. Skip trading")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            return self.trade_with_bank(gb)
        elif choice == "2":
            return self.trade_with_players(gb)
        else:
            return True
    
    def trade_with_bank(self, gb:SettleGame) -> bool:
        """Trade resources with the bank"""
        if not self.resource_hand:
            print("You have no resources to trade!")
            return False
        
        print("Your resources:")
        resource_counts = {}
        for resource in self.resource_hand:
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
        
        for resource, count in resource_counts.items():
            print(f"  {resource.value}: {count}")
        
        # Check for port bonuses (simplified - would need to check actual ports)
        tradeable_resources = []
        for resource, count in resource_counts.items():
            rate = self.exchange_rates.get(resource, 4)
            if count >= rate:
                tradeable_resources.append((resource, rate))
        
        if not tradeable_resources:
            print("You don't have enough resources for any trades!")
            return False
        
        print("\nAvailable trades:")
        for i, (resource, rate) in enumerate(tradeable_resources):
            print(f"{i+1}. Give {rate} {resource.value} for 1 of any resource")
        
        try:
            choice = int(input("Choose trade (number): ")) - 1
            if 0 <= choice < len(tradeable_resources):
                give_resource, rate = tradeable_resources[choice]
                
                receive_options = [ResourceEnum.WHEAT, ResourceEnum.WOOD, ResourceEnum.SHEEP, ResourceEnum.ORE, ResourceEnum.BRICK]
                print("Choose resource to receive:")
                for i, resource in enumerate(receive_options):
                    print(f"{i+1}. {resource.value}")
                
                receive_choice = int(input("Choose resource (number): ")) - 1
                if 0 <= receive_choice < len(receive_options):
                    receive_resource = receive_options[receive_choice]
                    
                    # Execute trade
                    for _ in range(rate):
                        self.resource_hand.remove(give_resource)
                    self.resource_hand.append(receive_resource)
                    
                    print(f"Traded {rate} {give_resource.value} for 1 {receive_resource.value}")
                    return True
        except (ValueError, IndexError):
            print("Invalid choice!")
        
        return False
    
    def trade_with_players(self, gb:SettleGame) -> bool:
        """Trade resources with other players"""
        if not self.resource_hand:
            print("You have no resources to trade!")
            return False
        
        other_players = [p for p in gb.players if p != self]
        if not other_players:
            print("No other players to trade with!")
            return False
        
        print("Your resources:")
        my_counts = {}
        for resource in self.resource_hand:
            my_counts[resource] = my_counts.get(resource, 0) + 1
        
        for resource, count in my_counts.items():
            print(f"  {resource.value}: {count}")
        
        # Simple trading interface (can be enhanced)
        print("\nOther players:")
        for i, player in enumerate(other_players):
            print(f"{i+1}. {player.name} ({len(player.resource_hand)} resources)")
        
        try:
            player_choice = int(input("Choose player to trade with (number): ")) - 1
            if 0 <= player_choice < len(other_players):
                other_player = other_players[player_choice]
                
                print(f"Propose a trade with {other_player.name}")
                # For simplicity, just ask for resource types
                # In a full implementation, you'd have a more sophisticated trade interface
                
                available_resources = list(my_counts.keys())
                print("Your resources to offer:")
                for i, resource in enumerate(available_resources):
                    print(f"{i+1}. {resource.value}")
                
                offer_choice = int(input("Choose resource to offer: ")) - 1
                if 0 <= offer_choice < len(available_resources):
                    offer_resource = available_resources[offer_choice]
                    
                    want_options = [ResourceEnum.WHEAT, ResourceEnum.WOOD, ResourceEnum.SHEEP, ResourceEnum.ORE, ResourceEnum.BRICK]
                    print("What do you want in return:")
                    for i, resource in enumerate(want_options):
                        print(f"{i+1}. {resource.value}")
                    
                    want_choice = int(input("Choose resource you want: ")) - 1
                    if 0 <= want_choice < len(want_options):
                        want_resource = want_options[want_choice]
                        
                        # Check if other player has the resource
                        if want_resource in other_player.resource_hand:
                            # Simple acceptance (could add AI logic for other player)
                            if isinstance(other_player, type(self)):  # Human player
                                accept = input(f"{other_player.name}, do you accept trading 1 {want_resource.value} for 1 {offer_resource.value}? (y/n): ").lower() == 'y'
                            else:  # AI player - simple logic
                                # AI accepts if they need the offered resource more than what they're giving
                                accept = other_player.resource_hand.count(want_resource) > 1
                            
                            if accept:
                                # Execute trade
                                self.resource_hand.remove(offer_resource)
                                other_player.resource_hand.append(offer_resource)
                                other_player.resource_hand.remove(want_resource)
                                self.resource_hand.append(want_resource)
                                
                                print(f"Trade completed! You gave {offer_resource.value} and received {want_resource.value}")
                                return True
                            else:
                                print("Trade rejected!")
                        else:
                            print(f"{other_player.name} doesn't have {want_resource.value}!")
        except (ValueError, IndexError):
            print("Invalid choice!")
        
        return False

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
        if not self.unplayed_dev_cards:
            print('You have no development cards to play!')
            return False
            
        print('Available development cards:')
        card_types = {}
        for i, card in enumerate(self.unplayed_dev_cards):
            card_name = card.type.name.replace('_', ' ').title()
            if card_name not in card_types:
                card_types[card_name] = []
            card_types[card_name].append(i)
        
        for card_name, indices in card_types.items():
            print(f'\t{card_name} ({len(indices)})')
        
        # For now, just play the first card (can be improved for user choice)
        card_to_play = self.unplayed_dev_cards.pop(0)
        self.played_dev_cards.append(card_to_play)
        
        print(f'Playing {card_to_play.type.name.replace("_", " ").title()}: {card_to_play.type.value}')
        
        match card_to_play.type:
            case GrowthCardEnum.KNIGHT: 
                return self.move_robber(gb)
            case GrowthCardEnum.YEAR_OF_PLENTY: 
                buyable_resources = [ResourceEnum.WHEAT, ResourceEnum.WOOD, ResourceEnum.SHEEP, ResourceEnum.ORE, ResourceEnum.BRICK]
                buyable_resource_names = [re.value.lower() for re in buyable_resources]
                
                print('Available resources: ' + ', '.join([r.value for r in buyable_resources]))
                
                resources_gained = 0
                while resources_gained < 2:
                    resp = input(f'Choose resource {resources_gained + 1}/2: ').lower().strip()
                    
                    if resp in buyable_resource_names:
                        resource = buyable_resources[buyable_resource_names.index(resp)]
                        self.resource_hand.append(resource)
                        print(f'Added {resource.value} to your hand')
                        resources_gained += 1
                    else:
                        print('Invalid resource. Try again.')

                return True
            case GrowthCardEnum.MONOPOLY: 
                buyable_resources = [ResourceEnum.WHEAT, ResourceEnum.WOOD, ResourceEnum.SHEEP, ResourceEnum.ORE, ResourceEnum.BRICK]
                buyable_resource_names = [re.value.lower() for re in buyable_resources]
                
                print('Available resources: ' + ', '.join([r.value for r in buyable_resources]))
                
                while True:
                    resp = input('Choose a resource to monopolize: ').lower().strip()
                    if resp in buyable_resource_names:
                        resource = buyable_resources[buyable_resource_names.index(resp)]
                        total_taken = 0
                        for other_player in gb.players:
                            if other_player != self:
                                count = other_player.resource_hand.count(resource)
                                for _ in range(count):
                                    other_player.resource_hand.remove(resource)
                                    self.resource_hand.append(resource)
                                total_taken += count
                        print(f'Took {total_taken} {resource.value} from other players')
                        return True
                    else:
                        print('Invalid resource. Try again.')
            case GrowthCardEnum.ROAD_BUILDER: 
                return self.place_buildings(gb, [BuildingEnum.ROAD, BuildingEnum.ROAD])
            case GrowthCardEnum.VICTORY_POINT:
                print('Victory point card played - adds to your victory points!')
                return True

        return True
    
    def buy_development_card(self, gb:SettleGame):
        """Buy a development card from the deck"""
        cost = [ResourceEnum.WHEAT, ResourceEnum.SHEEP, ResourceEnum.ORE]
        
        # Check if player can afford it
        from collections import Counter
        hand_count = Counter(self.resource_hand)
        cost_count = Counter(cost)
        
        for resource, needed in cost_count.items():
            if hand_count.get(resource, 0) < needed:
                print(f'Cannot afford development card! Need {needed} {resource.value}, have {hand_count.get(resource, 0)}')
                return False
        
        # Check if deck has cards
        card = gb.draw_development_card()
        if not card:
            print("No more development cards available!")
            return False
        
        # Deduct cost
        for resource in cost:
            self.resource_hand.remove(resource)
        
        # Add card to hand
        self.unplayed_dev_cards.append(card)
        
        print(f"Bought development card: {card.type.name.replace('_', ' ').title()}")
        return True
    
    def take_turn(self, gb:SettleGame) -> None:
        """Complete turn implementation for human players"""
        print(f"\n=== {self.name}'s Turn ===")
        print(self)
        
        # Pre-roll phase: option to play development card
        if self.unplayed_dev_cards:
            play_card = input("Do you want to play a development card before rolling? (y/n): ").lower() == 'y'
            if play_card:
                self.play_development_card(gb)
        
        print("(Dice will be rolled automatically)")
        
        # Main phase: building, trading, buying
        actions_remaining = True
        while actions_remaining:
            print("\nAvailable actions:")
            print("1. Build settlement (costs: Wheat, Sheep, Brick, Wood)")
            print("2. Build city (costs: 2 Wheat, 3 Ore)")
            print("3. Build road (costs: Brick, Wood)")
            print("4. Buy development card (costs: Wheat, Sheep, Ore)")
            print("5. Trade")
            print("6. End turn")
            
            try:
                choice = input("Choose action (1-6): ").strip()
                
                if choice == "1":
                    success = self.place_buildings(gb, [BuildingEnum.OUTPOST])
                    if success:
                        print("Settlement built successfully!")
                    else:
                        print("Could not build settlement.")
                        
                elif choice == "2":
                    success = self.place_buildings(gb, [BuildingEnum.TOWN])
                    if success:
                        print("City built successfully!")
                    else:
                        print("Could not build city.")
                        
                elif choice == "3":
                    success = self.place_buildings(gb, [BuildingEnum.ROAD])
                    if success:
                        print("Road built successfully!")
                    else:
                        print("Could not build road.")
                        
                elif choice == "4":
                    success = self.buy_development_card(gb)
                    if success:
                        print("Development card purchased!")
                    else:
                        print("Could not buy development card.")
                        
                elif choice == "5":
                    self.trade(gb)
                    
                elif choice == "6":
                    actions_remaining = False
                    
                else:
                    print("Invalid choice. Please choose 1-6.")
                    
            except KeyboardInterrupt:
                print("\nEnding turn...")
                actions_remaining = False
        
        print(f"End of {self.name}'s turn")
        return True

    def __str__(self):
        s = f'{self.name}\'s hand is:\n'
        for type, count in dict(Counter(self.resource_hand).items()).items():
            s += f'\t({str(count)}) {type.value}\n' 
        return s + '\n'
