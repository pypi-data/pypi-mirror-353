"""
Class to handle base websocket client
"""

from .base_client import BaseClient


class WsClient(BaseClient):
    """Websocket client class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = self.connect_ws()
        self.login_client()
