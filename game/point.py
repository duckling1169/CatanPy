import math

class Point:

    def __init__(self, x_init, y_init):
        self.x = x_init
        self.y = y_init

    def shift(self, x, y) -> None:
        self.x += x
        self.y += y

    @staticmethod
    def dist(p1_x, p1_y, p2_x, p2_y) -> float:
        return round(math.dist([p1_x, p1_y], [p2_x, p2_y]), 2)

    def __copy__(self):
        return Point(self.x, self.y)
    
    def __eq__(self, obj):
        return isinstance(obj, Point) and obj.x == self.x and obj.y == self.y
    
    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        from game.display_grid import DisplayGrid
        return f'Point({DisplayGrid.int_to_xscale(self.x)}, {str(self.y)})'
