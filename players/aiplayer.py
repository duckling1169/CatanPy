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
        settlement_vertex = None
        
        while not settlement_placed:
            tile_production_points = self.get_tile_production_points(gb)
            points = list(tile_production_points.keys())
            points.sort(reverse=True)
            
            for point in points:
                candidate_vertex = tile_production_points[point]
                if self.check_settlement_vertex(candidate_vertex, setup):
                    settlement_placed = candidate_vertex.set_building(BuildingEnum.OUTPOST, self.id)
                    if settlement_placed:
                        settlement_vertex = candidate_vertex
                        print(f"{self.name} placed settlement at ({candidate_vertex.x}, {candidate_vertex.y})")
                        break
            
            # If no good spots found, try any available spot
            if not settlement_placed:
                for node in gb.tilemap.nodes:
                    if node.type == NodeEnum.VERTEX and self.check_settlement_vertex(node, setup):
                        settlement_placed = node.set_building(BuildingEnum.OUTPOST, self.id)
                        if settlement_placed:
                            settlement_vertex = node
                            print(f"{self.name} placed settlement at ({node.x}, {node.y})")
                            break

        return settlement_vertex
    
    def place_road(self, gb:SettleGame) -> Node:
        road_edge = None
        road_placed = False
        
        while not road_placed:
            # Try to build roads near our settlements first
            for node in gb.tilemap.nodes:
                if node.has_building() and node.building.player_id == self.id and node.building.type == BuildingEnum.OUTPOST:
                    for neighbor in node.neighbors:
                        if neighbor.type == NodeEnum.EDGE and self.check_road_edge(neighbor):
                            road_placed = neighbor.set_building(BuildingEnum.ROAD, self.id)
                            if road_placed:
                                road_edge = neighbor
                                print(f"{self.name} placed road at ({neighbor.x}, {neighbor.y})")
                                break
                    if road_placed:
                        break
            
            # If no roads near settlements, try extending existing roads
            if not road_placed:
                for node in gb.tilemap.nodes:
                    if node.has_building() and node.building.player_id == self.id and node.building.type == BuildingEnum.ROAD:
                        for neighbor in node.neighbors:
                            if neighbor.type == NodeEnum.EDGE and self.check_road_edge(neighbor):
                                road_placed = neighbor.set_building(BuildingEnum.ROAD, self.id)
                                if road_placed:
                                    road_edge = neighbor
                                    print(f"{self.name} placed road at ({neighbor.x}, {neighbor.y})")
                                    break
                        if road_placed:
                            break

        return road_edge

    def trade(self):
        return True

    def move_robber(self, gb:SettleGame):
        """AI logic for moving the robber"""
        # Find the best tile to block (highest production that opponents use)
        best_tile = None
        best_score = -1
        
        for tile in gb.tilemap.tiles:
            if tile.id == gb.thief.current_tile_id:
                continue  # Can't stay on same tile
            
            if tile.resource == ResourceEnum.DESERT:
                continue  # Desert doesn't produce resources
            
            # Score based on opponents' buildings on this tile
            score = 0
            opponents_on_tile = []
            for node in tile.nodes:
                if node.has_building() and node.building.player_id != self.id:
                    if node.building.type == BuildingEnum.OUTPOST:
                        score += tile.resource_points * 1
                    elif node.building.type == BuildingEnum.TOWN:
                        score += tile.resource_points * 2
                    opponents_on_tile.append(node.building.player_id)
            
            if score > best_score:
                best_score = score
                best_tile = tile
        
        # Move robber to best tile or random tile if no good option
        if best_tile:
            gb.thief.move(best_tile.id)
            print(f"{self.name} moved the robber to {best_tile.resource.value} tile")
            
            # Steal from a random opponent on this tile
            opponents_on_tile = []
            for node in best_tile.nodes:
                if (node.has_building() and node.building.player_id != self.id and 
                    node.type == NodeEnum.VERTEX):
                    opponents_on_tile.append(node.building.player_id)
            
            if opponents_on_tile:
                import random
                victim_id = random.choice(list(set(opponents_on_tile)))
                victim = gb.players[victim_id]
                if victim.resource_hand:
                    stolen_resource = random.choice(victim.resource_hand)
                    victim.resource_hand.remove(stolen_resource)
                    self.resource_hand.append(stolen_resource)
                    print(f"{self.name} stole {stolen_resource.value} from {victim.name}")
        else:
            # Move to random non-desert tile
            available_tiles = [t for t in gb.tilemap.tiles if t.resource != ResourceEnum.DESERT and t.id != gb.thief.current_tile_id]
            if available_tiles:
                import random
                chosen_tile = random.choice(available_tiles)
                gb.thief.move(chosen_tile.id)
                print(f"{self.name} moved the robber to {chosen_tile.resource.value} tile")
        
        return True

    def play_development_card(self, gb:SettleGame):
        """AI logic for playing development cards"""
        if not self.unplayed_dev_cards:
            return False
        
        # Simple strategy: play knights and useful cards
        card_to_play = None
        for card in self.unplayed_dev_cards:
            if card.type in [GrowthCardEnum.KNIGHT, GrowthCardEnum.ROAD_BUILDER, GrowthCardEnum.YEAR_OF_PLENTY]:
                card_to_play = card
                break
        
        if card_to_play:
            self.unplayed_dev_cards.remove(card_to_play)
            self.played_dev_cards.append(card_to_play)
            
            print(f"{self.name} plays {card_to_play.type.name.replace('_', ' ').title()}")
            
            match card_to_play.type:
                case GrowthCardEnum.KNIGHT:
                    return self.move_robber(gb)
                case GrowthCardEnum.ROAD_BUILDER:
                    # Try to build two roads
                    roads_built = 0
                    for _ in range(2):
                        road = self.place_road(gb)
                        if road:
                            roads_built += 1
                    print(f"{self.name} built {roads_built} roads")
                    return True
                case GrowthCardEnum.YEAR_OF_PLENTY:
                    # Choose the two most needed resources
                    needed_resources = [ResourceEnum.WHEAT, ResourceEnum.ORE]  # Useful for cities and dev cards
                    for resource in needed_resources:
                        self.resource_hand.append(resource)
                    print(f"{self.name} gained {needed_resources[0].value} and {needed_resources[1].value}")
                    return True
                case GrowthCardEnum.MONOPOLY:
                    # Choose the most common resource among opponents
                    resource_counts = {}
                    for player in gb.players:
                        if player != self:
                            for resource in player.resource_hand:
                                if resource in [ResourceEnum.WHEAT, ResourceEnum.WOOD, ResourceEnum.SHEEP, ResourceEnum.ORE, ResourceEnum.BRICK]:
                                    resource_counts[resource] = resource_counts.get(resource, 0) + 1
                    
                    if resource_counts:
                        target_resource = max(resource_counts, key=resource_counts.get)
                        total_taken = 0
                        for player in gb.players:
                            if player != self:
                                count = player.resource_hand.count(target_resource)
                                for _ in range(count):
                                    player.resource_hand.remove(target_resource)
                                    self.resource_hand.append(target_resource)
                                total_taken += count
                        print(f"{self.name} monopolized {target_resource.value}, taking {total_taken} cards")
                    return True
        
        return False
    
    def take_turn(self, gb:SettleGame):
        """AI player's turn logic"""
        print(f"\n{self.name}'s turn:")
        print(self)
        
        # Simple AI strategy: try to build in order of priority
        actions_taken = 0
        max_actions = 3  # Limit actions per turn
        
        while actions_taken < max_actions:
            action_taken = False
            
            # Try to build a city if we have a settlement and resources
            from game.purchaseables import Building
            city_cost = Building(BuildingEnum.TOWN).cost
            if self.can_afford(city_cost):
                for node in gb.tilemap.nodes:
                    if (node.has_building() and node.building.player_id == self.id and 
                        node.building.type == BuildingEnum.OUTPOST):
                        if self.check_city_vertex(node):
                            node.set_building(BuildingEnum.TOWN, self.id)
                            for resource in city_cost:
                                self.resource_hand.remove(resource)
                            print(f"{self.name} upgraded settlement to city")
                            action_taken = True
                            break
            
            # Try to build a settlement if we have resources
            if not action_taken:
                settlement_cost = Building(BuildingEnum.OUTPOST).cost
                if self.can_afford(settlement_cost):
                    settlement = self.place_settlement(gb, setup=False)
                    if settlement:
                        for resource in settlement_cost:
                            self.resource_hand.remove(resource)
                        action_taken = True
            
            # Try to build a road if we have resources
            if not action_taken:
                road_cost = Building(BuildingEnum.ROAD).cost
                if self.can_afford(road_cost):
                    road = self.place_road(gb)
                    if road:
                        for resource in road_cost:
                            self.resource_hand.remove(resource)
                        action_taken = True
            
            # Try to buy a development card
            if not action_taken:
                dev_card_cost = [ResourceEnum.WHEAT, ResourceEnum.SHEEP, ResourceEnum.ORE]
                if self.can_afford(dev_card_cost):
                    card = gb.draw_development_card()
                    if card:
                        self.unplayed_dev_cards.append(card)
                        for resource in dev_card_cost:
                            self.resource_hand.remove(resource)
                        print(f"{self.name} bought a development card")
                        action_taken = True
            
            if not action_taken:
                break
            
            actions_taken += 1
        
        # Try to play a development card if we have any
        if self.unplayed_dev_cards:
            self.play_development_card(gb)
        
        return True
    
    def can_afford(self, cost):
        """Check if the AI can afford a given cost"""
        from collections import Counter
        hand_count = Counter(self.resource_hand)
        cost_count = Counter(cost)
        
        for resource, needed in cost_count.items():
            if hand_count.get(resource, 0) < needed:
                return False
        return True

    def __str__(self):
        self.resource_hand.sort()
        s = f'{self.name}\'s hand is:\n'
        for resource in self.resource_hand:
            s += f'\t{str(resource)}\n' 
        return s + '\n'
