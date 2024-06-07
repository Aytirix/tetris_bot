from tools import *
from IA.tetris_env import TetrisEnv
from IA.ia import QLearningAgent

os.system("clear" if os.name == "posix" else "cls")
env = TetrisEnv(print_map=True)
agent = QLearningAgent(float(os.getenv("ALPHA")), float(os.getenv("GAMMA")), float(os.getenv("EPSILON")), float(os.getenv("EPSILON_DECAY")))
state = env.reset()
env.current_piece = 6
state = (state[0], env.current_piece)
action = agent.choose_action(state, env)
action = (0, -5, 0)
next_state, reward, done = env.step(action)
state = next_state
print_map(state[0])

env.current_piece = 1
state = (state[0], env.current_piece)
action = agent.choose_action(state, env)
action = (0, -2, -1)
next_state, reward, done = env.step(action)
state = next_state
print_map(state[0])