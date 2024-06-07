from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver

class website():
	def __init__(self, url, username):
		self.url = url
		self.username = username
		self.driver = Driver()
		self.driver.start_driver()
		self.end_game = False

	def get_websocket(self):
		"""
		Récupère le websocket
		"""
		for _ in range(20):
			network = self.driver.driver.get_log('performance')
			for log in network:
				if "Sec-WebSocket-Key" in str(log):
					return re.findall(r'"Sec-WebSocket-Key":"(.*?)"', log["message"])[0]
			time.sleep(1)

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
		if not self.driver.send_keys(By.CSS_SELECTOR, 'body', move, clear=False):
			return False
		time.sleep(1)

	def logout(self):
		"""
		Se déconnecte du site
		"""
		self.driver.stop_driver()
		return True

	def update_map(self, map_string):
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
		if not map_string:
			print("Erreur lors de la récupération de la map")
			self.map = []
			return False
		elems = re.findall(r'"color":"(.*?)"', map_string)
		if not elems:
			print("Erreur lors de la récupération des cases")
			self.map = []
			return False
		num_cols = 10
		tab = [elems[i:i + num_cols] for i in range(0, len(elems), num_cols)]
		color_map = {
			"transparent": 0,
			"purple": 1,
			"orange": 2,
			"green": 3,
			"yellow": 4,
			"cyan": 5,
			"blue": 6,
			"red": 7
		}
		for i in range(len(tab)):
			for j in range(len(tab[i])):
				tab[i][j] = color_map.get(tab[i][j], 0)
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