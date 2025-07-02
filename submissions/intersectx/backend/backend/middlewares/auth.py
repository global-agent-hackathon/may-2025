import jwt
from fastapi import Request, FastAPI

from starlette.middleware.base import BaseHTTPMiddleware

from backend.models.base.exceptions import Status
from backend.settings import JWTConfig, get_app_settings
from backend.utils.exceptions import ServiceException


class AuthMiddleWare(BaseHTTPMiddleware):
    def __init__(
        self, app, jwt_config: JWTConfig, unprotected_routes: list[str] = None
    ):
        super().__init__(app)
        self.unprotected_routes = unprotected_routes
        self.jwt_config = jwt_config

    async def dispatch(self, request: Request, call_next):
        # Bypass authentication for excluded routes
        if request.url.path in self.unprotected_routes:
            return await call_next(request)

        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise ServiceException(
                Status.UNAUTHORIZED, message="Missing Authorization Header"
            )

        # Example: Expecting a Bearer token
        if not auth_header.startswith("Bearer "):
            raise ServiceException(Status.UNAUTHORIZED, message="Invalid Token")

        token = auth_header.split(" ")[1]

        # Simple token validation (Replace with your actual token verification)
        try:
            payload = jwt.decode(
                token,
                self.jwt_config.secret_key,
                algorithms=[self.jwt_config.algorithm],
            )
            request.state.user = (
                payload  # Attach user info to request for use in routes
            )
        except jwt.ExpiredSignatureError:
            raise ServiceException(
                reason=Status.UNAUTHORIZED, message="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise ServiceException(reason=Status.UNAUTHORIZED, message="Invalid Token")

        # If token is valid, proceed to the next request
        response = await call_next(request)
        return response


def get_auth_middleware(app: FastAPI, unprotected_routes: list[str] = None):
    app_settings = get_app_settings()  # Manually calling the dependency
    return AuthMiddleWare(app, app_settings.jwt_config, unprotected_routes)
