from typing import Optional

from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute

from backend.utils.logger import get_logger

LOG = get_logger()


def fix_cbv_class_name_bug(route: APIRoute):
    """
    As of fastapi-utils v0.8.0.
    The cbv decorator includes the class name. This function removes the class name.

    Ref: https://github.com/fastapiutils/fastapi-utils/blob/e9e7e2c834d703503a3bf5d5605db6232dd853b9/fastapi_utils/cbv.py#L132
    """
    try:
        route.name = route.name.split(".")[1]
        route.tags = list(set(route.tags))
    except IndexError:
        pass


def register_routers(
    app: FastAPI,
    protected_routers: Optional[list[APIRouter]] = None,
    unprotected_routers: Optional[list[APIRouter]] = None,
):
    if protected_routers is None:
        protected_routers = []

    if unprotected_routers is None:
        unprotected_routers = []

    _unprotected_routes = []

    for r in protected_routers:
        for route in r.routes:
            fix_cbv_class_name_bug(route)
            if hasattr(route.endpoint, "_unprotected"):
                _unprotected_routes.append(route.path)

        app.include_router(r)

    for r in unprotected_routers:
        for route in r.routes:
            fix_cbv_class_name_bug(route)
            _unprotected_routes.append((route.methods, route.path))

        app.include_router(r)

    if _unprotected_routes:
        LOG.warning(
            f"The following endpoints are marked unprotected: {_unprotected_routes}"
        )

    return [x[1] for x in _unprotected_routes]
