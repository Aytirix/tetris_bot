from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *

os.system('clear')

website = website("http://c2r7p2:3000", "BOT")
if not website.login():
	print("Erreur lors de la connexion")
	website.lougout()
	exit()
if not website.start_game():
	print("Erreur lors du lancement de la partie")
	website.lougout()
	exit()
time.sleep(1)

def getmap(website):
    while threading.current_thread().is_alive():
        if not website.get_map():
            print("Erreur lors de la récupération de la map")
            website.logout()
            exit()

thread = threading.Thread(target=getmap, args=[website])
thread.start()

while True:
	print("\n"*4)
	for line in website.map.copy():
		print(str(line).replace(", ", " ").replace("[", "").replace("]", ""))
	time.sleep(0.1)
time.sleep(5000)
website.logout()