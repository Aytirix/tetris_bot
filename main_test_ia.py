from IA.tools import *
from IA.tetris_env import TetrisEnv
from IA.ia import QLearningAgent

stop_requested = False
totalepisode = 0
debug_print_map = (os.getenv("PRINT_MAP") == "True")
use_profiler = (os.getenv("USE_PROFILER") == "True")
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
	global totalepisode, stop_requested, debug_print_map
	line = 0
	tetris = 0
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
		tetris += env.statistique["tetris"]
		print("\n\n\n")
		print_map(state[0])
		print(f"Episode {totalepisode} - Reward: {total_reward} - Complete lines: {env.statistique['complete_lines']} - Tetris: {env.statistique['tetris']} - Total lines: {line} - Total tetris: {tetris}")
	print(f"Total Episode: {num_episodes} - Total lines: {line} - Total tetris: {tetris} soit en moyenne {line / num_episodes} lignes et {tetris / num_episodes} tetris par partie.")

def launch_thread(num_threads, num_episodes):
	global threads
	try:
		for i in range(num_threads):
			print(f"Lancement du thread {i + 1}/{num_threads}")
			env = TetrisEnv(tetris_height, tetris_width, complete_lines, filled_cells_score, holes, bumpiness, max_height, malus_move_error, debug_print_map)
			agent = QLearningAgent()
			t = threading.Thread(target=run_session, args=(env, agent, num_episodes))
			threads.append(t)
			t.start()
			time.sleep(0.100)
	except Exception as e:
		print(f"Erreur lors du lancement des threads: {e}")

# Nombre de threads
num_threads = int(os.getenv("QQT_THREADS"))
num_episodes = int(os.getenv("QQT_EPISODES"))

os.system("clear" if os.name == "posix" else "cls")
print("Apprentissage en cours...")
threads = []

if use_profiler:
	profiler = cProfile.Profile()
	profiler.enable()

launch_thread(num_threads, num_episodes)

total_relance = 0
try:
	while threads:
		threads = [t for t in threads if t.is_alive()]
		if len(threads) < num_threads and not stop_requested and infinit_training:
			total_relance += num_threads - len(threads)
			launch_thread(num_threads - len(threads), num_episodes)
except Exception as e:
	print(f"Erreur lors de la vérification des threads: {e}")

if use_profiler:
	profiler.disable()
	stats = pstats.Stats(profiler)
	stats.strip_dirs()
	stats.sort_stats(pstats.SortKey.TIME)
	stats.print_stats(10)

print("Apprentissage terminé.")