from game.node import *
from game.enums import ResourceEnum
import random

class Tile:
    
    DIMENSIONS_CORNER = [ Point(-3, 0), Point(-1, -2), Point(1, -2), 
        Point(3, 0), Point(1, 2), Point(-1, 2) ]
    
    DIMENSIONS_EDGES = [ Point(-2, -1), Point(0, -2), Point(2, -1), 
        Point(2, 1), Point(0, 2), Point(-2, 1) ]
    
    DIRECTIONS = [ '-', '|', '-', '-', '|', '-']
    
    def __init__(self, cent:Point, roll:int, id:int, re:ResourceEnum):
        self.center = cent
        self.dice_roll = roll
        self.tile_id = id
        self.resource = re
        self.nodes = []
        self.edges = []

        self.has_robber = self.resource == ResourceEnum.DESERT

        for i in range(6):
            self.nodes.append(Node(self.center.x + self.DIMENSIONS_CORNER[i].x, self.center.y + self.DIMENSIONS_CORNER[i].y, [self.tile_id]))

        for i in range(6):
            self.edges.append(Node(self.center.x + self.DIMENSIONS_EDGES[i].x, self.center.y + self.DIMENSIONS_EDGES[i].y, [self.tile_id], self.DIRECTIONS[i]))

    def get_printable_tile(self):
        strings = [ "\n" ]

        match len(self.resource.name):
            case 6:
                strings.append(" " + self.resource.name)
            case 5:
                strings.append("  " + self.resource.name)
            case 4:
                strings.append("  " + self.resource.name)
            case _:
                strings.append("   " + self.resource.name)

        if (self.has_robber):
            strings.append("    R")
        else:
            strings.append((
                "   " + self.dice_roll if self.dice_roll > 9 else (f"    {str(self.dice_roll)}")
            ))
        
        return strings
    
    def get_roll_probability(self):
        if self.resource == ResourceEnum.DESERT | self.resource == ResourceEnum.EMPTY:
            return -1
        
        return (float) (self.dice_roll - 1) / 36.0 if self.dice_roll < 7 else (float) (13 - self.dice_roll) / 36.0
    
class TileMap():

    small_chips = [ 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12 ]
    
    small_tile_resources = [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, 
                ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP,
                ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, 
                ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE, 
                ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.DESERT ]
    
    start_point = Point(5, 8)

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.tiles = []
        tile_numbers = [ 3, 4, 5, 4, 3 ]

        def chips_assigned_fairly(tile_numbers):
            # two triangles of numbers (above and below mid row)
            # 4 vertices of #s to check
            start_top = 3
            start_bottom = 12

            def find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right):
                vertex_1 = [top_left, top_right, mid]
                vertex_2 = [top_left, mid_left, mid]
                vertex_3 = [mid_left, mid, btm_left]
                vertex_4 = [mid, btm_left, btm_right]
                vertices = [vertex_1, vertex_2, vertex_3, vertex_4]

                def contains_atleast_2(a, b):
                    return sum(x in a for x in b) >= 2
                
                print(vertices)

                for vertex in vertices:
                    if contains_atleast_2([6, 8], vertex) or contains_atleast_2([2, 12], vertex):
                        return False
                return True

            for middle in range(start_top, tile_numbers[1] + start_top): # tile_numbers[1] = 4
                mid = self.small_chips[middle]
                top_left = self.small_chips[middle - 4] if middle != start_top else 0
                top_right = self.small_chips[middle - 3] if middle != start_top + tile_numbers[1] - 1 else 0
                mid_left = self.small_chips[middle - 1] if middle != start_top else 0
                btm_left = self.small_chips[middle + 4] 
                btm_right = self.small_chips[middle + 5]

                shuffled = find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right)
                if not shuffled:
                    return False
                    
            for middle in range(start_bottom, tile_numbers[3] + start_bottom): # tile_numbers[3] = 4
                mid = self.small_chips[middle]
                top_left = self.small_chips[middle + -5] 
                top_right = self.small_chips[middle + -4]
                mid_left = self.small_chips[middle - 1] if middle != start_bottom else 0
                btm_left = self.small_chips[middle + 3] if middle != start_bottom else 0
                btm_right = self.small_chips[middle + 4] if middle != start_bottom + tile_numbers[3] - 1 else 0

                shuffled = find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right)
                if not shuffled:
                    return False
            
            print(f'Shuffled: {self.small_chips}')
            return True
        
        iters = 0
        while not chips_assigned_fairly(tile_numbers):
            iters += 1
            print('Reshuffled.')
            random.shuffle(self.small_chips)

        self.small_chips.reverse()

        # DESERT SHOULD APPEAR WHERE 0 CHIP IS
        random.shuffle(self.small_tile_resources)
        self.small_tile_resources.remove(ResourceEnum.DESERT)
        self.small_tile_resources.insert(self.small_chips.index(0), ResourceEnum.DESERT)

        start = self.start_point.__copy__()

        tile_id = 0
        for i in range(len(tile_numbers)):
            for _ in range(tile_numbers[i]):
                self.tiles.append(Tile(self.start_point.__copy__(), self.small_chips.pop(), tile_id, self.small_tile_resources.pop()))
                self.start_point.shift(0, 4)
                tile_id += 1

            start.shift(4, -2) if i < 2 else start.shift(4, 2)
            self.start_point = start.__copy__()
        
        for tile in self.tiles:
            for node in tile.nodes:
                self.nodes.append(node)
            for edge in tile.edges:
                self.edges.append(edge)

        print(f'Completed TileMap with ({iters}) iteration(s).')

    def __iter__(self):
        for tile in self.tiles:
            yield tile
