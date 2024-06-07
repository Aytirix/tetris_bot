from tools import *
from IA.tetris_env import TetrisEnv
from IA.database_manager import DatabaseManager
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
	for episode in range(num_episodes):
		if stop_requested:
			break
		totalepisode += 1
		state = env.reset()
		done = False
		total_reward = 0
		start_time = datetime.datetime.now()

		while not done and not stop_requested:
			action = agent.choose_action(state, env)
			next_state, reward, done = env.step(action)
			agent.update_q_value(state, action, reward, next_state, env)
			state = next_state
			total_reward += reward
			if debug_print_map:
				print_map(state[0])
			if len(agent.q_values_cache) >= 300:
				agent.save_q_values()

		print("\n\n\n")
		print_map(state[0])
		print("Total lines: ", env.statistique["complete_lines"])
		print("Total tetris: ", env.statistique["tetris"])
		agent.decay_epsilon()
		elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
		print(f"Episode {episode + 1}: Total Reward: {total_reward} - Temps: {elapsed_time}s")
	agent.save_q_values()

def launch_thread(num_threads, num_episodes):
	global threads
	try:
		for i in range(num_threads):
			print(f"Lancement du thread {i + 1}/{num_threads}")
			env = TetrisEnv(tetris_height, tetris_width, complete_lines, filled_cells_score, holes, bumpiness, max_height, malus_move_error, debug_print_map)
			agent = QLearningAgent(float(os.getenv("ALPHA")), float(os.getenv("GAMMA")), float(os.getenv("EPSILON")), float(os.getenv("EPSILON_DECAY")))
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