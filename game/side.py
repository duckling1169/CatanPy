from game.port import Port
from game.enums import SideEnum, SideDirectionEnum, ResourceEnum, PortDirectionEnum, PortEnum
from game.tile import Tile
from game.point import Point
from game.node import Node

class Side():

    def __init__(self, tiles:[Tile], resources:[ResourceEnum], direction:SideDirectionEnum):
        self.resources = resources
        self.direction = direction
        self.ports = []

        def make_port(resource:ResourceEnum, center:Point, type:PortEnum, direction:PortDirectionEnum, adjacent_tiles:[Tile]):
            port = Port(resource, center, type, direction)

            match port.type:
                case PortEnum.SQUARE: # shift x, shift y
                    one = Point(port.direction.value.x * 2 + port.center.x, port.center.y)
                    two = Point(port.center.x, port.direction.value.y * 2 + port.center.y)
                case PortEnum.TRIANGLE: # shift x, shift x,y
                    one = Point(port.direction.value.x * 2 + port.center.x, port.center.y)
                    two = Point(port.direction.value.x * 2 + port.center.x, port.direction.value.y * 2 + port.center.y)
            
            for tile in adjacent_tiles:
                for node in tile.nodes:
                    if node.port == None and \
                        (node.x == one.x and node.y == one.y) or \
                        (node.x == two.x and node.y == two.y):
                        node.port = port
    
            return port

        self.type = SideEnum.SINGLE_RESOURCE if len(resources) == 1 else SideEnum.DOUBLE_RESOURCE

        if self.type == SideEnum.DOUBLE_RESOURCE:
            adjacent_tiles = [tiles[id] for id in self.direction.value ]
            center = adjacent_tiles[2].center.__copy__()

            match self.direction:
                case SideDirectionEnum.BOTTOM:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_RIGHT
                case SideDirectionEnum.BOTTOM_LEFT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_LEFT
                case SideDirectionEnum.TOP_LEFT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.BOTTOM_LEFT
                case SideDirectionEnum.TOP:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_LEFT
                case SideDirectionEnum.TOP_RIGHT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_RIGHT
                case SideDirectionEnum.BOTTOM_RIGHT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.BOTTOM_RIGHT

            self.ports.append(make_port(self.resources[1], center, type, direction))

            center = adjacent_tiles[1].center.__copy__()

            match self.direction:
                case SideDirectionEnum.BOTTOM:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_LEFT
                case SideDirectionEnum.BOTTOM_LEFT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.BOTTOM_LEFT
                case SideDirectionEnum.TOP_LEFT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_LEFT
                case SideDirectionEnum.TOP:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_RIGHT
                case SideDirectionEnum.TOP_RIGHT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.TOP_RIGHT
                case SideDirectionEnum.BOTTOM_RIGHT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_RIGHT

            self.ports.append(make_port(self.resources[1], center, type, direction))
   
        elif self.type == SideEnum.SINGLE_RESOURCE:
            adjacent_tiles = [tile for tile in tiles if tile.id in self.direction.value]
            center = adjacent_tiles[1].center.__copy__()

            match self.direction:
                case SideDirectionEnum.BOTTOM:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_RIGHT
                case SideDirectionEnum.BOTTOM_LEFT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.BOTTOM_LEFT
                case SideDirectionEnum.TOP_LEFT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.TOP_LEFT
                case SideDirectionEnum.TOP:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_LEFT
                case SideDirectionEnum.TOP_RIGHT:
                    type = PortEnum.SQUARE
                    direction = PortDirectionEnum.TOP_RIGHT
                case SideDirectionEnum.BOTTOM_RIGHT:
                    type = PortEnum.TRIANGLE
                    direction = PortDirectionEnum.BOTTOM_RIGHT
            
            self.ports.append(make_port(self.resources[1], center, type, direction))

    def __str__(self):
        s = f'Side: {self.direction} | {self.type}\n'
        for port in self.ports:
            s += '\t' + port.__str__()
        return s + '\n'
    

# 3:1 
# Brick + 3:1
# Wood
# Wheat + 3:1
# Ore
# Sheep + 3:1

# solo 
# side 0: bottom right, square
# side 1: bottom left, square
# side 2: top left, triangle
# side 3: top left, square
# side 4: top right, square
# side 5: bottom right, triangle

# duo 
# side 0: port 0: bottom left, square 
# side 1: port 0: bottom left, triangle 
# side 2: port 0: top left, square 
# side 3: port 0: top right, square 
# side 4: port 0: top right, triange 
# side 5: port 0: bottom right, square 
