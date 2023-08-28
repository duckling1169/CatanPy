from game.tile import *
from game.node import *
from game.enums import *
from game.display_grid import *
from game.catanboard import CatanBoard

def run():
    gb = CatanBoard(27, 25, 1, ' ')

    gb.update_grid()

    print(gb)

run()