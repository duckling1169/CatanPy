from enum import Enum

class BuildingEnum(Enum):
    EMPTY = 'X'
    ROAD = 'R'
    SETTLEMENT = 'S'
    CITY = 'C'

class NodeEnum(Enum):
    VERTEX = [ BuildingEnum.EMPTY, BuildingEnum.SETTLEMENT, BuildingEnum.CITY ]
    EDGE = [ BuildingEnum.EMPTY, BuildingEnum.ROAD ]

class ResourceEnum(Enum):
    EMPTY = 'Empty'
    WHEAT = 'Wheat'
    WOOD = 'Wood'
    SHEEP = 'Sheep'
    ORE = 'Ore'
    BRICK = 'Brick'
    DESERT = 'Desert'

class DevelopmentCardEnum(Enum):
    KNIGHT = "Move the robber and take one resource from an opponent."
    ROADBUILDER = "Build 2 roads."
    VICTORYPOINT = "Grants you one victory point."
    MONOPOLY = "Get all other players' resources of one type."
    YEAROFPLENTY = "Take 2 of any resource from the bank."
    