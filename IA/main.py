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
from tetris_env import TetrisEnv
from database_manager import DatabaseManager
from ia import QLearningAgent
from dotenv import load_dotenv, set_key
load_dotenv()

totalepisode = 0
stop_requested = False  # Indicateur global pour demander l'arrêt
# récupération des variables d'environnement
print_map = (os.getenv("PRINT_MAP") == "True")
use_profiler = (os.getenv("USE_PROFILER") == "True")
infinit_training = (os.getenv("INFINI_TRAINING") == "True")
def run_session(env, agent, num_episodes):
	global totalepisode, stop_requested, print_map
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
			if print_map:
				print_map(state[0])

		agent.decay_epsilon()
		elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
		print(f"Episode {episode + 1}: Total Reward: {total_reward} - Temps: {elapsed_time}s")
	agent.save_q_values()

def handle_stop_signal(signal, frame):
	global stop_requested
	stop_requested = True
	print("Arrêt demandé, enregistrement des valeurs Q...")

signal.signal(signal.SIGINT, handle_stop_signal)

def print_map(map):
	# 0 = emoji case vide
	# 1 = carre emoji violet
	# 2 = carre emoji bleu
	# 3 = carre emoji orange
	# 4 = carre emoji jaune
	# 5 = carre emoji cyan
	# 6 = carre emoji rouge
	# 7 = carre emoji vert
	width = len(map[0])
	height = len(map)
	for y in range(height):
		for x in range(width):
			if map[y][x] == 0:
				print("⬛️", end="")
			elif map[y][x] == 1:
				print("🟪", end="")
			elif map[y][x] == 2:
				print("🟦", end="")
			elif map[y][x] == 3:
				print("🟧", end="")
			elif map[y][x] == 4:
				print("🟨", end="")
			elif map[y][x] == 5:
				print("🟫", end="")
			elif map[y][x] == 6:
				print("🟥", end="")
			elif map[y][x] == 7:
				print("🟩", end="")
		print("")
	print("")

def launch_thread(num_threads, num_episodes):
	global threads
	try:
		for i in range(num_threads):
			print(f"Lancement du thread {i + 1}/{num_threads}")
			env = TetrisEnv()
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

if __name__ == "__main__":
	os.system("clear" if os.name == "posix" else "cls")
	print("Apprentissage en cours...")
	threads = []

	if use_profiler:
		# Démarrer le profilage
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