from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *
from algo import *
from WebSocketListener import *

os.system('clear')

url = "c2r7p2:3000"

try:
	web = website(f"http://{url}", "BOT")
	while True:
		if web.login():
			break
		print("En attente de connexion")
		time.sleep(1)

	token = web.get_websocket()
	socket = WebSocketListener(f"ws://{url}/socket.io/?EIO=4&transport=websocket", web.driver, token)
	socket.start()

	ia = IA(web, socket)
	end_game = threading.Thread(target=ia.get_piece_movement)
	end_game.daemon = True
	end_game.start()

	if not web.start_game():
		print("Erreur lors du lancement de la partie")
		web.logout()
		exit()

	end_game = threading.Thread(target=web.check_end_game)
	end_game.daemon = True
	end_game.start()

	while end_game.is_alive():
		ia.execute_best_move()
except Exception as e:
	print(f"Erreur inattendu :{e}")
finally:
	web.logout()