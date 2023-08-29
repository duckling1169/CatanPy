from game.node import *
from game.enums import ResourceEnum
import random

class Tile:
    
    DIMENSIONS_CORNER = [ Point(-3, 0), Point(-1, -2), Point(1, -2), 
        Point(3, 0), Point(1, 2), Point(-1, 2) ]
    
    DIMENSIONS_EDGES = [ Point(-2, -1), Point(0, -2), Point(2, -1), 
        Point(2, 1), Point(0, 2), Point(-2, 1) ]
    
    DIRECTIONS = [ '-', '|', '-', '-', '|', '-']

    def __init__(self, center:Point, roll:int, id:int, resource:ResourceEnum, nodes:[Node]):
        self.center = center
        self.dice_roll = roll
        self.id = id
        self.resource = resource
        self.nodes = nodes

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
            return -1
        
        return (float) (self.dice_roll - 1) / 36.0 if self.dice_roll < 7 else (float) (13 - self.dice_roll) / 36.0
    
    
class TileMap():

    small_chips = [ 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12 ]
    
    small_tile_resources = [ ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, ResourceEnum.WHEAT, 
                ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP, ResourceEnum.SHEEP,
                ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, ResourceEnum.WOOD, 
                ResourceEnum.ORE, ResourceEnum.ORE, ResourceEnum.ORE, 
                ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.BRICK, ResourceEnum.DESERT ]
    
    def __init__(self):
        self.tiles = []
        self.nodes = []
        row_lengths = [ 3, 4, 5, 4, 3 ]

        # Get all locations for the nodes
        def get_node_locations(self, row_lengths):
            start_point = Point(5, 8)
            tile_centers = []
            start = start_point.__copy__()

            for i in range(len(row_lengths)):
                for _ in range(row_lengths[i]):
                    tile_centers.append(start_point.__copy__())
                    start_point.shift(0, 4)

                start.shift(4, -2) if i < 2 else start.shift(4, 2)
                start_point = start.__copy__()

            all_nodes = []
            for center in tile_centers:
                for i in range(6): # up to 6 unique Nodes for each: edges and vertices
                    all_nodes.append(Node(center.x + Tile.DIMENSIONS_CORNER[i].x, center.y + Tile.DIMENSIONS_CORNER[i].y, NodeEnum.VERTEX))
                    all_nodes.append(Node(center.x + Tile.DIMENSIONS_EDGES[i].x, center.y + Tile.DIMENSIONS_EDGES[i].y, NodeEnum.EDGE))

            for node in set(all_nodes):
                self.nodes.append(Node(node.x, node.y, node.type))

            return tile_centers
        
        tile_centers = get_node_locations(self, row_lengths)

        # Distributes chips according to Catan rules
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
            
            return True
        
        iters = 0
        while not chips_assigned_fairly(row_lengths):
            iters += 1
            random.shuffle(self.small_chips)

        self.small_chips.reverse()

        # DESERT SHOULD APPEAR WHERE 0 CHIP IS
        random.shuffle(self.small_tile_resources)
        self.small_tile_resources.remove(ResourceEnum.DESERT)
        self.small_tile_resources.insert(self.small_chips.index(0), ResourceEnum.DESERT)

        # Creates the Tiles with shared nodes
        def create_tiles(self, tile_centers):
            tile_id = 0
            tiles = []
            for center in tile_centers:
                tile_nodes = []
                for node in self.nodes:
                    for i in range(6):
                        if node.type == NodeEnum.VERTEX and node.x == center.x + Tile.DIMENSIONS_CORNER[i].x and node.y == center.y + Tile.DIMENSIONS_CORNER[i].y:
                            tile_nodes.append(node)
                        elif node.type == NodeEnum.EDGE and node.x == center.x + Tile.DIMENSIONS_EDGES[i].x and node.y == center.y + Tile.DIMENSIONS_EDGES[i].y:
                            node.icon = Tile.DIRECTIONS[i]
                            tile_nodes.append(node)

                tiles.append(Tile(center.__copy__(), self.small_chips.pop(), tile_id, self.small_tile_resources.pop(), nodes=tile_nodes))
                tile_id += 1
            return tiles
    
        self.tiles = create_tiles(self, tile_centers)

        # Adds tiles_touching and neighbors to nodes
        def add_neighbors(self):
            for tile in self.tiles:
                for node in tile.nodes:
                    for other_tile in self.tiles:
                        for other_node in other_tile.nodes:
                            if node == other_node:
                                node.tiles_touching.append(other_tile.id)
                    node.tiles_touching = list(set(node.tiles_touching))

            for node in self.nodes:
                node.neighbors = self.calculate_neighbors(node).copy()

        add_neighbors(self)

        print(f'Completed TileMap after ({iters}) iteration(s).')


    def calculate_neighbors(self, node:Node):
        neighbors = []

        def calculate_distances(array:[Node]):
            dists = {}
            for other in array:
                dist = math.floor(Point.dist(node.x, node.y, other.x, other.y))
                if dist in dists:
                    dists[dist].append((node, other))
                elif dist != 0:
                    dists[dist] = [(node, other)]

            distances = list(set(dists.keys()))
            distances.sort()
            return distances, dists

        distances, dists = calculate_distances(self.nodes)

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

    def get_node_from_id(self, id:int):
        if point == None:
            return None

        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def __iter__(self):
        for tile in self.tiles:
            yield tile


	# public boolean checkOtherSettlements(KeyPoint kp) {
	# 	CustomPoint cp = null;
	# 	for (Point p : Tile.CORNER_CHECKS) {
	# 		cp = new CustomPoint(kp.getPoint().x + p.x, kp.getPoint().y + p.y);
	# 		if (inBounds(cp)) {
	# 			for (KeyPoint vertex : this.vertices) {
	# 				if (isSameLocation(cp, vertex.getPoint()) && vertex.isOccupied()) {
	# 					return false;
	# 				}
	# 			}
	# 		}
	# 	}
	# 	return true;
	# }