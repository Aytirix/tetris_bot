from tools import *
from SeleniumV2 import SeleniumV2
from Driver import Driver
from website import *
from algo import *

os.system('clear')

# map = [[0 for _ in range(10)] for _ in range(20)]
# map[18][5] = 1
# map[18][6] = 1
# map[18][7] = 1
# map[19][6] = 1
# print("\n"*4)
# for line in map:
# 	print(str(line).replace(", ", " ").replace("[", "").replace("]", ""))
# ia = IA(map)
# move = ia.get_piece_movement()
# print(move)
# time.sleep(10000)
# exit()

website = website("http://c2r7p2:3000", "BOT")
if not website.login():
	print("Erreur lors de la connexion")
	website.logout()
	exit()
if not website.start_game():
	print("Erreur lors du lancement de la partie")
	website.logout()
	exit()
time.sleep(1)

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
	for line in website.map.copy():
		print(str(line).replace(", ", " ").replace("[", "").replace("]", ""))
	time.sleep(0.5)
website.logout()