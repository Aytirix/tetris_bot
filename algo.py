import copy
from tools import *
# from SeleniumV2 import SeleniumV2
# from Driver import Driver
from website import *

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
				if self.website.map[1][i] != 0:
					self.actual_piece = self.website.map[1][i]

	def get_best_move(self):
		best_score = float('-inf')
		best_move = None
		for rotation_idx, rotation in enumerate(self.piece_shapes[self.actual_piece]):
			for col in range(len(self.website.map[0]) - max(y for x, y in rotation)):
				simulated_board = self.simulate_board(rotation, col)
				if simulated_board is None:
					continue
				score = self.evaluate_board(simulated_board)
				if score > best_score:
					best_score = score
					best_move = (rotation_idx, col)
		return best_move

	def simulate_board(self, rotation, col):
		board_copy = copy.deepcopy(self.website.map)
		max_y = len(board_copy[0]) - 1
		max_x = len(board_copy) - 1

		lowest_position = None

		# Drop the piece to the lowest possible position
		for drop_row in range(len(board_copy)):
			can_place = True
			for (x, y) in rotation:
				if x + drop_row > max_x or y + col > max_y:
					can_place = False
					break
				if board_copy[x + drop_row][y + col] != 0:
					can_place = False
					break
			if not can_place:
				break
			lowest_position = drop_row

		# Place the piece on the board_copy at the lowest valid position
		if lowest_position is not None:
			for (x, y) in rotation:
				board_copy[x + lowest_position - 1][y + col] = self.actual_piece
			return board_copy
		else:
			return None

	def evaluate_board(self, board):
		complete_lines = self.get_complete_lines(board)
		holes = self.get_holes(board)
		bumpiness = self.get_bumpiness(board)
		height_penalty = self.get_height_penalty(board)
		return complete_lines * 10 - holes * 5 - bumpiness * 2 - height_penalty * 3

	def get_complete_lines(self, board):
		return sum(1 for row in board if all(cell != 0 for cell in row))

	def get_holes(self, board):
		holes = 0
		for col in range(len(board[0])):
			block_found = False
			for row in range(len(board)):
				if board[row][col] != 0:
					block_found = True
				elif block_found:
					holes += 1
		return holes

	def get_bumpiness(self, board):
		heights = [self.get_column_height(board, col) for col in range(len(board[0]))]
		bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights) - 1))
		return bumpiness

	def get_column_height(self, board, col):
		for row in range(len(board)):
			if board[row][col] != 0:
				return len(board) - row
		return 0

	def get_height_penalty(self, board):
		heights = [self.get_column_height(board, col) for col in range(len(board[0]))]
		return sum(heights) / len(heights)  # Average height of columns

	def execute_best_move(self):
		if not self.actual_piece:
			return None
		best_move = self.get_best_move()
		if not best_move:
			return None
		rotation_idx, target_col = best_move
		current_col = 5  # Assuming the piece starts at column 5

		# Rotate the piece to the best rotation
		for _ in range(rotation_idx):
			self.website.move(Keys.UP)
		
		# Move the piece to the target column
		while current_col > target_col:
			self.website.move(Keys.LEFT)
			current_col -= 1
		
		while current_col < target_col:
			self.website.move(Keys.RIGHT)
			current_col += 1
		
		# Drop the piece
		self.website.move(Keys.SPACE)
		
		# Reset actual_piece to None to await the next piece
		self.actual_piece = None