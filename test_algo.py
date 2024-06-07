from tools import *
from tetris_env import TetrisEnv
from algo import algo_tetris

max_line = 0
max_tetris = 0
line = 0
tetris = 0
total_game = 0
stop_requested = False
totalepisode = 0
debug_print_map = (os.getenv("PRINT_MAP") == "True")
infinit_training = (os.getenv("INFINI_TRAINING") == "True")

malus_move_error = float(os.getenv("MALUS_MOVE_ERROR"))
complete_lines = float(os.getenv("BONUS_COMPLETE_LINE"))
filled_cells_score = float(os.getenv("BONUS_FILLED_CELLS"))
holes = float(os.getenv("MALUS_HOLE"))
bumpiness = float(os.getenv("MALUS_BUMPINESS"))
max_height = float(os.getenv("MALUS_HEIGHT_MAX"))
tetris_height = int(os.getenv("TETRIS_HEIGHT"))
tetris_width = int(os.getenv("TETRIS_WIDTH"))

def handle_stop_signal(signal, frame):
	global stop_requested
	stop_requested = True
	print("Arrêt demandé, enregistrement des valeurs Q...")
signal.signal(signal.SIGINT, handle_stop_signal)

def run_session(env, agent, num_episodes):
	global total_game, totalepisode, stop_requested, debug_print_map, line, tetris, max_line, max_tetris
	for episode in range(num_episodes):
		if stop_requested:
			break
		totalepisode += 1
		state = env.reset()
		done = False
		total_reward = 0

		while not done and not stop_requested:
			action = agent.choose_action(state, env)
			next_state, reward, done = env.step(action)
			state = next_state
			total_reward += reward
			if debug_print_map:
				print_map(state[0])

		line += env.statistique["complete_lines"]
		if env.statistique["complete_lines"] > max_line:
			max_line = env.statistique["complete_lines"]
		if env.statistique["tetris"] > max_tetris:
			max_tetris = env.statistique["tetris"]
		tetris += env.statistique["tetris"]
		total_game += 1
		# print("\n\n\n")
		# print_map(state[0])

def launch_thread(num_threads, num_episodes):
	global threads
	try:
		for i in range(num_threads):
			print(f"Lancement du thread {i + 1}/{num_threads}")
			env = TetrisEnv(tetris_height, tetris_width, complete_lines, filled_cells_score, holes, bumpiness, max_height, malus_move_error, debug_print_map)
			agent = algo_tetris()
			t = threading.Thread(target=run_session, args=(env, agent, num_episodes))
			threads.append(t)
			t.start()
			time.sleep(0.100)
	except Exception as e:
		print(f"Erreur lors du lancement des threads: {e}")

num_threads = int(os.getenv("QQT_THREADS"))
num_episodes = int(os.getenv("QQT_EPISODES"))

os.system("clear" if os.name == "posix" else "cls")
print("Test en cours...")
threads = []

launch_thread(num_threads, num_episodes)

total_relance = 0
try:
	while threads:
		threads = [t for t in threads if t.is_alive()]
		if len(threads) < num_threads and not stop_requested and infinit_training:
			total_relance += num_threads - len(threads)
			launch_thread(num_threads - len(threads), num_episodes)
		if not print_map:
			os.system("clear" if os.name == "posix" else "cls")
			print(f"Nombre de threads restants: {len(threads)}")
		time.sleep(1)
except Exception as e:
	print(f"Erreur lors de la vérification des threads: {e}")

print(f"Total de parties jouées: {total_game} - Total de parties relancées: {total_relance}")
print("Résumé des parties:")
print(f"Total Episode: {totalepisode} - Total lines: {line} - Total tetris: {tetris} soit en moyenne {line / totalepisode} lignes et {tetris / totalepisode} tetris par partie.")
print(f"meilleur score: {max_line} lignes et {max_tetris} tetris")

print("Apprentissage terminé.")