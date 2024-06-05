from tools import *
from database_manager import DatabaseManager
from tetris_env import TetrisEnv

class QLearningAgent:
	def __init__(self, alpha=0.1, gamma=0.80, epsilon=1.0, epsilon_decay=0.999):
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.epsilon_decay = epsilon_decay
		self.db_manager = DatabaseManager()
		self.q_values_cache = {}

	def get_q_value(self, state, action):
		state_str = self.state_to_str(state)
		action_str = self.action_to_str(action)
		key = (state_str, action_str)
		if key in self.q_values_cache:
			return self.q_values_cache[key]
		result = self.db_manager.fetch_one("SELECT q_value FROM q_values WHERE state=%s AND action=%s", (state_str, action_str))
		if result:
			q_value = result[0]
		else:
			env = TetrisEnv()
			env.board, env.current_piece = copy.deepcopy(state)
			next_state, reward, done = env.step(action)
			q_value = reward
		return q_value

	def update_q_value(self, state, action, reward, next_state, env):
		state_str = self.state_to_str(state)
		action_str = self.action_to_str(action)
		next_piece = next_state[1]
		valid_actions = self.get_valid_actions(next_piece, env)
		
		if valid_actions:
			best_next_action = max(valid_actions, key=lambda a: self.get_q_value(next_state, a))
			target = reward + self.gamma * self.get_q_value(next_state, best_next_action)
		else:
			target = reward
		current_q_value = self.get_q_value(state, action)
		new_q_value = current_q_value + self.alpha * (target - current_q_value)
		self.q_values_cache[(state_str, action_str)] = new_q_value

	def save_q_values(self):
		batch_size = 50
		items = list(self.q_values_cache.items())
		for i in range(0, len(items), batch_size):
			batch = items[i:i + batch_size]
			query = "INSERT INTO q_values (state, action, q_value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE q_value=VALUES(q_value)"
			params = [(state_str, action_str, q_value) for (state_str, action_str), q_value in batch]
			self.db_manager.execute_many(query, params)

	def choose_action(self, state, env):
		_, piece = state
		valid_actions = self.get_valid_actions(piece, env)
		if not valid_actions:
			return (0, 0)
		if random.random() < self.epsilon:
			return random.choice(valid_actions)
		else:
			i = 0
			action_q_values = [(a, self.get_q_value(state, a)) for a in valid_actions]
			for action, q_value in action_q_values:
				print(f"Action {i}: {action} - Q-Value: {q_value}")
			max_q_value = max(action_q_values, key=lambda x: x[1])[1]
			best_actions = [action for action, q_value in action_q_values if q_value == max_q_value]
			best_action = random.choice(best_actions)
			print(f"Best Action: {best_action}")
			return best_action

	def decay_epsilon(self):
		self.epsilon *= self.epsilon_decay

	def state_to_str(self, state):
		board, piece = state
		board_flattened = board.flatten().astype(np.uint8).tobytes()
		compressed = zlib.compress(board_flattened)
		encoded = base64.b64encode(compressed).decode('utf-8')
		return f"{piece}-{encoded}"

	def str_to_state(self, state_str):
		piece, encoded_board = state_str.split('-')
		compressed = base64.b64decode(encoded_board)
		decompressed = zlib.decompress(compressed)
		board_flattened = np.frombuffer(decompressed, dtype=np.uint8)
		board = board_flattened.reshape((self.env_height, self.env_width))
		return board, int(piece)

	def action_to_str(self, action):
		rotation_idx, col = action
		return f"{rotation_idx}-{col}"

	def str_to_action(self, action_str):
		rotation_idx, col = map(int, action_str.split('-'))
		return rotation_idx, col

	def get_valid_actions(self, piece, env):
		valid_actions = []
		num_rotations = len(env.piece_shapes[piece])
		for rot in range(num_rotations):
			for col in range(-env.width + 1, env.width):
				if self.is_valid_action(env, piece, rot, col):
					valid_actions.append((rot, col))
		return valid_actions

	def is_valid_action(self, env, piece, rotation_idx, col_offset):
		rotation = env.piece_shapes[piece][rotation_idx]
		max_x = env.height - 1
		max_y = env.width - 1

		for x, y in rotation:
			new_x = x
			new_y = y + col_offset
			if new_y < 0 or new_y > max_y or new_x > max_x or env.board[new_x][new_y] != 0:
				return False
			
		# Vérifier si un mouvement de rotation est possible juste avant de fixer la pièce
		if not self.can_rotate_in_place(env, piece, rotation_idx, col_offset):
			return False

		return True

	def can_rotate_in_place(self, env, piece, rotation_idx, col_offset):
		# Tester les différentes rotations possibles à partir de la position actuelle
		possible_rotations = len(env.piece_shapes[piece])
		for next_rotation in range(possible_rotations):
			if next_rotation == rotation_idx:
				continue  # ignorer la rotation actuelle
			next_rotation_positions = env.piece_shapes[piece][next_rotation]
			if all(self.is_cell_free(env, x, y + col_offset) for x, y in next_rotation_positions):
				return True
		return False

	def is_cell_free(self, env, x, y):
		max_x = env.height - 1
		max_y = env.width - 1
		return 0 <= y <= max_y and 0 <= x <= max_x and env.board[x][y] == 0
