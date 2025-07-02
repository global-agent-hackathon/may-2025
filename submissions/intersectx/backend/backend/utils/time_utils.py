from datetime import datetime
from enum import Enum


class TimeUnit(str, Enum):
    MILLI_SECOND = "ms"
    SECOND = "secs"
    MINUTE = "mins"

    def __float__(self):
        """
        Normalize the time unit to seconds

        >>> float(TimeUnit.MILLI_SECOND)
        1000

        >>> float(TimeUnit.SECOND)
        1

        >>> float(TimeUnit.MINUTE)
        0.01666666667

        :return: time unit normalized to seconds
        """
        mapping = {
            "MILLI_SECOND": 1000.0,
            "SECOND": 1.0,
            "MINUTE": 0.01666666667,  # 1/ 60
        }
        return mapping[self.name]


def show_time_taken(
    start: datetime,
    message: str = "",
    time_unit: TimeUnit = TimeUnit.MILLI_SECOND,
    logger=None,
):
    """
    A simple util to log time taken for any execution

    :param start: Provide a datetime object (this is to be initialized at client end before starting the execution
    :param message: Optional message to be logged/displayed along with time
    :param time_unit: Unit in which time should be displayed
    :param logger: Logger to be used for logging/printing the message

    :return: Time taken for the execution

    Example
    ---

    >>> s = datetime.now()
    >>> LOG = get_logger()
    >>> time.sleep(1)
    >>> show_time_taken(s, message="My random task")
    [info ] My random task took 1000 ms
    1000
    """
    e = datetime.now()
    tt = (e - start).total_seconds() * float(time_unit)
    if logger:
        logger.info(f"{message} took {tt} {time_unit.value}")
    else:
        print(f"{message} took {tt} {time_unit.value}")

    return tt
