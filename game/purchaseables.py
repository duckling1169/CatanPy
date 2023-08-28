from game.enums import ResourceEnum

class Purchaseables():

	def __init__(self, name:str, cost:[ResourceEnum]):
		self.name = name
		self.cost = cost
