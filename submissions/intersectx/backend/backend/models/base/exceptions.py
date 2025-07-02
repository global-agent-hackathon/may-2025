from enum import StrEnum, auto


class Status(StrEnum):
    SUCCESS = auto()
    CREATED = auto()
    BAD_REQUEST = auto()
    ENTITY_NOT_FOUND = auto()
    MISSING_PARAMS = auto()
    UNAUTHORIZED = auto()
    EXECUTION_ERROR = auto()
    INVALID_PARAM = auto()
    NOT_PROCESSED = auto()
    MISSING_DATA = auto()
    INVALID_DATA = auto()
    THROTTLED = auto()
    UNKNOWN_ERROR = auto()
    NOT_FOUND = auto()
    NOT_IMPLEMENTED = auto()


class NotFoundException(Exception):
    """Simple exception for when an entity is not found."""

    def __init__(self, message: str):
        self.message = message
        self.status = Status.NOT_FOUND
        super().__init__(self.message)
