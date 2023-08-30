from game.node import *
from game.enums import ResourceEnum
import random

class Tile:
    
    EDGE_DIMENSIONS = [ Point(-2, 0), Point(-1, -2), Point(1, -2), 
        Point(2, 0), Point(1, 2), Point(-1, 2) ]
    
    VERTICE_DIMENSIONS = [ Point(-2, -1), Point(0, -3), Point(2, -1), 
        Point(2, 1), Point(0, 3), Point(-2, 1) ]
    
    EDGE_ICONS = [ '|', '-', '-', '|', '-', '-' ]

    def __init__(self, center:Point, roll:int, id:int, resource:ResourceEnum, nodes:[Node]):
        self.center = center
        self.dice_roll = roll        
        self.id = id
        self.resource = resource
        self.nodes = nodes

        self.resource_points = 0
        for i in range(6):
            for j in range(6):
                if i+j+2 == self.dice_roll:
                    self.resource_points += 1

        self.has_robber = self.resource == ResourceEnum.DESERT

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
            return 0
        
        return (float) (self.dice_roll - 1) / 36.0 if self.dice_roll < 7 else (float) (13 - self.dice_roll) / 36.0
    
    def __str__(self):
        return f'Tile {self.id}\nResource: {self.resource.value}\nRoll: {self.dice_roll}'
    
class TileMap():

    chips = [ 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12 ]
    
    tile_resources = [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, 
                ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP,
                ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, 
                ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE, 
                ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.DESERT ]
    
    START_POINT = Point(6, 3)

    MIN_ACROSS = 21
    MIN_DOWN = 23
    
    def __init__(self, across, down):

        # Get all locations for the nodes
        orig_point = self.START_POINT.__copy__()
        # orig_point.shift(0, 0)
        copy_point = orig_point.__copy__()

        tile_centers = []
        all_nodes = []
        row_lengths = [ 3, 4, 5, 4, 3 ]
        for i in range(len(row_lengths)): # 0 - 4
            for _ in range(row_lengths[i]): # [ 3, 4, 5, 4, 3]
                for j in range(len(Tile.VERTICE_DIMENSIONS)): # same amount of edges and vertices
                    all_nodes.append(Node(copy_point.x + Tile.VERTICE_DIMENSIONS[j].x, copy_point.y + Tile.VERTICE_DIMENSIONS[j].y, NodeEnum.VERTEX))
                    all_nodes.append(Node(copy_point.x + Tile.EDGE_DIMENSIONS[j].x, copy_point.y + Tile.EDGE_DIMENSIONS[j].y, NodeEnum.EDGE))
                
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
