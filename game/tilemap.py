from game.enums import NodeEnum, SideDirectionEnum, ResourceEnum
from game.side import Side
from game.node import Node
from game.point import Point
from game.tile import Tile

import random
import math

class TileMap():

    chips = [ 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12 ]
    
    tile_resources = [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, 
                ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP,
                ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, 
                ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE, 
                ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.DESERT ]
    
    START_POINT = Point(6, 3)
    
    def __init__(self, border):
        # shift the start point over if there's a border
        self.START_POINT.shift(border, border)

        # Get all locations for the nodes
        orig_point = self.START_POINT.__copy__()
        copy_point = orig_point.__copy__()

        tile_centers = []
        all_nodes = []
        row_lengths = [ 3, 4, 5, 4, 3 ]
        for i in range(len(row_lengths)): # 0 - 4
            for _ in range(row_lengths[i]): # [ 3, 4, 5, 4, 3]
                for j in range(len(Tile.VERTICE_DIMENSIONS)): # same amount of edges and vertices
                    all_nodes.append(Node(x=copy_point.x + Tile.VERTICE_DIMENSIONS[j].x, y=copy_point.y + Tile.VERTICE_DIMENSIONS[j].y, type=NodeEnum.VERTEX))
                    all_nodes.append(Node(x=copy_point.x + Tile.EDGE_DIMENSIONS[j].x, y=copy_point.y + Tile.EDGE_DIMENSIONS[j].y, type=NodeEnum.EDGE))
                
                tile_centers.append(copy_point.__copy__())
                copy_point.shift(4, 0)

            orig_point.shift(-2, 4) if i < 2 else orig_point.shift(2, 4)
            copy_point = orig_point.__copy__()

        self.nodes = list(set(all_nodes))

        # Distributes chips according to Catan rules
        def chips_assigned_fairly(tile_numbers):
            start_top = 3
            start_bottom = 12

            def find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right):
                vertices = [[top_left, top_right, mid], [top_left, mid_left, mid], [mid_left, mid, btm_left], [mid, btm_left, btm_right]]

                def contains_atleast_2(a, b):
                    return sum(x in a for x in b) >= 2
                
                for vertex in vertices:
                    if contains_atleast_2([6, 8], vertex) or contains_atleast_2([2, 12], vertex):
                        return False
                return True

            for middle in range(start_top, tile_numbers[1] + start_top): # tile_numbers[1] = 4
                mid = self.chips[middle]
                top_left = self.chips[middle - 4] if middle != start_top else 0
                top_right = self.chips[middle - 3] if middle != start_top + tile_numbers[1] - 1 else 0
                mid_left = self.chips[middle - 1] if middle != start_top else 0
                btm_left = self.chips[middle + 4] 
                btm_right = self.chips[middle + 5]

                shuffled = find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right)
                if not shuffled:
                    return False
                    
            for middle in range(start_bottom, tile_numbers[3] + start_bottom): # tile_numbers[3] = 4
                mid = self.chips[middle]
                top_left = self.chips[middle - 5] 
                top_right = self.chips[middle - 4]
                mid_left = self.chips[middle - 1] if middle != start_bottom else 0
                btm_left = self.chips[middle + 3] if middle != start_bottom else 0
                btm_right = self.chips[middle + 4] if middle != start_bottom + tile_numbers[3] - 1 else 0

                shuffled = find_illegal_chips(top_left, top_right, mid_left, mid, btm_left, btm_right)
                if not shuffled:
                    return False
            
            return True
        
        iters = 0
        while not chips_assigned_fairly(row_lengths):
            iters += 1
            random.shuffle(self.chips)

        self.chips.reverse()

        # DESERT SHOULD APPEAR WHERE 0 CHIP IS
        random.shuffle(self.tile_resources)
        self.tile_resources.remove(ResourceEnum.DESERT)
        self.tile_resources.insert(self.chips.index(0), ResourceEnum.DESERT)

        # Creates the Tiles with shared nodes
        self.tiles = []
        for i in range(len(tile_centers)):
            tile_nodes = []
            for node in self.nodes:
                for j in range(len(Tile.VERTICE_DIMENSIONS)):
                    if node.type == NodeEnum.VERTEX and node.x == tile_centers[i].x + Tile.VERTICE_DIMENSIONS[j].x and node.y == tile_centers[i].y + Tile.VERTICE_DIMENSIONS[j].y:
                        tile_nodes.append(node)
                    elif node.type == NodeEnum.EDGE and node.x == tile_centers[i].x + Tile.EDGE_DIMENSIONS[j].x and node.y == tile_centers[i].y + Tile.EDGE_DIMENSIONS[j].y:
                        node.icon = Tile.EDGE_ICONS[j]
                        tile_nodes.append(node)

            self.tiles.append(Tile(tile_centers[i], self.chips.pop(), i, self.tile_resources.pop(), tile_nodes))
    
        # Adds tiles_touching and neighbors to nodes
        for tile in self.tiles:
            for node in tile.nodes:
                for other_tile in self.tiles:
                    for other_node in other_tile.nodes:
                        if node == other_node:
                            node.tiles_touching.append(other_tile.id)
                node.tiles_touching = list(set(node.tiles_touching))

        for node in self.nodes:
            node.neighbors = self.calculate_neighbors(node)


        side1 = Side(self.tiles, 
                     [ResourceEnum.THREE_FOR_ONE], 
                     SideDirectionEnum.BOTTOM)
        side2 = Side(self.tiles, 
                     [ResourceEnum.BRICK, ResourceEnum.THREE_FOR_ONE], 
                     SideDirectionEnum.BOTTOM_LEFT)
        side3 = Side(self.tiles, 
                     [ResourceEnum.WOOD], 
                     SideDirectionEnum.TOP_LEFT)
        side4 = Side(self.tiles, 
                     [ResourceEnum.WHEAT, ResourceEnum.THREE_FOR_ONE], 
                     SideDirectionEnum.TOP)
        side5 = Side(self.tiles, 
                     [ResourceEnum.ORE], 
                     SideDirectionEnum.TOP_RIGHT)
        side6 = Side(self.tiles, 
                     [ResourceEnum.SHEEP, ResourceEnum.THREE_FOR_ONE], 
                     SideDirectionEnum.BOTTOM_RIGHT)
        
        self.sides = [ side1, 
                      side2, 
                      side3, 
                      side4, 
                      side5, 
                      side6 
        ]
        
        print(f'Completed TileMap after ({iters}) iteration(s).')


    def calculate_neighbors(self, node:Node):
        neighbors = []

        dists = {}
        for other in self.nodes:
            dist = math.floor(Point.dist(node.x, node.y, other.x, other.y))
            if dist in dists:
                dists[dist].append((node, other))
            elif dist != 0:
                dists[dist] = [(node, other)]

        distances = list(set(dists.keys()))
        distances.sort()

        for distances in distances[:2]:
            for node, other in dists[distances]:
                neighbors.append(other)

        return neighbors

    def get_node_from_point(self, point:Point):
        if point == None:
            return None
        
        for node in self.nodes:
            if node.x == point.x and node.y == point.y:
                return node
        return None

    def get_tile_from_id(self, id:int):
        for tile in self.tiles:
            if tile.id == id:
                return tile
        return None

    def __iter__(self):
        for tile in self.tiles:
            yield tile
