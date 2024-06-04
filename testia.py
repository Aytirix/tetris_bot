import mysql.connector
import numpy as np
import random
import copy
import threading

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
		board_copy = copy.deepcopy(self.board)
		
		max_y = len(board_copy[0]) - 1
		max_x = len(board_copy) - 1

		lowest_position = None
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

		if lowest_position is not None:
			for (x, y) in rotation:
				board_copy[x + lowest_position - 1][y + col] = self.current_piece
		else:
			return self.get_state(), -10, True  # Reward -10 for invalid move

		self.board = board_copy
		reward = self.calculate_reward()
		done = self.check_game_over()
		self.current_piece = random.choice(list(self.piece_shapes.keys()))
		return self.get_state(), reward, done

	def calculate_reward(self):
		complete_lines = self.get_complete_lines(self.board)
		holes = self.get_holes(self.board)
		bumpiness = self.get_bumpiness(self.board)
		max_height = self.get_max_height(self.board)
		return complete_lines * 100 - holes * 10 - bumpiness * 5 - max_height * 2

	def get_max_height(self, board):
		return max(self.get_column_height(board, col) for col in range(len(board[0])))

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

	def check_game_over(self):
		return any(self.board[0])

class QLearningAgent:
	def __init__(self, db_config, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995):
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.epsilon_decay = epsilon_decay
		self.db_config = db_config

	def db_connect(self):
		return mysql.connector.connect(**self.db_config)

	def __del__(self):
		self.conn.close()

	def get_q_value(self, state, action):
		state_str = self.state_to_str(state)
		action_str = self.action_to_str(action)
		self.conn = self.db_connect()
		self.cursor = self.conn.cursor()
		try:
			self.cursor.execute("SELECT q_value FROM q_values WHERE state=%s AND action=%s", (state_str, action_str))
			result = self.cursor.fetchone()
			self.conn.close()
			if result:
				return result[0]
			else:
				return 0.0
		except:
			self.conn.close()
			return 0.0

	def update_q_value(self, state, action, reward, next_state):
		state_str = self.state_to_str(state)
		action_str = self.action_to_str(action)
		best_next_action = max(self.get_valid_actions(next_state[1]), key=lambda a: self.get_q_value(next_state, a))
		target = reward + self.gamma * self.get_q_value(next_state, best_next_action)
		current_q_value = self.get_q_value(state, action)
		new_q_value = current_q_value + self.alpha * (target - current_q_value)
		self.conn = self.db_connect()
		self.cursor = self.conn.cursor()
		try:
			self.cursor.execute(
				"INSERT INTO q_values (state, action, q_value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE q_value=%s",
				(state_str, action_str, new_q_value, new_q_value)
			)
			self.conn.commit()
		except:
			pass
		self.conn.close()

	def choose_action(self, state):
		valid_actions = self.get_valid_actions(state[1])
		if random.random() < self.epsilon:
			return random.choice(valid_actions)
		else:
			return max(valid_actions, key=lambda a: self.get_q_value(state, a))

	def decay_epsilon(self):
		self.epsilon *= self.epsilon_decay

	def state_to_str(self, state):
		board, piece = state
		return f"{piece}-" + ''.join(map(str, board.flatten().astype(int)))

	def action_to_str(self, action):
		rotation_idx, col = action
		return f"{rotation_idx}-{col}"

	def get_valid_actions(self, piece):
		num_rotations = len(env.piece_shapes[piece])
		return [(rot, col) for rot in range(num_rotations) for col in range(10)]
# Configuration de la base de données
db_config = {
	'user': 'tetris_rl',
	'password': 'tetris_rltetris_rl',
	'host': '145.239.62.99',
	'database': 'tetris_rl'
}

def run_session(env, agent, num_episodes):
    for episode in range(num_episodes):
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.update_q_value(state, action, reward, next_state)
            state = next_state
            total_reward += reward

        agent.decay_epsilon()
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

# Nombre de threads
num_threads = 4
num_episodes = 1000

# Créer et démarrer les threads
threads = []

for i in range(num_threads):
    env = TetrisEnv()
    agent = QLearningAgent(db_config=db_config)
    t = threading.Thread(target=run_session, args=(env, agent, num_episodes))
    threads.append(t)
    t.start()

# Attendre que tous les threads se terminent
for t in threads:
    t.join()

print("Apprentissage terminé.")