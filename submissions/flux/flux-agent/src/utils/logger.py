import logging
import sys
from typing import Optional


class AppLogger:
    _instance: Optional['AppLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        self._logger = logging.getLogger("flux_agent")
        self._logger.setLevel(logging.INFO)
        
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    @property
    def logger(self) -> logging.Logger:
        return self._logger
    
    def info(self, message: str) -> None:
        self._logger.info(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        self._logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str) -> None:
        self._logger.warning(message)
    
    def debug(self, message: str) -> None:
        self._logger.debug(message)


def get_logger() -> AppLogger:
    return AppLogger() 