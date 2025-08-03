from game.enums import NodeEnum, SideDirectionEnum, ResourceEnum
from game.side import Side
from game.node import Node
from game.point import Point
from game.tile import Tile

import random
import math

class Board():

    STARTING_CHIPS = [ 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12 ]
    
    STARTING_RESOURCES = [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, 
                ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP,
                ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, 
                ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE, 
                ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.DESERT ]
    
    START_POINT = Point(8, 3)
    
    def __init__(self, border:int, random_ports:bool):
        # shift the start point over if there's a border
        shifted = Board.START_POINT.__copy__()
        shifted.shift(border, border)

        # Get all locations for the nodes
        orig_point = shifted.__copy__()
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


        # Remove duplicates more efficiently using a dictionary
        unique_nodes = {}
        for node in all_nodes:
            key = (node.x, node.y, node.type)
            if key not in unique_nodes:
                unique_nodes[key] = node
        self.nodes = list(unique_nodes.values())
        print(f"Created {len(self.nodes)} unique nodes from {len(all_nodes)} total nodes")

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
        max_iters = 1000  # Prevent infinite loops
        self.chips = Board.STARTING_CHIPS.copy()
        while not chips_assigned_fairly(row_lengths) and iters < max_iters:
            iters += 1
            random.shuffle(self.chips)
        
        if iters >= max_iters:
            print("Warning: Could not find optimal chip placement within iteration limit. Using current arrangement.")

        self.chips.reverse()

        # DESERT SHOULD APPEAR WHERE 0 CHIP IS
        self.tile_resources = Board.STARTING_RESOURCES.copy()
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

        # Calculate neighbors more efficiently
        print("Calculating node neighbors...")
        for i, node in enumerate(self.nodes):
            if i % 20 == 0:  # Progress indicator
                print(f"Progress: {i}/{len(self.nodes)} nodes processed")
            node.neighbors = self.calculate_neighbors(node)

        # Create all 6 sides
        port_resource_collections = [
            [ResourceEnum.THREE_FOR_ONE],
            [ResourceEnum.BRICK, ResourceEnum.THREE_FOR_ONE],
            [ResourceEnum.WOOD],
            [ResourceEnum.WHEAT, ResourceEnum.THREE_FOR_ONE],
            [ResourceEnum.ORE],
            [ResourceEnum.SHEEP, ResourceEnum.THREE_FOR_ONE]
        ]
        if random_ports:
            random.shuffle(port_resource_collections)

        self.sides = []
        for direction in SideDirectionEnum:
            r = port_resource_collections.pop()
            self.sides.append(Side(self.tiles, r, direction))
        
        print(f'Completed TileMap after ({iters}) iteration(s).')

    def calculate_neighbors(self, node:Node) -> [Node]:
        """Calculate neighbors more efficiently using predefined patterns"""
        neighbors = []
        
        # For hexagonal grid, neighbors are at specific relative positions
        # This is much more efficient than calculating distance to every node
        neighbor_offsets = [
            (-2, 0), (2, 0),    # horizontal neighbors
            (-1, -2), (1, -2),  # upper diagonal
            (-1, 2), (1, 2)     # lower diagonal
        ]
        
        # Add closer neighbors for edge-vertex connections
        close_offsets = [
            (-1, -1), (1, -1), (-1, 1), (1, 1),  # close diagonal
            (0, -2), (0, 2)     # vertical
        ]
        
        all_offsets = neighbor_offsets + close_offsets
        
        for dx, dy in all_offsets:
            target_x = node.x + dx
            target_y = node.y + dy
            
            # Find node at this position
            for other in self.nodes:
                if other.x == target_x and other.y == target_y:
                    # Check if this is a valid neighbor based on node types
                    if self.are_valid_neighbors(node, other):
                        neighbors.append(other)
                    break
        
        return neighbors
    
    def are_valid_neighbors(self, node1:Node, node2:Node) -> bool:
        """Check if two nodes can be neighbors based on their types and distance"""
        dist = Point.dist(node1.x, node1.y, node2.x, node2.y)
        
        # Vertices connect to edges and other vertices at specific distances
        if node1.type == NodeEnum.VERTEX:
            if node2.type == NodeEnum.EDGE:
                return 1.8 <= dist <= 2.2  # Edges are about distance 2 from vertices
            elif node2.type == NodeEnum.VERTEX:
                return 3.8 <= dist <= 4.2  # Vertices are about distance 4 from each other
        
        # Edges connect to vertices and other edges
        elif node1.type == NodeEnum.EDGE:
            if node2.type == NodeEnum.VERTEX:
                return 1.8 <= dist <= 2.2  # Vertices are about distance 2 from edges
            elif node2.type == NodeEnum.EDGE:
                return 2.8 <= dist <= 3.2  # Edges connect to other edges at distance ~3
        
        return False

    def get_node_from_point(self, point:Point) -> Node:
        if point == None:
            return None
        
        for node in self.nodes:
            if node.x == point.x and node.y == point.y:
                return node
        return None

    def get_tile_from_point(self, point:Point) -> Tile:
        if point == None:
            return None
        
        for tile in self.tiles:
            if tile.center.x == point.x and tile.center.y == point.y:
                return tile
        return None

    def get_tile_from_id(self, id:int) -> Tile:
        for tile in self.tiles:
            if tile.id == id:
                return tile
        return None

    def __iter__(self):
        for tile in self.tiles:
            yield tile
