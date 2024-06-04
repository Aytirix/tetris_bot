from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *
from algo import *

os.system('clear')

try:
	website = website("http://c2r7p2:3000", "BOT")
	while True:
		if website.login():
			break
			# print("Erreur lors de la connexion")
			# website.logout()
			# exit()
		print("En attente de connexion")
		time.sleep(1)

	ia = IA(website)
	end_game = threading.Thread(target=ia.get_piece_movement)
	end_game.daemon = True
	end_game.start()

	if not website.start_game():
		print("Erreur lors du lancement de la partie")
		website.logout()
		exit()


	thread = threading.Thread(target=website.get_map)
	thread.daemon = True
	thread.start()

	execute_move = threading.Thread(target=website.exexute_move)
	execute_move.daemon = True
	execute_move.start()

	end_game = threading.Thread(target=website.check_end_game)
	end_game.daemon = True
	end_game.start()


	while end_game.is_alive():
		print("\n"*4)

		ia.map = website.map
		ia.execute_best_move()
		time.sleep(1)
except Exception as e:
	print(f"Erreur inattendu :{e}")
finally:
	website.logout()