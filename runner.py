from game.tile import *
from game.node import *
from game.enums import *
from game.display_grid import *
from game.catanboard import CatanBoard
from players.player import Player
from players.aiplayer import AIPlayer
class Runner():

    # 21 across, 23 down

    def __init__(self, auto):

        self.gb = CatanBoard() 
        self.players = []

        if auto:
            self.players = [ Player('Adam', 0), AIPlayer('CatanBot', 1) ]

        else:
            resp = ''
            id = 0
            while resp != 'q' or len(self.players) > 3:
                resp = input('Enter next player name or \'ai\' (q to 8,Mstop): ')
                if resp != 'q':
                    self.players.append(AIPlayer(resp, id)) if resp == 'ai' else self.players.append(Player(resp, id))
                id += 1

        # self.gb.tilemap.nodes[1].set_building(BuildingEnum.SETTLEMENT, 1)
        # print(self.gb.tilemap.nodes[1].is_occupied())
        # self.gb.update_grid()
        # print(self.gb)

        # print(self.gb.tilemap.nodes[0])
        # for neighbor in self.gb.tilemap.nodes[0].neighbors:
        #     print(neighbor)

        for player in self.players:
            self.gb.update_grid()
            print(self.gb)
            player.place_buildings(self.gb, [BuildingEnum.SETTLEMENT, BuildingEnum.ROAD])

        self.players.reverse()

        for player in self.players:
            self.gb.update_grid()
            print(self.gb)
            player.place_buildings(self.gb, [BuildingEnum.SETTLEMENT, BuildingEnum.ROAD], True)

        self.players.reverse()


    def run(self):
        
        self.gb.update_grid()
        print(self.gb)

        # while True:
        for player in self.players:
            player.play(self.gb)

Runner(True).run()