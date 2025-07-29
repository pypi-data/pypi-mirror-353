import os

DEFAULT_MAGIQUE_SERVER_URL = """ws://magique.spateo.aristoteleo.com/ws
ws://server.magique1.aristoteleo.com/ws
ws://server.magique2.aristoteleo.com/ws"""

_SERVER_URL = os.environ.get("MAGIQUE_SERVER_URL", DEFAULT_MAGIQUE_SERVER_URL)

SERVER_URLS = []
if "\n" in _SERVER_URL:
    SERVER_URLS = _SERVER_URL.split("\n")
else:
    SERVER_URLS = [_SERVER_URL]
