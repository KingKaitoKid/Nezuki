from nezuki.Logger import *
logger = get_nezuki_logger()
from nezuki.Browser import Browser
from JWPlayer import JWPlayer
from selenium.webdriver.common.by import By
import re

class AnimeSaturn:
    def __init__(self, browser: Browser):
        """
        Inizializza l'oggetto Anime Saturn insieme al player
        
        Args:
            browser (Browser, required): Istanza del browser avviato (del modulo Nezuki)
        """
        self.browser = browser
        self.player = JWPlayer(self.browser)

    def get_title(self)->dict:
        """
            Estrae il titolo dell'anime e il numero dell'episodio dalla pagina di Anime Saturn.

            Returns:
                dict: Dizionario con le chiavi "titolo" e "episodio".

            Examples:
                >>> get_title() # Happy case
                {'titolo': 'One Piece', 'episodio': '1050'}

                >>> get_title() # Bad case
                {'titolo': 'TOCHECKFILE_AnimeNameMissing', 'episodio': 'Episodio X'}
        """
        data_return: dict = {"titolo": 'TOCHECKFILE_AnimeNameMissing', "episodio": "Episodio X"}
        try:
            rowTitle = self.browser.find_element(By.XPATH, '//h4')
            pattern = r'(.+) Episodio (\d+)'
            string_parsed = re.match(pattern, rowTitle.text.strip())
            logger.debug(f"Effettuato parsing con output: {string_parsed}", extra={"internal": True})
            data_return = {"titolo": string_parsed.group(1), "episodio": string_parsed.group(2)}
            logger.debug(f"Il titolo ricavato è: {data_return}", extra={"internal": True})
            return data_return
        except Exception as e:
            return data_return
        
    def get_next_episode(self)->str|None:
        """
            Ottiene, se disponibile, il prossimo episodio da vedere

            Examples:
                >>> get_next_episode() # Happy case
                '/watch?file=3ZqYJugfVUOq&server=0'

                >>> get_next_episode() # Bad case
                None
        """
        try:
            next_div = self.browser.driver.find_element(By.XPATH, '//div[@title="Episodio successivo"]')
            onclick_attr = next_div.get_attribute("onclick")
            logger.debug(f"Localizzazione del prossimo episodio", extra={"internal": True})
            if onclick_attr and "window.location.href=" in onclick_attr:
                match = re.search(r"window.location.href='([^']+)'", onclick_attr)
                if match:
                    next_url = match.group(1)
                    logger.debug(f"Prossimo episodio localizzato: {next_url}", extra={"internal": True})
                    return next_url
        except Exception as e:
            logger.error(f"Non è stato possibile localizzare il prossimo episodio perché non disponibile o per un errore: {e}", extra={"internal": True})
            print(f"Failed to get next episode URL: {e}")
        return None
    