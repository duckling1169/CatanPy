from game.thief import Thief
from game.board import Board
from game.display_grid import DisplayGrid
from game.enums import GrowthCardEnum, ResourceEnum, BuildingEnum
from game.point import Point
from game.developmentcard import DevelopmentCard
import random

class SettleGame:
		
	def __init__(self, border:int=2, auto:bool=True, scale:int=1, empty_icon:str=' ', random_ports:bool=True):
		from players.player import Player
		from players.aiplayer import AIPlayer
		
		self.tilemap = Board(border, random_ports)
		self.grid = DisplayGrid(DisplayGrid.MIN_ACROSS + border*2, DisplayGrid.MIN_DOWN + border*2, scale, empty_icon)

		for tile in self.tilemap.tiles:
			if tile.resource == ResourceEnum.DESERT:
				self.thief = Thief(tile.id)

		self.deck = []
		for _ in range(14):
			self.deck.append(DevelopmentCard(GrowthCardEnum.KNIGHT))
		for _ in range(5):
			self.deck.append(DevelopmentCard(GrowthCardEnum.VICTORY_POINT))
		for _ in range(2):
			self.deck.append(DevelopmentCard(GrowthCardEnum.MONOPOLY))
		for _ in range(2):
			self.deck.append(DevelopmentCard(GrowthCardEnum.ROAD_BUILDER))
		for _ in range(2):
			self.deck.append(DevelopmentCard(GrowthCardEnum.YEAR_OF_PLENTY))

		random.shuffle(self.deck)

		self.players = []
		if auto:
			self.players = [ Player('Adam', 0), AIPlayer('CatanBot', 1) ]
			return
		
		resp = ''
		id = 0
		while resp != 'q' or len(self.players) > 3:
			resp = input('Enter next player name or \'ai\' (q to stop): ')
			if resp != 'q':
				self.players.append(AIPlayer(resp, id)) if resp == 'ai' else self.players.append(Player(resp, id))
			id += 1

	def setup_game(self) -> None:
		for player in self.players:
			self.update_grid()
			print(self)
			player.place_buildings(self, [BuildingEnum.OUTPOST, BuildingEnum.ROAD])

		self.gb.players.reverse()

		for player in self.players:
			self.update_grid()
			print(self)
			player.place_buildings(self, [BuildingEnum.OUTPOST, BuildingEnum.ROAD], True)

		self.gb.players.reverse()

		return None

	def update_grid(self) -> None:
		for tile in self.tilemap:
			
			# self.grid.update_grid(tile.resource.value, tile.center.__copy__())
			# lower_center = tile.center.__copy__()
			# lower_center.shift(0, 1)
			# if tile.has_robber:
			# 	self.grid.update_grid('R', lower_center.__copy__())
			# else:
			# 	self.grid.update_grid(tile.dice_roll, lower_center.__copy__())
			# upper_center = tile.center.__copy__()
			# upper_center.shift(0, -1)
			# self.grid.update_grid(f'({str(tile.resource_points)})', upper_center.__copy__())

			self.grid.update_grid(str(tile.resource.value), tile.center.__copy__())

			# for node in tile.nodes:
			# 	self.grid.update_grid(node.icon, Point(node.x, node.y))
			
		for node in self.tilemap.nodes:
			self.grid.update_grid(node.icon, Point(node.x, node.y))

		for side in self.tilemap.sides:
			for port in side.ports:
				self.grid.update_grid(port.icon, port.center)
			for point, icon in side.connections:
				self.grid.update_grid(icon, point)
		
		return None

	def __str__(self):
		return self.grid.__str__()
