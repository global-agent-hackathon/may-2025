from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Static application configuration.
    Use the single `settings` instance when importing.
    """

    APP_NAME: str = "YouTube Agent"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 3000
    MODEL: str = "gpt-4.1-mini"
    WORKERS: int = 8
    WS_ENDPOINT: str = "/ws"


def get_settings():
    return Settings()
