import time, os, random, threading, re, copy, zlib, base64, datetime, cProfile, signal, pstats
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