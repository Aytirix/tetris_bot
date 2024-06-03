from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *

website = website()
if not website.login():
	print("Erreur lors de la connexion")
	website.lougout()
	exit()
if not website.start_game():
	print("Erreur lors du lancement de la partie")
	website.lougout()
	exit()
time.sleep(2)
website.move(Keys.ARROW_UP)
time.sleep(2)
website.move(Keys.ARROW_DOWN)
time.sleep(2)
website.move(Keys.ARROW_LEFT)
time.sleep(2)
website.move(Keys.ARROW_RIGHT)
time.sleep(5000)
website.lougout()