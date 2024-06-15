from colorama import Fore, Style
from tools import *
from tetris_env import TetrisEnv
from algo import algo_tetris

tetris_height = int(os.getenv("TETRIS_HEIGHT"))
tetris_width = int(os.getenv("TETRIS_WIDTH"))

# Paramètres pour le bot Tetris
initial_population_size = 10
generations = 10
mutation_rate = 0.1
tournament_size = 5

# Poids pour le bot Tetris
WEIGHT_RANGES = {
	'complete_lines': (0, 300),
	'filled_cells_score': (0, 300),
	'holes': (0, 300),
	'bumpiness': (0, 300),
	'max_height': (0, 300)
}

# Fonction pour générer un chromosome aléatoire
def generate_chromosome():
	return {
		key: random.uniform(*range_)
		for key, range_ in WEIGHT_RANGES.items()
	}

# Fonction pour générer une population initiale
def generate_initial_population(size):
	return [generate_chromosome() for _ in range(size)]

# Fonction pour évaluer la fitness d'un chromosome
def evaluate_fitness(chromosome):
	cpy = chromosome.copy()
	cpy['move_error'] = -10000
	env = TetrisEnv(tetris_height, tetris_width, False, False, cpy)
	agent = algo_tetris(tetris_height, tetris_width, False, cpy)
	state = env.reset()
	done = False
	total_reward = 0
	while not done:
		action = agent.choose_action(state, env)
		next_state, reward, done = env.step(action)
		state = next_state
		total_reward += reward
	stat = env.statistique['complete_lines'] + env.statistique['tetris'] * 4
	return stat

# Fonction pour la sélection par tournoi
def tournament_selection(population, scores, k):
	selected = random.sample(list(zip(population, scores)), k)  # Supprimez les parenthèses après 'scores'
	selected.sort(key=lambda x: x[1], reverse=True)
	return selected[0][0]

# Fonction pour le crossover
def crossover(parent1, parent2):
	child = {}
	for key in parent1.keys():
		child[key] = random.choice([parent1[key], parent2[key]])
	return child

# Fonction pour la mutation
def mutate(chromosome, rate):
	for key in chromosome.keys():
		if key == 'move_error':
			continue
		if random.random() < rate:
			chromosome[key] = random.uniform(*WEIGHT_RANGES[key])
	return chromosome

def evaluate_population_subset(population_subset, results, index):
    for i, chromosome in enumerate(population_subset):
        results[index + i] = evaluate_fitness(chromosome)

def genetic_algorithm():
    population = generate_initial_population(initial_population_size)
    threads = []
    num_threads = 4  # Choisissez ce nombre en fonction de votre CPU
    results = [None] * initial_population_size  # Prépare un tableau pour stocker les scores

    for generation in range(generations):
        chunk_size = len(population) // num_threads
        for i in range(num_threads):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i < num_threads - 1 else len(population)
            thread = threading.Thread(target=evaluate_population_subset,
                                      args=(population[start_index:end_index], results, start_index))
            threads.append(thread)
            thread.start()

        # Attendre que tous les threads terminent
        for thread in threads:
            thread.join()

        scores = results[:]
        new_population = []

        for _ in range(initial_population_size // 2):
            parent1 = tournament_selection(population, scores, tournament_size)
            parent2 = tournament_selection(population, scores, tournament_size)
            
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent1, parent2)
            
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            new_population.append(child1)
            new_population.append(child2)

        population = new_population

        best_score = max(scores)
        best_chromosome = population[scores.index(best_score)]
        
        print(f'{Fore.YELLOW}Génération {generation + 1}/{generations} - Meilleur score: {best_score}{Style.RESET_ALL}')
        for key, value in best_chromosome.items():
            print(f'{Fore.GREEN}{key}{Style.RESET_ALL}: {value}')

    return best_chromosome

if __name__ == '__main__':
	os.system("clear" if os.name == "posix" else "cls")
	best_weights = genetic_algorithm()
	for key, value in best_weights.items():
		print(f'{key}: {value}')
