import argparse
from tools import *
from WebSocketListener import start_saso

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--classic", help="Run the bot in SASO Journey mode", action="store_true")
	parser.add_argument("-j", "--journey", help="Run the bot in SASO Multiplayer mode", action="store_true")
	parser.add_argument("--join", help="Run the bot in SASO Journey mode (join room exist)", nargs='?', default=None)
	parser.add_argument("-l", "--local", help="Run the bot in local mode", action="store_true")
	args = parser.parse_args()
	if args.classic and args.journey:
		parser.print_help()
	elif args.classic or args.journey or args.join:
		if args.journey:
			saso = start_saso("journey")
		elif args.classic:
			saso = start_saso("classic")
		elif args.join:
			saso = start_saso("classic", args.join)
		else:
			parser.print_help()
	elif args.local:
		import test_algo
	else:
		parser.print_help()