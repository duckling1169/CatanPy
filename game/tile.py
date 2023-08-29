from game.node import *
from game.enums import ResourceEnum
import random

class Tile:
    
    DIMENSIONS_CORNER = [ Point(-3, 0), Point(-1, -2), Point(1, -2), 
        Point(3, 0), Point(1, 2), Point(-1, 2) ]
    
    DIMENSIONS_EDGES = [ Point(-2, -1), Point(0, -2), Point(2, -1), 
        Point(2, 1), Point(0, 2), Point(-2, 1) ]
    
    DIRECTIONS = [ '-', '|', '-', '-', '|', '-']

    def __init__(self, center:Point, roll:int, id:int, resource:ResourceEnum, corners:[Node], edges:[Node]):
        self.center = center
        self.dice_roll = roll
        self.id = id
        self.resource = resource
        self.corners = corners
        self.edges = edges

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
        self.corners = []
        self.edges = []

        row_lengths = [ 3, 4, 5, 4, 3 ]
        start_point = Point(5, 8)
        start = start_point.__copy__()
        tile_centers = []

        for i in range(len(row_lengths)):
            for _ in range(row_lengths[i]):
                tile_centers.append(start_point.__copy__())
                start_point.shift(0, 4)

            start.shift(4, -2) if i < 2 else start.shift(4, 2)
            start_point = start.__copy__()

        corner_points = []
        edge_points = []
        for center in tile_centers:
            for i in range(6): # up to 6 unique Nodes for each: edges and corners
                corner_points.append(Point(center.x + Tile.DIMENSIONS_CORNER[i].x, center.y + Tile.DIMENSIONS_CORNER[i].y))
                edge_points.append(Point(center.x + Tile.DIMENSIONS_EDGES[i].x, center.y + Tile.DIMENSIONS_EDGES[i].y))

        for corner in set(corner_points):
            self.corners.append(Node(corner.x, corner.y))
   
        for edge in set(edge_points):
            self.edges.append(Node(edge.x, edge.y))

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

        start = start_point.__copy__()

        tile_id = 0
        for center in tile_centers:
            tile_corners = []
            for corner in self.corners:
                for i in range(6):
                    if corner.x == center.x + Tile.DIMENSIONS_CORNER[i].x and corner.y == center.y + Tile.DIMENSIONS_CORNER[i].y:
                        tile_corners.append(corner)

            tile_edges = []
            for edge in self.edges:
                for i in range(6):
                    if edge.x == center.x + Tile.DIMENSIONS_EDGES[i].x and edge.y == center.y + Tile.DIMENSIONS_EDGES[i].y:
                        tile_edges.append(edge)
                        edge.icon = Tile.DIRECTIONS[i]
            
            self.tiles.append(Tile(center.__copy__(), self.small_chips.pop(), tile_id, self.small_tile_resources.pop(), tile_corners, tile_edges))
            tile_id += 1

        for tile in self.tiles:
            for corner in tile.corners:
                for other_tile in self.tiles:
                    for other_corner in other_tile.corners:
                        if corner == other_corner:
                            corner.tiles_touching.append(other_tile.id)
                corner.tiles_touching = list(set(corner.tiles_touching))

        for corner in self.corners:
            corner.neighbors = self.calculate_neighbors(corner).copy()

        for edge in self.edges:
            edge.neighbors = self.calculate_neighbors(edge).copy()

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

        distances, dists = calculate_distances(self.corners)

        for distances in distances[:1]:
            for node, other in dists[distances]:
                neighbors.append(other)

        distances, dists = calculate_distances(self.edges)

        for distances in distances[:1]:
            for node, other in dists[distances]:
                neighbors.append(other)

        return neighbors

    def get_corner_from_point(self, point:Point):
        for corner in self.corners:
            if corner.x == point.x and corner.y == point.y:
                return corner
        return None
    
    def get_edge_from_point(self, point:Point):
        for edge in self.edges:
            if edge.x == point.x and edge.y == point.y:
                return edge
        return None

    def __iter__(self):
        for tile in self.tiles:
            yield tile

    

	# public boolean checkOtherSettlements(KeyPoint kp) {
	# 	CustomPoint cp = null;
	# 	for (Point p : Tile.CORNER_CHECKS) {
	# 		cp = new CustomPoint(kp.getPoint().x + p.x, kp.getPoint().y + p.y);
	# 		if (inBounds(cp)) {
	# 			for (KeyPoint corner : this.corners) {
	# 				if (isSameLocation(cp, corner.getPoint()) && corner.isOccupied()) {
	# 					return false;
	# 				}
	# 			}
	# 		}
	# 	}
	# 	return true;
	# }