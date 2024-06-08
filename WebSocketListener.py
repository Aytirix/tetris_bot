from tools import *
from algo import algo_tetris
from tetris_env import TetrisEnv

poids = {
	"complete_lines": float(os.getenv("BONUS_COMPLETE_LINE")),
	"filled_cells_score": float(os.getenv("BONUS_FILLED_CELLS")),
	"holes": float(os.getenv("MALUS_HOLE")),
	"bumpiness": float(os.getenv("MALUS_BUMPINESS")),
	"max_height": float(os.getenv("MALUS_HEIGHT_MAX")),
	"move_error": float(os.getenv("MALUS_MOVE_ERROR"))
}
last_move = (os.getenv("C") == "True")

class WebSocketListener:
	def __init__(self, url, username, room):
		self.uri = url
		self.username = username
		self.room = room
		self.ws = None

	def connect_ws(self):
		try:
			self.ws = create_connection(self.uri)
			if not self.ws.connected:
				self.ws = None
				return False
			return True
		except Exception as e:
			print("Impossible de se connecter au serveur", e)
			return False

class bot(WebSocketListener, algo_tetris):
	def __init__(self, url, username, room):
		WebSocketListener.__init__(self, url, username, room)
		global poids
		global last_move
		algo_tetris.__init__(self, use_last_move=last_move, poids=poids)
		self.lock = False
		self.actual_piece = None
		self.env = TetrisEnv(check_move=last_move,poids=poids)
		self.map = [[0 for _ in range(10)] for _ in range(20)]
		self.end_game = False
		self.stats = {
			"score": 0,
			"linesCleared": 0,
			"tetrisScored": 0,
			"linesCleared": 0,
			"level": 0
		}

	def start_connection(self):
		try:
			if not self.connect_ws():
				return False
			time.sleep(1)
			self.ws.send("40")
			time.sleep(1)
			self.ws.send('420["validate_username",{"username":"%s"}]' % self.username)
			time.sleep(1)
			return True
		except Exception as e:
			print("Error", e)
			return False

	def listen_forever(self):
		while not self.end_game:
			try:
				message = self.ws.recv()
				if '42["grid_update",{"grid":[[{"filled":' in message:
					message = message[2:]
					self.update_map(message)
				elif len(message) > 0 and message[0] == "2":
					self.ws.send("3")
				elif '42["log_update",{"logs":["Game over for player' in message:
					self.end_game = True
					print("Game over")
					exit(0)
				elif 'tetrisScored' in message:
					os.system("clear")
					message = message[2:]
					message = json.loads(message)[1]
					self.stats = message
			except Exception as e:
				print("Connection closed", e)
				break

	def get_piece_movement(self):
		try:
			for i in range(5, 8):
				if self.map[1][i] != 0 and self.map[1][i]:
					self.env.current_piece = int(self.map[1][i])
					return True
			return False
		except Exception as e:
			print("Error", e)
			return False

	def update_map(self, map):
		"""
		Récupère la map sous forme d'un double tableau
		Le premier tableau représente les lignes
		Le deuxième tableau représente les colonnes
		Chaque case est représentée par un nombre
		0 = case vide
		1 = case violet
		2 = case bleu
		3 = case orange
		4 = case jaune
		5 = case cyan
		6 = case rouge
		7 = case vert
		"""
		try:
			map = json.loads(map)[1]["grid"]
			color_map = {
				"transparent": 0,
				"purple": 1,
				"blue": 2,
				"orange": 3,
				"yellow": 4,
				"cyan": 5,
				"red": 6,
				"green": 7
			}
			for line in map:
				for i in range(len(line)):
					line[i] = color_map.get(line[i]["color"], 0)
			self.map = np.array(map)
			os.system("clear")
			for key, value in self.stats.items():
				print(key, value)
			print_map(self.map)
			return True
		except Exception as e:
			print("Error", e)
			return False

	def play(self):
		try:
			while not self.end_game:
				if self.get_piece_movement():
					rot, col, last = self.choose_action((self.env.board, self.env.current_piece), self.env)
					self.env.step((rot, col, last))
					i = 0
					j = 0
					for i in range(1, rot+1):
						self.move("rotate")
					if col < 0:
						for j in range(-1, col-1, -1):
							self.move("left")
					else:
						for j in range(1, col+1):
							self.move("right")
					self.move("drop")
					time.sleep(0.1)
					self.env.current_piece = None
			return True
		except Exception as e:
			print("Error", e)
			return False

	def start_game(self, game_mode):
		try:
			if game_mode == "classic":
				self.ws.send(
					'42["join_room",{"username":"%s","room":"%s"}]'
					% (self.username, self.room)
				)
			elif game_mode == "journey":
				self.ws.send(
					'42["join_room_journey",{"username":"%s","room":"%s"}]'
					% (self.username, self.room)
				)
			else:
				print("Invalid game mode")
				return
			time.sleep(1)
			self.ws.send(
				'42["redirect_game",{"room":"%s","username":"%s"}]'
				% (self.room, self.username)
			)
			time.sleep(1)
			if game_mode == "classic":
				sleep = input("Press Enter to start the game")
			self.ws.send(
				'42["game_started",{"username":"%s","room":"%s"}]'
				% (self.username, self.room)
			)
			return True
		except Exception as e:
			print("Error", e)
			return False

	def move(self, direction):
		try:
			if direction not in ["left", "right", "rotate", "fall", "stopFall", "drop"]:
				print("Invalid direction")
				return
			if direction in ["fall", "stopFall", "rotate", "drop"]:
				self.ws.send('42["%s"]' % direction)
			else:
				self.ws.send('42["move",{"direction":"%s"}]' % direction)
			return True
		except Exception as e:
			print("Error", e)
			return False

	def leave_game(self):
		try:
			print("Leaving game")
			self.ws.send('42["leave_game",{"username":"%s","room":"%s"}]' % (self.username, self.room))
			self.ws.close()
			self.end_game = True
			return True
		except Exception as e:
			print("Error", e)
			return False

os.system("clear")

time.sleep(1)
username = os.getenv("USERNAME")
room = os.getenv("ROOM")
listener = bot("ws://c2r7p2:3000/socket.io/?EIO=4&transport=websocket", username, room)
if not listener.start_connection():
	exit(1)
listener.start_game("journey")

piece = threading.Thread(target=listener.play)
piece.daemon = True
piece.start()

thread = threading.Thread(target=listener.listen_forever)
thread.daemon = True
thread.start()

def on_key_press(event):
	if event.Key == "Escape":
		listener.leave_game()
		listener.end_game = True
		listener.ws.close()
		exit(0)

def move_mouse():
	while True:
		pyautogui.moveRel(1, 0)
		time.sleep(60)

thread_mouse = threading.Thread(target=move_mouse)
thread_mouse.daemon = True
thread_mouse.start()

hookman = pyxhook.HookManager()
hookman.KeyDown = on_key_press
hookman.HookKeyboard()
hookman.start()
print("Press Escape to leave the game")

while True:
	if not thread.is_alive():
		break
	if not piece.is_alive():
		break
	time.sleep(1)