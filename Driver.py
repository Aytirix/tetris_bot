from SeleniumV2 import SeleniumV2
from tools import *

class Driver(SeleniumV2):
	def __init__(self):
		super().__init__()
		SeleniumV2.__init__(self)
		self.driver = None
		self.user_name = os.getenv("USER") or os.getenv("USERNAME")

		self.options = webdriver.ChromeOptions()
		self.options.binary_location = f"/home/{self.user_name}/sgoinfre/chrome-linux64/chrome"
		
		self.options.add_argument("--mute-audio")
		self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

		self.options.add_argument("--start-maximized")
		self.options.add_argument("disable-infobars"); # disabling infobars
		self.options.add_argument("--disable-extensions"); # disabling extensions
		self.options.add_argument("--disable-gpu"); # applicable to windows os only
		self.options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
		self.options.add_argument("--no-sandbox"); # Bypass OS security model
		self.options.add_argument("-disable-accelerated-2d-canvas"); # Disable hardware acceleration
		self.options.add_argument("--disable-blink-features=AutomationControlled") # pour ne pas être détecté par le site

		self.capabilities = DesiredCapabilities.CHROME.copy()
		self.capabilities['acceptSslCerts'] = True  # Accepte tous les certificats SSL.

	def start_driver(self):
		try:
			self.driver = webdriver.Chrome(service=Service(f"/home/{self.user_name}/sgoinfre/chromedriver-linux64/chromedriver"), options=self.options, desired_capabilities=self.capabilities)
		except Exception as e:
			if self.driver is not None:
				self.driver.quit()
			print("Erreur lors du lancement du driver : " + str(e))
			return False
		try:
			self.driver.set_page_load_timeout(180)
		except Exception as e:
			try:
				self.driver.quit()
			except:
				pass
			self.print("Erreur de chargement de la page" + str(e))

	def stop_driver(self):
		if self.driver is not None:
			self.driver.quit()
			self.driver = None