from settlegame import SettleGame
from game.enums import *
from game.purchaseables import GrowthCard
import random

class Runner:

    def __init__(self):
        self.game = SettleGame() 
        self.game.setup_game()
        self.current_player_index = 0
        self.game_over = False
        self.max_turns = 100  # Safety limit to prevent infinite games
        self.turn_count = 0
        
    def run_game(self):
        """Main game loop with proper turn management and win conditions"""
        print("Starting Catan game!")
        
        while not self.game_over and self.turn_count < self.max_turns:
            current_player = self.game.players[self.current_player_index]
            print(f"\n=== Turn {self.turn_count + 1}: {current_player.name}'s turn ===")
            
            # Roll dice and distribute resources
            dice_roll = self.roll_dice()
            print(f"{current_player.name} rolled {dice_roll}")
            
            if dice_roll == 7:
                # Handle robber
                self.handle_robber_roll(current_player)
            else:
                # Distribute resources
                self.distribute_resources(dice_roll)
            
            # Player's turn actions
            self.game.update_grid()
            print(self.game)
            current_player.take_turn(self.game)
            
            # Check for victory
            victory_points = current_player.calculate_victory_points(self.game)
            if victory_points >= 10:
                print(f"\n🎉 {current_player.name} wins with {victory_points} victory points!")
                self.game_over = True
                break
            
            # Next player
            self.current_player_index = (self.current_player_index + 1) % len(self.game.players)
            self.turn_count += 1
        
        if self.turn_count >= self.max_turns:
            print(f"\nGame ended after {self.max_turns} turns. No winner determined.")
    
    def roll_dice(self):
        """Roll two dice and return the sum"""
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        return die1 + die2
    
    def distribute_resources(self, dice_roll):
        """Distribute resources to players based on dice roll"""
        for tile in self.game.tilemap.tiles:
            if tile.dice_roll == dice_roll and tile.resource != ResourceEnum.DESERT:
                # Check if robber is on this tile
                if hasattr(self.game, 'thief') and self.game.thief.current_tile_id == tile.id:
                    continue  # No resources if robber is present
                    
                # Give resources to players with buildings on this tile
                for node in tile.nodes:
                    if node.has_building() and node.type == NodeEnum.VERTEX:
                        player = self.game.players[node.building.player_id]
                        resources_to_give = 1
                        if node.building.type == BuildingEnum.TOWN:
                            resources_to_give = 2  # Cities produce 2 resources
                        
                        for _ in range(resources_to_give):
                            player.resource_hand.append(tile.resource)
                        
                        print(f"{player.name} receives {resources_to_give} {tile.resource.value}")
    
    def handle_robber_roll(self, current_player):
        """Handle when a 7 is rolled - discard cards and move robber"""
        # First, players with >7 cards must discard half
        for player in self.game.players:
            if len(player.resource_hand) > 7:
                discard_count = len(player.resource_hand) // 2
                print(f"{player.name} must discard {discard_count} cards")
                # For now, discard randomly - can be improved for human players
                for _ in range(discard_count):
                    if player.resource_hand:
                        discarded = random.choice(player.resource_hand)
                        player.resource_hand.remove(discarded)
                        print(f"{player.name} discarded {discarded.value}")
        
        # Current player moves the robber
        current_player.move_robber(self.game)

class Tester:

    def __init__(self):
        func_list = [func for func in dir(Tester) if callable(getattr(Tester, func)) and 'test' in func ]

        for func in func_list:
            result = getattr(Tester, func)()
            print(f'{func}: {result}')

    @staticmethod
    def test_nodes():
        gb = SettleGame()

        vertices = []
        edges = []
        for node in gb.tilemap.nodes:
            vertices.append(node) if node.type == NodeEnum.VERTEX else edges.append(node)
        
        return len(vertices) == 54 and len(edges) == 72

    @staticmethod
    def test_display():
        gb = SettleGame(border=1, scale=2, empty_icon='E', random_ports=False)
        gb.update_grid()
        print(gb)
        return True

    @staticmethod
    def test_create_road():
        gb = SettleGame() 

        node_id = 0
        for i in range(len(gb.tilemap.nodes)):
            if gb.tilemap.nodes[i].type == NodeEnum.EDGE:
                node_id = i
                break

        gb.tilemap.nodes[node_id].set_building(BuildingEnum.ROAD, 0)
        gb.update_grid()
        return gb.tilemap.nodes[node_id].has_building() and \
            gb.tilemap.nodes[node_id].building.type == BuildingEnum.ROAD and \
                gb.tilemap.nodes[node_id].building.player_id == 0

    @staticmethod
    def test_create_settlement():
        gb = SettleGame() 

        node_id = 0
        for i in range(len(gb.tilemap.nodes)):
            if gb.tilemap.nodes[i].type == NodeEnum.VERTEX:
                node_id = i
                break

        gb.tilemap.nodes[node_id].set_building(BuildingEnum.OUTPOST, 0)
        gb.update_grid()
        return gb.tilemap.nodes[node_id].has_building() and \
            gb.tilemap.nodes[node_id].building.type == BuildingEnum.OUTPOST and \
                gb.tilemap.nodes[node_id].building.player_id == 0

    @staticmethod
    def test_create_city():
        gb = SettleGame() 

        node_id = 0
        for i in range(len(gb.tilemap.nodes)):
            if gb.tilemap.nodes[i].type == NodeEnum.VERTEX:
                node_id = i
                break

        gb.tilemap.nodes[node_id].set_building(BuildingEnum.TOWN, 0)
        gb.update_grid()
        return gb.tilemap.nodes[node_id].has_building() and \
            gb.tilemap.nodes[node_id].building.type == BuildingEnum.TOWN and \
                gb.tilemap.nodes[node_id].building.player_id == 0

    @staticmethod
    def test_development_cards():
        gb = SettleGame()
        gb.players[0].unplayed_dev_cards.append(GrowthCard(GrowthCardEnum.KNIGHT))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(GrowthCard(GrowthCardEnum.YEAR_OF_PLENTY))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(GrowthCard(GrowthCardEnum.ROAD_BUILDER))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(GrowthCard(GrowthCardEnum.MONOPOLY))
        gb.players[0].play_development_card(gb)
        return True

if __name__ == "__main__":
    # Run tests
    print("Running tests...")
    tester = Tester()
    
    # Run the game
    print("\nStarting game...")
    runner = Runner()
    runner.run_game()
