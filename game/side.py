from game.port import Port
from game.enums import SideEnum, SideDirectionEnum, ResourceEnum, PortDirectionEnum, PortEnum
from game.tile import Tile
from game.point import Point
class Side():

    CONNECTION_ICON = '·'

    def __init__(self, tiles:[Tile], resources:[ResourceEnum], direction:SideDirectionEnum):
        self.resources = resources
        self.direction = direction
        self.ports = []
        self.connections = []

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

            # Assign icons for pretty port printing
            match port.type:
                case PortEnum.SQUARE:
                    self.connections.append((Point(port.center.x + port.direction.value.x, port.center.y), Side.CONNECTION_ICON))
                    self.connections.append((Point(port.center.x, port.center.y + port.direction.value.y), Side.CONNECTION_ICON))
                case PortEnum.TRIANGLE:
                    self.connections.append((Point(port.center.x + port.direction.value.x, port.center.y), Side.CONNECTION_ICON))
                    self.connections.append((Point(port.center.x + port.direction.value.x, port.center.y + port.direction.value.y), Side.CONNECTION_ICON))

    
            return port

        adjacent_tiles = [tiles[direction] for direction in self.direction.value]
        self.type = SideEnum.SINGLE_RESOURCE if len(resources) == 1 else SideEnum.DOUBLE_RESOURCE

        if self.type == SideEnum.DOUBLE_RESOURCE:
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
            
            self.ports.append(make_port(self.resources[1], center, type, direction, adjacent_tiles))
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

            self.ports.append(make_port(self.resources[0], center, type, direction, adjacent_tiles))

        elif self.type == SideEnum.SINGLE_RESOURCE:
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
            
            self.ports.append(make_port(self.resources[0], center, type, direction, adjacent_tiles))
   
    def __str__(self):
        s = f'Side: {self.direction} | {self.type}\n'
        for port in self.ports:
            s += '\t' + port.__str__()
        return s + '\n'
