from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver

class website():
	def __init__(self, url, username):
		self.url = url
		self.username = username
		self.driver = Driver()
		self.driver.start_driver()
		self.map = []
		self.execute_move = []
		self.lock = False
		self.end_game = False

	def login(self):
		"""
		Se connecte au site
		"""
		if not self.driver.change_page(self.url):
			return False
		if not self.driver.send_keys(By.CSS_SELECTOR, '[name="username"]', self.username, timeout=5):
			return False
		if not self.driver.click_element(By.CSS_SELECTOR, 'button', timeout=5):
			return False
		return True

	def start_game(self):
		"""
		Lance une partie
		"""
		if not self.driver.send_keys(By.CSS_SELECTOR, '[name="roomName"]', "BOT", timeout=15):
			return False
		for i in range(2):
			if not self.driver.click_element(By.CSS_SELECTOR, 'button', timeout=15):
				return False
		return True

	def move(self, move):
		"""
		Execute un mouvement

		exemple:
		website.move(Keys.SPACE)
		website.move(Keys.LEFT)
		website.move(Keys.RIGHT)
		website.move(Keys.UP)
		website.move(Keys.DOWN)
		"""
		if not self.driver.send_keys(By.CSS_SELECTOR, 'body', move):
			return False

	def exexute_move(self):
		"""
		Execute les mouvements en attente

		exemple:
		website.execute_move.append(Keys.SPACE)
		website.execute_move.append(Keys.LEFT)
		website.execute_move.append(Keys.RIGHT)
		website.execute_move.append(Keys.UP)
		website.execute_move.append(Keys.DOWN)
		"""
		while threading.current_thread().is_alive() and not self.end_game:
			for move in self.execute_move.copy():
				self.move(move)
				self.execute_move.remove(move)

	def logout(self):
		"""
		Se déconnecte du site
		"""
		self.driver.stop_driver()
		return True
	
	def get_map(self):
		"""
		Récupère la map sous forme d'un double tableau
		Le premier tableau représente les lignes
		Le deuxième tableau représente les colonnes
		Chaque case est représentée par un nombre
		0 = case vide
		1 = case violette
		2 = case orange
		3 = case verte
		4 = case jaune
		5 = case cyan
		6 = case bleue
		7 = case rouge
		"""
		while threading.current_thread().is_alive() and not self.end_game:
			tab = []
			map = self.driver.presence_of_element(By.CSS_SELECTOR, '[class^="game-grid"]', attribut="outerHTML")
			if not map:
				print("Erreur lors de la récupération de la map")
				self.map = []
				return False
			elems = re.findall(r'style="background-color: (.*?);', map)
			if not elems:
				print("Erreur lors de la récupération des cases")
				self.map = []
				return False
			tab = [[] for _ in range(20)]
			for col in range(0, 20):
				for line in range(0, 20*10, 20):
					color = 0
					if "transparent" in elems[col+line]:
						color = 0
					elif "purple" in elems[col+line]:
						color = 1
					elif "orange" in elems[col+line]:
						color = 2
					elif "green" in elems[col+line]:
						color = 3
					elif "yellow" in elems[col+line]:
						color = 4
					elif "cyan" in elems[col+line]:
						color = 5
					elif "blue" in elems[col+line]:
						color = 6
					elif "red" in elems[col+line]:
						color = 7
					else:
						print("Erreur lors de la récupération de la couleur" )
						self.map = []
						return False 
					tab[col].append(color)
			if not self.lock:
				self.map = tab

	def check_end_game(self):
		"""
		Vérifie si la partie est terminée
		"""
		while threading.current_thread().is_alive():
			if self.driver.presence_of_element(By.XPATH, '//div[text()="GAME OVER"]'):
				self.end_game = True
				score = self.driver.presence_of_element(By.CSS_SELECTOR, '[class="font-4"]', attribut="innerText")
				print(f"Partie terminée avec un score de {score}")
				return True
			time.sleep(1)
		return False