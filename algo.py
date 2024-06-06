import copy
from tools import *
from website import *
from IA.ia import QLearningAgent

"""
	0 = case vide
	1 = case violette T
	2 = case orange J
	3 = case verte Z
	4 = case jaune O
	5 = case cyan I
	6 = case bleue L
	7 = case rouge S
"""

class IA():
	def __init__(self, website):
		self.website = website
		self.actual_piece = None
		self.agent = QLearningAgent()
		self.width = 10
		self.height = 20
		self.board = None
		self.piece_shapes = {
			1: [  # T shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 6)],  # Original
				[(1, 5), (2, 5), (3, 5), (2, 6)],   # 270 degrees
				[(1, 5), (1, 6), (1, 7), (2, 6)],  # 180 degrees
				[(1, 6), (2, 6), (3, 6), (2, 5)]  # 90 degrees
			],
			2: [  # L shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 7)],  # Original
				[(1, 5), (2, 5), (3, 5), (3, 6)],  # 90 degrees
				[(1, 5), (1, 6), (1, 7), (2, 5)],  # 180 degrees
				[(1, 5), (1, 6), (2, 6), (3, 6)]   # 270 degrees
			],
			3: [  # J shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 5)],  # Original
				[(1, 5), (2, 5), (3, 5), (1, 6)],   # 270 degrees
				[(1, 5), (1, 6), (1, 7), (2, 7)],  # 180 degrees
				[(1, 6), (2, 6), (3, 6), (3, 5)]  # 90 degrees
			],
			4: [  # O shape (only one rotation)
				[(1, 5), (1, 6), (2, 5), (2, 6)]   # Original
			],
			5: [  # I shape rotations
				[(1, 5), (2, 5), (3, 5), (4, 5)],  # Original
				[(1, 5), (1, 6), (1, 7), (1, 8)]   # 90 degrees
			],
			6: [  # S shape rotations
				[(2, 5), (2, 6), (1, 6), (1, 7)],  # Original
				[(1, 5), (2, 5), (2, 6), (3, 6)]   # 90 degrees
			],
			7: [  # Z shape rotations
				[(1, 5), (1, 6), (2, 6), (2, 7)],  # Original
				[(1, 6), (2, 6), (2, 5), (3, 5)]   # 90 degrees
			]
		}

	def get_piece_movement(self):
		while threading.current_thread().is_alive():
			if not self.website.map:
				continue
			for i in range(5, 8):
				if self.website.map[1][i] != 0 and self.website.map[1][i] != self.actual_piece:
					self.actual_piece = self.website.map[1][i]
					break
			
	def execute_best_move(self):
		if not self.actual_piece:
			return None
		self.board = np.array(self.website.map)
		best_move = self.agent.choose_action((self.board, self.actual_piece), self)
		if not best_move:
			return None
		rotation_idx, target_col, last_move = best_move

		# Rotate the piece to the best rotation
		for _ in range(rotation_idx):
			self.website.move(Keys.UP)
		
		# Move the piece to the target column
		if target_col > 0:
			for _ in range(target_col):
				self.website.move(Keys.RIGHT)
		else:
			for _ in range(abs(target_col)):
				self.website.move(Keys.LEFT)

		# Drop the piece
		self.website.move(Keys.SPACE)
		if last_move > 0:
			for _ in range(last_move):
				self.website.move(Keys.RIGHT)
		else:
			for _ in range(abs(last_move)):
				self.website.move(Keys.LEFT)

		# Reset actual_piece to None to await the next piece
		self.actual_piece = None