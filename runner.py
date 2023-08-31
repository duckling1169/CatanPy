from catangame import CatanGame
from game.enums import *
from game.display_grid import *
from players.player import Player
from players.aiplayer import AIPlayer
from game.developmentcard import DevelopmentCard
class Runner():

    # 21 across, 23 down

    def __init__(self, auto=True):

        self.gb = CatanGame(auto) 

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

        self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.KNIGHT))
        self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.MONOPOLY))
        self.gb.players[0].unplayed_dev_cards.append(DevelopmentCard(DevelopmentCardEnum.ROAD_BUILDER))
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


Runner()
#.run()