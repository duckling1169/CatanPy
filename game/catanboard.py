from game.tile import TileMap
from game.display_grid import DisplayGrid
from game.enums import DevelopmentCardEnum
from game.node import *
from game.developmentcard import DevelopmentCard
import random

class CatanBoard:
	
	sides = [] # Side()?
	players = [] # Player()!
	
	def __init__(self, length, width, scale=1, empty_icon='.'):
		self.tilemap = TileMap()
		self.grid = DisplayGrid(length, width, scale, empty_icon)

		self.deck = []
		for _ in range(14):
			self.deck.append(DevelopmentCard(DevelopmentCardEnum.KNIGHT))
		for _ in range(5):
			self.deck.append(DevelopmentCard(DevelopmentCardEnum.VICTORYPOINT))
		for _ in range(2):
			self.deck.append(DevelopmentCard(DevelopmentCardEnum.MONOPOLY))
		for _ in range(2):
			self.deck.append(DevelopmentCard(DevelopmentCardEnum.ROADBUILDER))
		for _ in range(2):
			self.deck.append(DevelopmentCard(DevelopmentCardEnum.YEAROFPLENTY))

		random.shuffle(self.deck)

	def update_grid(self):
		for tile in self.tilemap:

			self.grid.update_grid(tile.resource.value, tile.center.__copy__())
			lower_center = tile.center.__copy__()
			lower_center.shift(1, 0)
			self.grid.update_grid(tile.dice_roll, lower_center.__copy__())

			for corner in tile.corners:
				if not corner.is_occupied():
					self.grid.update_grid(corner.icon, Point(corner.x, corner.y))
				else:
					self.grid.update_grid(corner.icon, Point(corner.x, corner.y)) # y+1 ?

			for edge in tile.edges:
				if not edge.is_occupied():
					self.grid.update_grid(edge.icon, Point(edge.x, edge.y))
				else:
					self.grid.update_grid(edge.icon, Point(edge.x, edge.y)) # y+1 ?

	def __str__(self):
		return self.grid.__str__()

