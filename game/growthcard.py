from game.purchaseables import Purchaseables
from game.enums import GrowthCardEnum, ResourceEnum

class GrowthCard(Purchaseables):
        
    def __init__(self, type:GrowthCardEnum):
        self.type = type
        self.cost = [ ResourceEnum.WHEAT, ResourceEnum.SHEEP, ResourceEnum.ORE ]
        super().__init__(self.type.name.title().replace('_', ' '), self.cost)

    def __str__(self):
        return f'{self.name}: {self.type.value}'
    