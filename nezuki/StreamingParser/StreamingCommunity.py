from nezuki.Logger import *
logger = get_nezuki_logger()
from nezuki.Browser import Browser
from JWPlayer import JWPlayer
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import re, requests, json, html, time

class StreamingCommunity:
    def __init__(self, browser: Browser):
        """
        Inizializza l'oggetto Streaming Community 
        
        Args:
            browser (Browser, required): Istanza del browser avviato (del modulo Nezuki)
        """
        self.browser = browser
        self.host = ""
        self.player = JWPlayer(self.browser)

    def get_serie_info(self, url: str)->dict:
        """ Estrae il JSON dalla pagina della serie, come se fosse la risposta di una API

        Returns:
            dict: Il JSON di Streaming Community completo 
        """
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers)
        match = re.search(r'data-page="([^"]+)', response.text)
        if not match:
            raise RuntimeError("\u274c data-page non trovato nella risposta HTML.")
        return json.loads(html.unescape(match.group(1)))

    def __get_segment(self, title_id, episode_id):
        iframe_page = f"{self.host}/iframe/{title_id}?episode_id={episode_id}"
        self.browser.open_url(iframe_page)
        try:
            ActionChains(self.browser.driver).move_by_offset(100, 100).click().perform()
        except Exception as e:
            print(f"\u26a0\ufe0f Errore durante il click: {e}")

    def __open_vixcloud_iframe(self):
        vixcloud_url = None
        for iframe in self.browser.driver.find_elements(By.TAG_NAME, "iframe"):
            src = iframe.get_attribute("src")
            if src and "vixcloud" in src:
                vixcloud_url = src
                break
        
        if vixcloud_url:
            self.browser.open_url(vixcloud_url)

    def __listen_requests(self):
        m3u8_url = None
        headers = None

        for request in reversed(self.browser.driver.requests):
            if (
                request.response
                and request.response.status_code == 200
                # and ".m3u8" in request.url
                and "playlist" in request.url
                and "rendition=720" in request.url
            ):
                m3u8_url = request.url
                headers = dict(request.headers)
                break
        return {"headers": headers, "m3u8_url": m3u8_url}

    def get_url_file(self, title_id, episode_id)->dict:
        self.__get_segment(title_id, episode_id)
        time.sleep(3)
        self.__open_vixcloud_iframe()
        time.sleep(5)
        info_file: dict = self.__listen_requests()
        return info_file