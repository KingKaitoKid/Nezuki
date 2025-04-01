import os
import time
import argparse
import typing
import urllib.request
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from nezuki.Logger import *

logger = get_nezuki_logger()

class Browser:
    """ Classe che permette di avviare e controllare un browser """
    def __init__(self, browserName: typing.Literal['firefox', 'chrome'], headless: bool = True):
        """
            Classe che istanzia l'oggetto Browser

            Args:
                browserName (string, required): Nome del browser che si intende avviare
                headless (bool, optional): Esegui in modalità senza GUI (default True)
        """
        self.browserName = browserName
        self.headless = headless
        self.driver = None

        logger.debug(f"Browser scelto è {browserName.capitalize()}", extra={"internal": True})
        if browserName == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            self.Options = FirefoxOptions
            self.Service = FirefoxService
            self.DriverManager = GeckoDriverManager
        elif browserName == "chrome":
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            self.Options = Options
            self.Service = Service
            self.DriverManager = ChromeDriverManager
        else:
            raise ValueError(f"Browser '{browserName}' non supportato.")

        self.options = self.setup_options()

    def setup_options(self, options: list = ['disable-gpu', 'no-sandbox']) -> 'Options':
        """
        Definisce e restituisce le opzioni per il browser.

        Args:
            options (list, optional): Lista di opzioni per il driver browser da settare (default ['disable-gpu', 'no-sandbox']), **se il browser richiesto è headless** viene aggiunta l'opzione automaticamente

        Returns:
            Options (list, optional): oggetto contenente le opzioni di configurazione per il browser selezionato (default ['disable-gpu', 'no-sandbox'])
        """
        optionsDefined = self.Options() # LEggiamo le opzioni del browser
        if self.headless:
            logger.debug(f"Aggiungo opzione headless", extra={"internal": True})
            options.add_argument("--headless")
        logger.debug(f"Aggiungo le opzioni {options}", extra={"internal": True})
        for option in options:
            optionsDefined.add_argument(f"--{option}")
        return optionsDefined

    def start(self):
        """
            Avvia il browser con le opzioni definite nel costruttore.
        """
        service = self.Service(self.DriverManager().install())
        logger.debug(f"Avvio {self.browserName.capitalize()} con le opzioni {self.options}", extra={"internal": True})
        if self.browserName == "firefox":
            from selenium.webdriver import Firefox
            self.driver = Firefox(service=service, options=self.options)
        elif self.browserName == "chrome":
            from selenium.webdriver import Chrome
            self.driver = Chrome(service=service, options=self.options)

    def quit(self):
        """
            Chiude il browser se è stato avviato.
        """
        if self.driver:
            logger.debug(f"Chiudo il browser {self.browserName}", extra={"internal": True})
            self.driver.quit()
        else:
            logger.warning(f"Nessun browser da chiudere perché mai avviato", extra={"internal": True})

    def open_url(self, url: str):
        """
        Naviga verso l'URL specificato.

        Args:
            url (str): L'indirizzo web da visitare.
        """
        if self.driver:
            logger.debug(f"Apro in {self.browserName} l'url {url}", extra={"internal": True})
            self.driver.get(url)
        else:
            logger.warning(f"Non è stato avviato alcun browser, apertura url {url} fallita", extra={"internal": True})

    def find(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Trova un singolo elemento nella pagina.

        Args:
            selector (str): Selettore dell'elemento.
            by (By, optional): Metodo di selezione (es. By.ID, By.CLASS_NAME, By.XPATH). Default By.CSS_SELECTOR.

        Returns:
            WebElement: L'elemento trovato.
        """
        logger.debug(f"Cerco l'elemento {selector} secondo il filtro {by}", extra={"internal": True})
        return self.driver.find_element(by, selector)

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Trova tutti gli elementi che corrispondono al selettore.

        Args:
            selector (str): Selettore degli elementi.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.

        Returns:
            list[WebElement]: Lista di elementi trovati.
        """
        logger.debug(f"Cerco gli elementi {selector} secondo il filtro {by}", extra={"internal": True})
        return self.driver.find_elements(by, selector)

    def click(self, selector: str, by: By = By.CSS_SELECTOR):
        """
        Clicca su un elemento nella pagina.

        Args:
            selector (str): Selettore dell'elemento da cliccare.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
        """
        logger.debug(f"Effettuo il click sull'elemento {selector} applicando il filtro {by}", extra={"internal": True})
        el = self.find(selector, by)
        el.click()

    def type(self, selector: str, text: str, by: By = By.CSS_SELECTOR):
        """
        Inserisce testo in un campo input.

        Args:
            selector (str): Selettore dell'input.
            text (str): Testo da inserire.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
        """
        logger.debug(f"Scrivo il testo \"{text}\" nel campo {selector} con il filtro di ricera {by}", extra={"internal": True})
        el = self.find(selector, by)
        el.clear()
        el.send_keys(text)

    def wait_for(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10):
        """
        Attende la presenza di un elemento nel DOM.

        Args:
            selector (str): Selettore dell'elemento.
            by (By, optional): Metodo di selezione. Default By.CSS_SELECTOR.
            timeout (int, optional): Tempo massimo di attesa in secondi. Default 10.

        Returns:
            WebElement: L'elemento trovato, se presente entro il timeout.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        logger.debug(f"Il browser è in attesa dell'elemento {selector} con filtro {by}, attende {timeout} secondi prima di dare timeout", extra={"internal": True})
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))

    def screenshot(self, path: str):
        """
        Salva uno screenshot della pagina corrente.

        Args:
            path (str): Percorso completo del file dove salvare lo screenshot.
        """
        if self.driver:
            logger.debug(f"Salvo lo screenshot della pagina nel path {path}", extra={"internal": True})
            self.driver.save_screenshot(path)
        else:
            logger.warning(f"Non è possibile fare uno screenshot ad un browser mai avviatoq", extra={"internal": True})