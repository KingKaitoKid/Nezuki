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
        self.host = f"https://{self.browser.get_host()}"

    def get_serie_info(self)->dict:
        """ Estrae il JSON dalla pagina della serie, come se fosse la risposta di una API

        Returns:
            dict: Il JSON di Streaming Community completo 
        """
        url = self.browser.get_current_url()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers)
        match = re.search(r'data-page="([^"]+)', response.text)
        if not match:
            raise RuntimeError("\u274c data-page non trovato nella risposta HTML.")
        return json.loads(html.unescape(match.group(1)))

    def __get_segment(self, title_id, episode_id):
        """
        Funzione interna per navigare alla pagina embedded di Streaming Community dove si può estrarre VixCloud
        
        Args:
            title_id (string, required): L'ID di Streaming Community della serie
            episode_id (string, required): L'ID dell'episodio di Streaming Community
        """
        iframe_page = f"{self.host}/iframe/{title_id}?episode_id={episode_id}"
        self.browser.open_url(iframe_page)
        try:
            ActionChains(self.browser.driver).move_by_offset(100, 100).click().perform()
        except Exception as e:
            print(f"\u26a0\ufe0f Errore durante il click: {e}")

    def __open_vixcloud_iframe(self):
        """Funzione interna per aprire la pagina di vixcloud se disponibile"""
        vixcloud_url = None
        for iframe in self.browser.driver.find_elements(By.TAG_NAME, "iframe"):
            src = iframe.get_attribute("src")
            if src and "vixcloud" in src:
                vixcloud_url = src
                break
        
        if vixcloud_url:
            self.browser.open_url(vixcloud_url)

    def __listen_requests(self)->dict:
        """Funzione interna per ottenere l'URL del file M3U8 master

        Examples:
            >>> __listen_requests()
            {'headers': {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0', 'accept': '*/*', 'accept-language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3', 'accept-encoding': 'gzip, deflate, br, zstd', 'referer': 'https://vixcloud.co/embed/207643?token=0b1fe0c7a02e7876d4baaa19dd02de36&t=SXRhbGlhIFNob3Jl&referer=1&expires=1745338315&d=UzE6RTEgVmFjYW56YSBNb2RlIG9uIQ%3D%3D&b=1', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'te': 'trailers'}, 'm3u8_url': 'https://vixcloud.co/playlist/207643?type=video&rendition=720p&token=OWTfNmgQd30llEMkoxEs_g&expires=1750522312&b=1'}
        """
        m3u8_url = None
        headers = None
        print(type(self.browser.driver))
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
        """
            Funzione per ottenere l'URL del file M3U8 master dell'episodio

            Args:
                title_id (string, required): L'ID di Streaming Community della serie
                episode_id (string, required): L'ID dell'episodio di Streaming Community

            Examples:
                >>> get_url_file()
                {'headers': {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0', 'accept': '*/*', 'accept-language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3', 'accept-encoding': 'gzip, deflate, br, zstd', 'referer': 'https://vixcloud.co/embed/207643?token=0b1fe0c7a02e7876d4baaa19dd02de36&t=SXRhbGlhIFNob3Jl&referer=1&expires=1745338315&d=UzE6RTEgVmFjYW56YSBNb2RlIG9uIQ%3D%3D&b=1', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'te': 'trailers'}, 'm3u8_url': 'https://vixcloud.co/playlist/207643?type=video&rendition=720p&token=OWTfNmgQd30llEMkoxEs_g&expires=1750522312&b=1'}
        """
        self.__get_segment(title_id, episode_id)
        time.sleep(3)
        self.__open_vixcloud_iframe()
        time.sleep(5)
        info_file: dict = self.__listen_requests()
        return info_file
    
    def download_file(self, info_file: dict, save_path: str):
        """
        Accoda il download del file M3U8 ottenuto da StreamingCommunity.

        Args:
            browser (Browser): L'istanza del browser con le code di download.
            info_file (dict): Dizionario con chiavi 'headers' e 'm3u8_url' (output di get_url_file).
            save_path (str): Dove salvare il file scaricato.
        """
        m3u8_url = info_file.get("m3u8_url")
        if not m3u8_url:
            logger.error("URL M3U8 non trovato, download annullato.")
            return
        self.browser.download(m3u8_url, save_path)
        logger.info(f"Accodato download M3U8 da {m3u8_url}", extra={"internal": True})