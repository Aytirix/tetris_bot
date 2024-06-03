from tools import *

"""
Cette classe est une surcouche de Selenium personnalisée pour ce programme
"""
class SeleniumV2():
	def __init__(self):
		pass

	def handle_exception(self, e: Exception, msg: str = None) -> None:
		"""
		Gère les exceptions levées par Selenium.

		Paramètres :
			e (Exception) : Exception levée par Selenium.
			msg (str) : Message d'erreur personnalisé (défaut : None).

		Retour :
			None
		"""
		if msg:
			exception_map = {
				TimeoutException: "Le temps d'attente est dépassé",
				NoSuchElementException: "L'élément n'a pas été trouvé",
				ElementNotVisibleException: "L'élément n'est pas visible",
				ElementNotInteractableException: "L'élément n'est pas interactif",
				StaleElementReferenceException: "L'élément n'est plus valide",
				WebDriverException: "Le driver a rencontré une erreur inattendue",
				NoSuchWindowException: "La fenêtre a été fermée",
				NoSuchFrameException: "La frame n'a pas été trouvée",
				ElementNotSelectableException: "L'élément n'est pas sélectionnable",
				ElementClickInterceptedException: "L'élément n'est pas cliquable",
			}
			# Si lé méthode error_screen n'est pas définie, on affiche le message d'erreur dans la console
			if not hasattr(self, "error_screen"):
				print_msg("ERREUR", f"{msg}", 'red')
				return
			return self.error_screen(add_erreur=f"{msg} | Erreur : {exception_map.get(type(e), f'{e}')}", check_erreur_ecoute=False)

	def presence_of_element(self, by: By = None, value: str = None, timeout: int = 1, find_all: bool = False, shadow: bool = False, msg: str = None, element: WebElement = None, attribut=None) -> WebElement:
		"""
		Vérifie la présence d'un ou plusieurs éléments en utilisant Selenium.

		Paramètres :
			by (By) : Méthode de localisation de l'élément.
			value (str) : Sélecteur de l'élément.
			find_all (bool) : True pour localiser tous les éléments, False pour un seul (défaut : False).
			timeout (int) : Temps d'attente en secondes (défaut : 1).
			shadow (bool) : True pour retourner le shadow root de l'élément, False sinon (défaut : False).
			msg (str) : Message d'erreur personnalisé (défaut : None).
			element (WebElement) : Un élément WebElement sur lequel effectuer la recherche (défaut : None).
			attribut (str) : Nom de l'attribut à retourner (défaut : None).

		Retour :
			WebElement/list[WebElement]/None : L'élément ou les éléments trouvés, leur shadow root, ou None.
		"""
		driver = self.driver if not element else element
		try:
			if by and value and timeout == 0:
				elements = driver.find_elements(by, value) if find_all else driver.find_element(by, value)
			elif by and value and timeout != 0:
				elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value))) if find_all else WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
			else:
				elements = element
			
			if attribut:
				if find_all:
					for i in range(len(elements)):
						elements[i] = elements[i].get_attribute(attribut)
				else:
					elements = elements.get_attribute(attribut)
			elif not find_all and shadow:
					return elements.shadow_root if hasattr(elements, 'shadow_root') else None
			return elements
		except Exception as e:
			message = value if msg == True else msg
			self.handle_exception(e, f"Fonction : {inspect.stack()[1][3]} | Sélecteur : " + message if message not in [None, False, True] else message)
			return None

	def click_element(self, by: By = None, value: str = None, timeout: int = 1, msg: str = None, element: WebElement = None, wait: int = 2) -> bool:
		"""
		Clique sur un élément identifié par ses critères de localisation ou un élément WebElement donné.

		Paramètres :
			by (By, optionnel) : Méthode de localisation de l'élément.
			value (str, optionnel) : Sélecteur de l'élément.
			timeout (int, optionnel) : Temps d'attente en secondes avant de renoncer à trouver l'élément (défaut : 1).
			msg (str, optionnel) : Message d'erreur personnalisé à afficher en cas d'exception (défaut : None).
			element (WebElement, optionnel) : Un élément WebElement sur lequel cliquer directement (défaut : None).

		Retour :
			bool : True si l'élément a été cliqué avec succès, False sinon.
		"""
		try:
			if timeout == 0:
				if element and not by and not value:
					element.click()
				elif element and by and value:
					element.find_element(by, value).click()
				else:
					self.driver.find_element(by, value).click()
			else:
				if element and not by and not value:
					element.click()
				elif element and by and value:
					WebDriverWait(element, timeout).until(EC.element_to_be_clickable((by, value))).click()
				else:
					WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value))).click()
			time.sleep(random.uniform(wait, wait*1.5))
			return True
		except Exception as e:
			message = value if msg == True else msg
			self.handle_exception(e, f"Fonction : {inspect.stack()[1][3]} | Sélecteur : " + message if message not in [None, False, True] else message)
			return False

	def send_keys(self, by: By = None, value: str = None, keys: str = None, timeout: int = 1, msg: str = None, element: WebElement = None, clear: bool = True) -> bool:
		"""
		Insère du texte dans un élément identifié par ses critères de localisation.

		Paramètres :
			by (By) : Méthode de localisation de l'élément.
			value (str) : Sélecteur de l'élément.
			keys (str) : Texte à insérer dans l'élément.
			timeout (int) : Temps d'attente en secondes avant de renoncer à trouver l'élément (défaut : 1).
			msg (str) : Message d'erreur personnalisé à afficher en cas d'exception (défaut : None).

		Retour :
			bool : True si le texte a été inséré avec succès, False sinon.
		"""
		try:
			driver = self.driver if not element else element
			if by and value and keys:
				elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
				try:
					elem.clear() if clear else None
				except:
					pass
				# vérifier que ce n'est pas une touche
				if isinstance(keys, str):
					for letter in keys:
						elem.send_keys(letter)
						time.sleep(random.uniform(0.05, 0.2))
				else:
					elem.send_keys(keys)
			elif element and keys:
				element.clear() if clear else None
				if isinstance(keys, str):
					for letter in keys:
						element.send_keys(letter)
						time.sleep(random.uniform(0.05, 0.2))
				else:
					element.send_keys(keys)
			
			time.sleep(random.uniform(0.8, 3.3))
			return True
		except Exception as e:
			message = value if msg == True else msg
			self.handle_exception(e, f"Fonction : {inspect.stack()[1][3]} | Sélecteur : " + message if message not in [None, False, True] else message)
			return False

	def alert_click(self, method: str) -> bool:
		"""
		Clique sur une alerte en utilisant la méthode spécifiée.

		Paramètres :
			method (str) : Méthode à utiliser pour interagir avec l'alerte ("accept" pour accepter, "dismiss" pour annuler).

		Retour :
			bool : True si l'interaction avec l'alerte a réussi, False sinon.
		"""
		try:
			alert = self.driver.switch_to.alert
			if method == "accept":
				alert.accept()
				time.sleep(random.uniform(2, 6))
			elif method == "dismiss":
				alert.dismiss()
			return True
		except:
			return False

	def has_internet_connection(self):
		"""
		Vérifie si l'ordinateur a une connexion Internet.

		Retour :
			bool : True si l'ordinateur a une connexion Internet, False sinon.
		"""
		url = "https://www.google.com"
		
		try:
			if hasattr(self, "proxy"):
				proxy_dict = {
					"http": f"http://{self.proxy}",
				}
				response = requests.get(url, proxies=proxy_dict, timeout=10)
			else:
				# Cette méthode est plus rapide que requests.get si vous n'utilisez pas de proxy
				socket.create_connection(("www.google.com", 443), timeout=10)
			return True
		except:
			return False

		
	def switch_iframe(self, by: By, value: str, timeout: int = 1, msg: str = None) -> bool:
		"""
		Change de frame en utilisant les critères de localisation donnés.

		Paramètres :
			by (By) : Méthode de localisation de l'élément.
			value (str) : Sélecteur de l'élément.
			timeout (int) : Temps d'attente en secondes avant de renoncer à trouver la frame (défaut : 1).
			msg (str) : Message d'erreur personnalisé à afficher en cas d'exception (défaut : None).

		Retour :
			bool : True si le changement de frame a réussi, False sinon.
		"""
		try:
			WebDriverWait(self.driver, timeout).until(EC.frame_to_be_available_and_switch_to_it((by, value)))
			return True
		except Exception as e:
			self.handle_exception(e, f"Fonction : {inspect.stack()[1][3]} | Sélecteur : " + value if msg == True else msg)
			return False
	
	def change_page(self, page: str) -> bool:
		"""
		Change de page en utilisant l'URL donnée.

		Paramètres :
			page (str) : URL de la page à charger.
		Retour :
			bool : True si le changement de page a réussi, False sinon.
		"""
		try:
			self.driver.get(page)
			time.sleep(random.uniform(3, 5))
			return True
		except Exception as e:
			self.handle_exception(e, False)
			return False