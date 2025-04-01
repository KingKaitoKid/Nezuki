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
logger = get_nezuki_logger()

browser = Browser("firefox", False)

browser.start()
browser.get("https://google.com")