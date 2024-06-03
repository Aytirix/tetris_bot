from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver

class website():
	def __init__(self):
		self.driver = Driver()
		self.driver.start_driver()
	
	def login(self):
		if not self.driver.change_page("http://c2r6p9:3000/"):
			return False
		if not self.driver.send_keys(By.CSS_SELECTOR, '[name="username"]', "BOT"):
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

	def lougout(self):
		self.driver.stop_driver()
		return True