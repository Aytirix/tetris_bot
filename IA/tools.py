import cProfile
import datetime
import os
import pstats
import time
import mysql.connector
import numpy as np
import random
import copy
import threading
import zlib
import base64
import signal
from dotenv import load_dotenv, set_key
load_dotenv()

def print_map(map, linecompleteindex = []):	
	width = len(map[0])
	height = len(map)
	for y in range(height):
		for x in range(width):
			if map[y][x] == 0:
				print("⬛️", end="")
			elif map[y][x] == 1:
				print("🟪", end="")
			elif map[y][x] == 2:
				print("🟦", end="")
			elif map[y][x] == 3:
				print("🟧", end="")
			elif map[y][x] == 4:
				print("🟨", end="")
			elif map[y][x] == 5:
				print("🟫", end="")
			elif map[y][x] == 6:
				print("🟥", end="")
			elif map[y][x] == 7:
				print("🟩", end="")
			elif map[y][x] == 8: # For debugging purposes
				print("🔴", end="")
		if linecompleteindex is not None and y in linecompleteindex:
			print("⬅️", end="")
		print("")
	print("")