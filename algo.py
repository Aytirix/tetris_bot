from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *


class IA():
	def __init__(self, map):
		self.map = map
		self.map_temp = []
		self.execute_move = []

	def get_piece_movement(self):
		"""
		Rechercher la pièce qui peut bouger
		return: La pièce qui peut bouger,
				None si aucune pièce ne peut bouger
		"""
		for i in range(20):
			for j in range(10):
				if self.map[i][j] == 1:
					if self.map[i+1][j] == 0:
						return (i, j)
		return None