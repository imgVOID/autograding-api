from fastapi import APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router_tasks = APIRouter(
    redirect_slashes=False,
    prefix="/api/tasks",
    tags=["tasks"],
)
router_themes = APIRouter(
    redirect_slashes=False,
    prefix="/api/themes",
    tags=["themes"],
)
router_check = APIRouter(
    redirect_slashes=False,
    prefix="/api/check",
    tags=["check"],
)
