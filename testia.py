import datetime
import os
import time
import mysql.connector
import numpy as np
import random
import copy
import threading
import zlib
import base64
import signal

totalepisode = 0
stop_requested = False  # Indicateur global pour demander l'arrêt

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

class DatabaseManager:
	def __init__(self, db_config = None):
		self.db_config = {
			'user': 'tetris_rl',
			'password': 'tetris_rltetris_rl',
			'host': '145.239.62.99',
			'database': 'tetris_rl'} if db_config is None else db_config

	def execute_query(self, query, params, retry_attempts=5):
		for attempt in range(retry_attempts):
			try:
				conn = mysql.connector.connect(**self.db_config)
				cursor = conn.cursor()
				cursor.execute(query, params)
				conn.commit()
				return
			except mysql.connector.errors.DatabaseError as e:
				if e.errno == 1205:  # ER_LOCK_WAIT_TIMEOUT
					if attempt < retry_attempts - 1:
						time.sleep(1)  # Attendre avant de réessayer
						continue
					else:
						print(f"Transaction failed after {retry_attempts} attempts due to lock wait timeout.")
						raise
				else:
					raise
			finally:
				if conn.is_connected():
					cursor.close()
					conn.close()

	def fetch_one(self, query, params):
		try:
			conn = mysql.connector.connect(**self.db_config)
			cursor = conn.cursor()
			cursor.execute(query, params)
			result = cursor.fetchone()
			return result
		except Exception as e:
			print(f"Error fetching data: {e}")
			return None
		finally:
			if conn.is_connected():
				cursor.close()
				conn.close()

class QLearningAgent:
	def __init__(self, alpha=0.1, gamma=0.80, epsilon=1.0, epsilon_decay=0.001):
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
			q_value = 0.0
		self.q_values_cache[key] = q_value
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
		for (state_str, action_str), q_value in self.q_values_cache.items():
			self.db_manager.execute_query(
				"INSERT INTO q_values (state, action, q_value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE q_value=%s",
				(state_str, action_str, q_value, q_value))


	def choose_action(self, state, env):
		_, piece = state
		valid_actions = self.get_valid_actions(piece, env)
		if not valid_actions:
			# Retourner une action par défaut si aucune action valide n'est trouvée
			return (0, 0)  # Action par défaut (rotation_idx, col)
		if random.random() < self.epsilon:
			return random.choice(valid_actions)
		else:
			return max(valid_actions, key=lambda a: self.get_q_value(state, a))

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
			for col in range(env.width):
				if self.is_valid_action(env, piece, rot, col):
					valid_actions.append((rot, col))
		return valid_actions

	def is_valid_action(self, env, piece, rotation_idx, col):
		rotation = env.piece_shapes[piece][rotation_idx]
		max_x = env.height - 1
		max_y = env.width - 1

		for x, y in rotation:
			new_x = x
			new_y = y + col
			if new_y < 0 or new_y > max_y or new_x > max_x or env.board[new_x][new_y] != 0:
				return False
		return True

def run_session(env, agent, num_episodes):
	global totalepisode, stop_requested
	for episode in range(num_episodes):
		if stop_requested:
			break
		totalepisode += 1
		state = env.reset()
		done = False
		total_reward = 0
		start_time = datetime.datetime.now()

		while not done:
			action = agent.choose_action(state, env)
			next_state, reward, done = env.step(action)
			agent.update_q_value(state, action, reward, next_state, env)
			state = next_state
			total_reward += reward

		agent.decay_epsilon()
		elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
		print(f"Episode {episode + 1}: Total Reward: {total_reward} - Temps: {elapsed_time}s")
	agent.save_q_values()

def handle_stop_signal(signal, frame):
	global stop_requested
	stop_requested = True
	print("Arrêt demandé, enregistrement des valeurs Q...")

signal.signal(signal.SIGINT, handle_stop_signal)

# Nombre de threads
num_threads = 1
num_episodes = 5000

if __name__ == "__main__":
	os.system("clear" if os.name == "posix" else "cls")
	print("Apprentissage en cours...")
	threads = []
	def launch_thread(num_threads, num_episodes):
		global threads
		try:
			for i in range(num_threads):
				print(f"Lancement du thread {i + 1}/{num_threads}")
				env = TetrisEnv()
				agent = QLearningAgent()
				t = threading.Thread(target=run_session, args=(env, agent, num_episodes))
				threads.append(t)
				t.start()
				time.sleep(0.100)
		except Exception as e:
			print(f"Erreur lors du lancement des threads: {e}")

	launch_thread(num_threads, num_episodes)
	total_relance = 0
	try:
		while threads:
			# print(f"Threads restants: {len(threads)}/{num_threads}/ Total relancé: {total_relance}")
			# moyenne = totals_reward / totalepisode
			# print(f"Moyenne des récompenses: {moyenne}")
			# episode = totalepisode / num_threads
			# print(f"Episode moyen: {episode}/{num_episodes}\n")
			time.sleep(60)

			threads = [t for t in threads if t.is_alive()]
			if len(threads) < num_threads and not stop_requested:
				total_relance += num_threads - len(threads)
				launch_thread(num_threads - len(threads), num_episodes)
	except Exception as e:
		print(f"Erreur lors de la vérification des threads: {e}")

	print("Apprentissage terminé.")
