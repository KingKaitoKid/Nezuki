from nezuki.Logger import *
custom_config = {
    "file": {
        "filename": "/Users/kaitokid/Documents/vs_workspaces/Nezuki/nezuki/StreamingParser/Logs/log.log",
        "maxBytes": 100 * 1024 * 1024,  
        "backupCount": 5,
        "when": "D",
        "interval": 1
    }
}
configure_nezuki_logger(custom_config)
from nezuki.Browser import *
from nezuki.StreamingParser import *
logger = get_nezuki_logger()

browser = Browser("firefox", False)

browser.start()
browser.open_url("https://www.anisaturn.com/watch?file=bdKKKHbdpY4g0")

anisaturn = AnimeSaturn(browser)

nameFile = anisaturn.get_title().get("titolo")

file = anisaturn.player.getItemPlayer().get("url")

browser.download_mp4(file, "/Users/kaitokid/Documents/vs_workspaces/Nezuki/nezuki/StreamingParser/test.mp4")