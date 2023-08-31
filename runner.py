from catangame import CatanGame
from game.enums import *
from game.display_grid import *
from players.player import Player
from players.aiplayer import AIPlayer
from game.developmentcard import DevelopmentCard
class Runner:

    def __init__(self):

        gb = CatanGame() 
        gb.setup_game()
        while True:
            for player in gb.players:
                player.play()

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
