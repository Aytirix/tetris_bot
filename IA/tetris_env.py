from tools import *

class TetrisEnv:
	def __init__(self, height=20, width=10, complete_lines=200, filled_cells_score=0.3, holes=40, bumpiness=4, max_height=3, move_error=-10000, print_map=False):
		self.statistique ={
			"complete_lines": 0,
			"tetris": 0,
		}
		self.poids = {
			"complete_lines": complete_lines,
			"filled_cells_score": filled_cells_score,
			"holes": holes,
			"bumpiness": bumpiness,
			"max_height": max_height,
			"move_error": move_error
		}
		self.print_map = print_map
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
		self.current_piece = self.random_piece()

	def random_piece(self):
		available_pieces = list(self.piece_shapes.keys())
		if self.current_piece is not None:
			available_pieces.remove(self.current_piece)
		self.current_piece = random.choice(available_pieces)

	def reset(self):
		self.board = np.zeros((self.height, self.width))
		self.random_piece()
		return self.get_state()

	def get_state(self):
		return copy.deepcopy(self.board), self.current_piece

	def step(self, action):
		rotation_idx, col, last_move = action
		if rotation_idx >= len(self.piece_shapes[self.current_piece]):
			raise ValueError("Index de rotation invalide")
		rotation = self.piece_shapes[self.current_piece][rotation_idx]
		board_copy = self.board.copy()
		
		max_x = len(board_copy) - 1
		max_y = len(board_copy[0]) - 1

		for _, y in rotation:
			if y + col < 0 or y + col > max_y:
				return self.get_state(), self.poids["move_error"], True

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
					return self.get_state(), self.poids["move_error"], True

			# Appliquer le dernier mouvement latéral si possible
			if last_move != 0:
				valid_last_move = True
				for x, y in rotation:
					new_y = y + col + last_move
					if new_y < 0 or new_y > max_y or board_copy[lowest_position + x][new_y] != 0:
						valid_last_move = False
						break
				if valid_last_move:
					col += last_move

			# Placer la pièce
			for x, y in rotation:
				board_copy[lowest_position + x][y + col] = self.current_piece
			self.board = board_copy
			reward = self.calculate_reward()
			done = self.check_game_over()
			self.random_piece()
			return self.get_state(), reward, done
		else:
			return self.get_state(), self.poids["move_error"], True

	def calculate_reward(self):
		complete_lines = self.get_complete_lines(self.board)
		filled_cells_score = self.get_filled_cells_score(self.board)
		holes = self.get_holes(self.board)
		bumpiness = self.get_bumpiness(self.board)
		max_height = self.get_max_height(self.board)
		return complete_lines * self.poids["complete_lines"] \
				+ filled_cells_score * self.poids["filled_cells_score"] \
				- holes * self.poids["holes"] \
				- bumpiness * self.poids["bumpiness"] \
				- max_height * self.poids["max_height"]

	def get_filled_cells_score(self, board):
		score = 0
		for row in range(len(board)):
			for cell in board[row]:
				if cell != 0:
					poids = 1 + (len(board) - row) / (len(board))
					score += (len(board) - row) * poids
		return score

	def get_complete_lines(self, board):
		complete_lines = 0
		new_board = board.copy()
		complete_lines_idx = []
		for i, row in enumerate(board):
			if all(cell != 0 for cell in row):
				complete_lines += 1
				self.statistique["complete_lines"] += 1
				complete_lines_idx.append(i)
				new_board = np.delete(new_board, i, axis=0)
				new_line = np.zeros((1, new_board.shape[1]))
				new_board = np.vstack([new_line, new_board])
		if complete_lines_idx and self.print_map:
			print_map(board, complete_lines_idx)
		self.board = new_board
		self.statistique["complete_lines"] += complete_lines
		if complete_lines == 4:
			self.statistique["tetris"] += 1
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
		return any(self.board[0]) or any(self.board[1])
