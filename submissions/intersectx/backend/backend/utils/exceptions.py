from typing import Any, Optional

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.models.base.exceptions import Status
from backend.utils.logger import get_logger

LOG = get_logger()


class ServiceException(Exception):  # pragma: no cover
    def __init__(
        self,
        status: Status,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        super(ServiceException, self).__init__(
            f"{status}: {dict(status=status, message=message, details=details)}"
        )
        self.status = status
        self.message = message
        self.details = details

    @property
    def _reason_status_map(self):
        return {
            Status.BAD_REQUEST.name: status.HTTP_400_BAD_REQUEST,
            Status.INVALID_PARAM.name: status.HTTP_400_BAD_REQUEST,
            Status.NOT_PROCESSED.name: status.HTTP_400_BAD_REQUEST,
            Status.MISSING_DATA.name: status.HTTP_400_BAD_REQUEST,
            Status.INVALID_DATA.name: status.HTTP_400_BAD_REQUEST,
            Status.MISSING_PARAMS.name: status.HTTP_400_BAD_REQUEST,
            Status.UNAUTHORIZED.name: status.HTTP_403_FORBIDDEN,
            Status.ENTITY_NOT_FOUND.name: status.HTTP_404_NOT_FOUND,
            Status.THROTTLED.name: status.HTTP_408_REQUEST_TIMEOUT,
            Status.EXECUTION_ERROR.name: status.HTTP_500_INTERNAL_SERVER_ERROR,
            Status.NOT_FOUND.name: status.HTTP_404_NOT_FOUND,
        }

    def get_code(self, reason: str) -> status:
        return self._reason_status_map.get(reason)


def exception_handler(request: Request, exc: ServiceException):
    LOG.error(
        f"{request.method} {request.url} ({request.query_params}): {exc}", exc_info=True
    )

    return JSONResponse(
        status_code=exc.get_code(exc.reason.name),
        content={
            "http_code": exc.get_code(exc.reason.name),
            "status": exc.status.value,
            "message": exc.message,
            "details": exc.details if exc.details else None,
        },
    )
