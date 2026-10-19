"""Optional Instagram client. Never read or persist login sessions on disk."""
from essentiabot_lib import config

class InstagramSession:
    _client = None
    _initialized = False
    last_error = None

    @classmethod
    def get_client(cls):
        if cls._initialized:
            return cls._client
        cls._initialized = True
        cls.last_error = None
        if not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
            return None
        try:
            from instagrapi import Client
            client = Client()
            client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
            cls._client = client
        except Exception as exc:
            # No retries or security-setting changes for authentication challenges.
            cls._client = None
            cls.last_error = type(exc).__name__
        return cls._client

    @classmethod
    def reset(cls):
        cls._client = None
        cls._initialized = False
        cls.last_error = None
