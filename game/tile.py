from game.node import Node
from game.point import Point
from game.enums import ResourceEnum

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
    
