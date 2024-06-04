from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver

class website():
	def __init__(self, url, username):
		self.url = url
		self.username = username
		self.driver = Driver()
		self.driver.start_driver()
		self.map_temp = []
		self.map = []
		self.lock = False

	def login(self):
		if not self.driver.change_page(self.url):
			return False
		if not self.driver.send_keys(By.CSS_SELECTOR, '[name="username"]', self.username):
			return False
		if not self.driver.click_element(By.CSS_SELECTOR, 'button'):
			return False
		return True

	def start_game(self):
		if not self.driver.send_keys(By.CSS_SELECTOR, '[name="roomName"]', "BOT_GAME"):
			return False
		for i in range(2):
			if not self.driver.click_element(By.CSS_SELECTOR, 'button'):
				return False
			time.sleep(1)
		return True

	def move(self, move):
		if not self.driver.send_keys(By.CSS_SELECTOR, 'body', move):
			return False

	def logout(self):
		self.driver.stop_driver()
		return True
	
	def get_map(self):
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
					print("Erreur lors de la récupération de la couleur (detectée: " + style + ")" )
					self.map = []
					return False
				tab[col].append(color)
		if not self.lock:
			self.map = tab
		return True