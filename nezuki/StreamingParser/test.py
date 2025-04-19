from nezuki.Logger import *

custom_config = {
    "file": {
        "filename": "/Users/kaitokid/Documents/Nezuki/nezuki/StreamingParser/logs.log",
        "maxBytes": 100 * 1024 * 1024,
        "backupCount": 5,
        "when": "D",
        "interval": 1
    }
}
configure_nezuki_logger(custom_config)
logger = get_nezuki_logger()

from nezuki.Browser import *
from nezuki.StreamingParser import *

browser = Browser("firefox", True)
browser.setup_options()
browser.start()
browser.open_url("https://www.anisaturn.com/watch?file=pBC_1hqFyAm65")

anisaturn = AnimeSaturn(browser)

# Recupera titolo e URL
nameFile = anisaturn.get_title().get("titolo")
file = anisaturn.player.getItemPlayer().get("url")

# Invia alla coda di download del browser
save_path = f"/Users/kaitokid/Documents/vs_workspaces/Nezuki/nezuki/StreamingParser/{nameFile}.mp4"
browser.download(file, save_path)

# Esegue i download in batch
browser.process_download_queue()

# Prossimo episodio (da usare in ciclo se vuoi gestire tutta la serie)
next_ep = anisaturn.get_next_episode()
logger.info(f"Prossimo episodio: {next_ep}")
