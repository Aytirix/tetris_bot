import cProfile
import datetime
import os
import pstats
import time
import mysql.connector
import numpy as np
import random
import copy
import threading
import zlib
import base64
import signal

global totalepisode, stop_requested

class TetrisEnv:
	def __init__(self, height=20, width=10):
		self.height = height
		self.width = width
		self.board = np.zeros((height, width))
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
		self.current_piece = None

	def reset(self):
		self.board = np.zeros((self.height, self.width))
		self.current_piece = random.choice(list(self.piece_shapes.keys()))
		return self.get_state()

	def get_state(self):
		return copy.deepcopy(self.board), self.current_piece

	def step(self, action):
		rotation_idx, col = action
		if rotation_idx >= len(self.piece_shapes[self.current_piece]):
			raise ValueError("Index de rotation invalide")
		rotation = self.piece_shapes[self.current_piece][rotation_idx]
		board_copy = self.board.copy()  # Utilisation de la copie superficielle
		
		max_x = len(board_copy) - 1
		max_y = len(board_copy[0]) - 1

		for _, y in rotation:
			if y + col < 0 or y + col > max_y:
				return self.get_state(), -10, True

		lowest_position = max_x
		for x, y in rotation:
			for drop_row in range(max_x + 1):
				test_x = drop_row + x
				if test_x > max_x or board_copy[test_x][y + col] != 0:
					lowest_position = min(lowest_position, drop_row - 1)
					break

		if lowest_position >= 0:
			for x, y in rotation:
				if lowest_position + x > max_x or lowest_position + x < 0 or y + col < 0 or y + col > max_y or board_copy[lowest_position + x][y + col] != 0:
					return self.get_state(), -10, True
				board_copy[lowest_position + x][y + col] = self.current_piece
			self.board = board_copy
			reward = self.calculate_reward()
			done = self.check_game_over()
			self.current_piece = random.choice(list(self.piece_shapes.keys()))
			return self.get_state(), reward, done
		else:
			return self.get_state(), -10, True

	def calculate_reward(self):
		complete_lines = self.get_complete_lines(self.board)
		holes = self.get_holes(self.board)
		bumpiness = self.get_bumpiness(self.board)
		max_height = self.get_max_height(self.board)
		return complete_lines * 200 - holes * 5 - bumpiness * 3 - max_height * 1

	def get_complete_lines(self, board):
		complete_lines = 0
		for row in board:
			if all(cell != 0 for cell in row):
				complete_lines += 1
				# Supprimer la ligne complète et ajouter une nouvelle ligne en haut
				board = np.delete(board, np.where(np.all(board != 0, axis=1)), axis=0)
				new_line = np.zeros((1, board.shape[1]))
				board = np.vstack([new_line, board])
		self.board = board
		return complete_lines

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

	def get_max_height(self, board):
		return max(self.get_column_height(board, col) for col in range(len(board[0])))

	def check_game_over(self):
		return any(self.board[0])
