import argparse
from tools import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--saso", help="Run the bot in SASO mode", action="store_true")
    parser.add_argument("-l", "--local", help="Run the bot in local mode", action="store_true")
    args = parser.parse_args()
    if args.saso:
        import WebSocketListener
    elif args.local:
        import test_algo
    else:
        parser.print_help()