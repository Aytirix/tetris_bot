import time, os, random, threading, re, copy, zlib, base64, datetime, cProfile, signal, pstats, json, mysql.connector, asyncio
import tkinter as tk
from websocket import create_connection
import numpy as np
from dotenv import load_dotenv
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import (
	TimeoutException,
	NoSuchElementException,
	ElementNotVisibleException,
	ElementNotInteractableException,
	StaleElementReferenceException,
	WebDriverException,
	NoSuchWindowException,
	NoSuchFrameException,
	ElementNotSelectableException,
	ElementClickInterceptedException,
)
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