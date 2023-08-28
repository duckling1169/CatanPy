from game.purchaseables import Purchaseables
from game.enums import DevelopmentCardEnum, ResourceEnum

class DevelopmentCard(Purchaseables):
        
    def __init__(self, card_type:DevelopmentCardEnum):
        self.card_type = card_type
        self.cost = [ ResourceEnum.WHEAT, ResourceEnum.SHEEP, ResourceEnum.ORE ]
        super().__init__('Development Card', self.cost)

    def play(self):
        match(self.card_type):
            case DevelopmentCardEnum.KNIGHT: 
                True
            case DevelopmentCardEnum.YEAROFPLENTY: 
                True
            case DevelopmentCardEnum.ROADBUILDER: 
                True
            case DevelopmentCardEnum.MONOPOLY: 
                True
            case DevelopmentCardEnum.VICTORYPOINT: 
                True
        return True
