from game.thief import Thief
from game.board import Board
from game.display_grid import DisplayGrid
from game.enums import GrowthCardEnum, ResourceEnum, BuildingEnum
from game.point import Point
from game.purchaseables import GrowthCard
import random

class SettleGame:
		
	def __init__(self, border:int=2, auto:bool=True, scale:int=1, empty_icon:str=' ', random_ports:bool=True):
		# Import here to avoid circular imports
		from players.player import Player
		from players.aiplayer import AIPlayer
		
		self.tilemap = Board(border, random_ports)
		self.grid = DisplayGrid(DisplayGrid.MIN_ACROSS + border*2, DisplayGrid.MIN_DOWN + border*2, scale, empty_icon)

		# Initialize thief on desert tile
		self.thief = None
		for tile in self.tilemap.tiles:
			if tile.resource == ResourceEnum.DESERT:
				self.thief = Thief(tile.id)
				break

		# Initialize development card deck
		self.deck = []
		for _ in range(14):
			self.deck.append(GrowthCard(GrowthCardEnum.KNIGHT))
		for _ in range(5):
			self.deck.append(GrowthCard(GrowthCardEnum.VICTORY_POINT))
		for _ in range(2):
			self.deck.append(GrowthCard(GrowthCardEnum.MONOPOLY))
		for _ in range(2):
			self.deck.append(GrowthCard(GrowthCardEnum.ROAD_BUILDER))
		for _ in range(2):
			self.deck.append(GrowthCard(GrowthCardEnum.YEAR_OF_PLENTY))

		random.shuffle(self.deck)

		# Initialize players
		self.players = []
		if auto:
			self.players = [ Player('Adam', 0), AIPlayer('CatanBot', 1) ]
			return
		
		# Manual player setup
		resp = ''
		id = 0
		while resp != 'q' and len(self.players) < 4:  # Max 4 players
			resp = input('Enter next player name or \'ai\' (q to stop): ')
			if resp != 'q':
				if resp == 'ai':
					self.players.append(AIPlayer(f'Bot{id}', id))
				else:
					self.players.append(Player(resp, id))
				id += 1

	def setup_game(self) -> None:
		"""Setup phase - each player places 2 settlements and 2 roads"""
		print("=== SETUP PHASE ===")
		
		# First round - each player places 1 settlement + 1 road
		for player in self.players:
			self.update_grid()
			print(self)
			print(f"{player.name}'s turn to place initial settlement and road")
			player.place_buildings(self, [BuildingEnum.OUTPOST, BuildingEnum.ROAD])

		# Second round - reverse order, players get resources from second settlement
		self.players.reverse()
		for player in self.players:
			self.update_grid()
			print(self)
			print(f"{player.name}'s turn to place second settlement and road")
			player.place_buildings(self, [BuildingEnum.OUTPOST, BuildingEnum.ROAD], True)

		# Restore original order
		self.players.reverse()
		print("Setup phase complete!")

	def draw_development_card(self):
		"""Draw a development card from the deck"""
		if self.deck:
			return self.deck.pop()
		return None

	def update_grid(self) -> None:
		"""Update the display grid with current game state"""
		# Clear grid first by updating with empty tiles
		for tile in self.tilemap:
			self.grid.update_grid(str(tile.resource.value), tile.center.__copy__())

		# Update nodes (buildings)
		for node in self.tilemap.nodes:
			self.grid.update_grid(node.icon, Point(node.x, node.y))

		# Update sides (ports and connections)
		for side in self.tilemap.sides:
			for port in side.ports:
				self.grid.update_grid(port.icon, port.center)
			for point, icon in side.connections:
				self.grid.update_grid(icon, point)
		
		return None

	def __str__(self):
		return self.grid.__str__()
