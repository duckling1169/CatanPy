from catangame import CatanGame
from game.enums import *
from game.display_grid import *
from players.player import Player
from players.aiplayer import AIPlayer
from game.developmentcard import DevelopmentCard
class Runner:

    # 21 across, 23 down

    def __init__(self):

        self.gb = CatanGame() 

        self.gb.tilemap.nodes[1].set_building(BuildingEnum.SETTLEMENT, 1)
        # print(self.gb.tilemap.nodes[1].is_occupied())
        self.gb.update_grid()
        print(self.gb)

        # print(self.gb.tilemap.nodes[0])
        # for neighbor in self.gb.tilemap.nodes[0].neighbors:
        #     print(neighbor)


        # for player in self.players:
        #     self.gb.update_grid()
        #     print(self.gb)
        #     player.place_buildings(self.gb, [BuildingEnum.SETTLEMENT, BuildingEnum.ROAD])

        # self.players.reverse()

        # for player in self.players:
        #     self.gb.update_grid()
        #     print(self.gb)
        #     player.place_buildings(self.gb, [BuildingEnum.SETTLEMENT, BuildingEnum.ROAD], True)

        # self.players.reverse()

        # self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.KNIGHT))
        # self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.MONOPOLY))
        # self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.ROAD_BUILDER))
        self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.YEAR_OF_PLENTY))

        self.gb.players[0].play_development_card(self.gb)

    def run(self):
        
        self.gb.update_grid()
        print(self.gb)

        # while True:
        for player in self.players:
            player.play(self.gb)

        # Before-roll options: Play Development card or roll 

        # Roll + give out resources OR if 7; move Robber + steal from a player on that tile

        # After-roll options: Buy a purchaseable item or trade with bank or players

class Tester:

    def __init__(self):
        func_list = [func for func in dir(Tester) if callable(getattr(Tester, func)) and 'test' in func ]

        for func in func_list:
            print(f'{func}: {getattr(Tester, func)()}')

    def test_nodes():
        gb = CatanGame()

        vertices = []
        edges = []
        for node in gb.tilemap.nodes:
            vertices.append(node) if node.type == NodeEnum.VERTEX else edges.append(node)
        
        return len(vertices) == 54 and len(edges) == 72

    def test_display():
        gb = CatanGame(border=1, scale=2, empty_icon='E', random_ports=False)
        gb.update_grid()
        print(gb)
        return True



    def test_create_road():
        gb = CatanGame() 

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

    def test_create_settlement():
        gb = CatanGame() 

        node_id = 0
        for i in range(len(gb.tilemap.nodes)):
            if gb.tilemap.nodes[i].type == NodeEnum.VERTEX:
                node_id = i
                break

        gb.tilemap.nodes[node_id].set_building(BuildingEnum.SETTLEMENT, 0)
        gb.update_grid()
        return gb.tilemap.nodes[node_id].has_building() and \
            gb.tilemap.nodes[node_id].building.type == BuildingEnum.SETTLEMENT and \
                gb.tilemap.nodes[node_id].building.player_id == 0

    def test_create_city():
        gb = CatanGame() 

        node_id = 0
        for i in range(len(gb.tilemap.nodes)):
            if gb.tilemap.nodes[i].type == NodeEnum.VERTEX:
                node_id = i
                break

        gb.tilemap.nodes[node_id].set_building(BuildingEnum.CITY, 0)
        gb.update_grid()
        return gb.tilemap.nodes[node_id].has_building() and \
            gb.tilemap.nodes[node_id].building.type == BuildingEnum.CITY and \
                gb.tilemap.nodes[node_id].building.player_id == 0

    def test_development_cards():
        gb = CatanGame()
        gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.KNIGHT))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.YEAR_OF_PLENTY))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.ROAD_BUILDER))
        gb.players[0].play_development_card(gb)
        gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.MONOPOLY))
        gb.players[0].play_development_card(gb)

tester = Tester()
