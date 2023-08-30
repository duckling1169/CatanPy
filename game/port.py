from game.point import Point
from game.enums import PortEnum, PortDirectionEnum, ResourceEnum

class Port():

    def __init__(self, resource:ResourceEnum, center:Point, 
                 type:PortEnum, direction:PortDirectionEnum):
        self.resource = resource
        self.center = center
        self.type = type
        self.direction = direction

        self.update_port_location()
        self.icon = 'P'

    def update_port_location(self):
        port_x = self.type.value.x * self.direction.value.x
        port_y = self.type.value.y * self.direction.value.y

        self.center.shift(port_x, port_y)

    def __str__(self):
        return f'{self.resource.value} port at {self.center}\n{self.type} | {self.direction}'
    
    def __copy__(self):
        return Port(self.resource, self.center.__copy__(), self.type, self.direction)