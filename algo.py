from tools import *
from tetris_env import TetrisEnv

class algo_tetris:
	def __init__(self, height=20, width=10, use_last_move=False, poids={"complete_lines": 200, "filled_cells_score": 0.3, "holes": 50, "bumpiness": 4, "max_height": 3, "move_error": -10000}):
		self.height = height
		self.width = width
		self.use_last_move = use_last_move
		self.poids = poids

	def get_q_value(self, state, action):
		env = TetrisEnv(self.height, self.width, False, self.use_last_move, self.poids)
		env.board, env.current_piece = copy.deepcopy(state)
		next_state, reward, done = env.step(action)
		q_value = reward
		return q_value

	def choose_action(self, state, env):
		_, piece = state
		valid_actions = self.get_valid_actions(piece, env)
		if not valid_actions:
			return (0, 0, 0)
		action_q_values = [(a, self.get_q_value(state, a)) for a in valid_actions]
		# for action, q_value in action_q_values:
		# 	print(f"Action {action} - Q-Value: {q_value}")
		max_q_value = max(action_q_values, key=lambda x: x[1])[1]
		best_actions = [action for action, q_value in action_q_values if q_value == max_q_value]
		best_action = random.choice(best_actions)
		# print(f"Best Action: {best_action}")
		# print()
		return best_action

	def get_valid_actions(self, piece, env):
		valid_actions = []
		num_rotations = len(env.piece_shapes[piece])
		for rot in range(num_rotations):
			for col in range(-env.width + 1, env.width):
				if self.is_valid_action(env, piece, rot, col):
					valid_actions.append((rot, col, 0))
					if self.use_last_move:
						last_move = self.is_late_move_valid(env, piece, rot, col)
						if last_move != 0:
							valid_actions.append((rot, col, last_move))
		return valid_actions

	def is_valid_action(self, env, piece, rotation_idx, col_offset):
		rotation = env.piece_shapes[piece][rotation_idx]
		max_x = env.height - 1
		max_y = env.width - 1

		for y, x in rotation:
			start_x = x 
			new_x = x + col_offset
			new_y = y

			if new_x < 0 or new_x > max_y or new_y > max_x:
				return False  # le bloc cible est hors limites

			# Déterminer la direction du balayage pour vérifier les cellules intermédiaires
			step = 1 if new_x > start_x else -1

			# Vérifier chaque cellule entre la position de départ et la position cible
			for intermediate_x in range(start_x, new_x + step, step):
				if env.board[new_y][intermediate_x] != 0 and env.board[new_y][intermediate_x] != piece:
					return False
		return True

	def is_late_move_valid(self, env, piece, rotation_idx, col_offset):
		rotation = env.piece_shapes[piece][rotation_idx]
		max_x = env.width - 1
		max_y = env.height - 1
		board_copy = copy.deepcopy(env.board)

		# Déterminez la position la plus basse pour la pièce
		lowest_positions = []
		for y, x in rotation:
			for potential_y in range(max_y + 1):
				adjusted_y = y + potential_y
				adjusted_x = x + col_offset
				if adjusted_y > max_y or adjusted_x < 0 or adjusted_x > max_x or board_copy[adjusted_y][adjusted_x] != 0:
					lowest_positions.append(potential_y - 1)
					break
			else:
				lowest_positions.append(max_y - y)
		lowest_position = min(lowest_positions)

		# Tester les mouvements latéraux pour combler un trou
		valid_lateral_move = 0
		for dx in [-1, 1]:
			move_possible = True
			temp_board = copy.deepcopy(board_copy)

			# Vérifiez d'abord s'il n'y a pas de collision
			for y, x in rotation:
				new_x = x + col_offset + dx
				new_y = y + lowest_position
				if not (0 <= new_x <= max_x and 0 <= new_y <= max_y and temp_board[new_y][new_x] == 0):
					move_possible = False
					break
			
			if move_possible:
				for y, x in rotation:
					temp_board[y + lowest_position][x + col_offset + dx] = 9
				# Vérifier si le mouvement remplit un trou
				for y, x in rotation:
					new_x = x + col_offset + dx
					new_y = y + lowest_position
					if new_y <= max_y and new_y >= 0 and temp_board[new_y][new_x] == 9:
						# Il y a un trou sous le bloc après le mouvement
						if temp_board[new_y - 1][new_x] != 0 and temp_board[new_y - 1][new_x] != 9:
							return dx
		return valid_lateral_move
