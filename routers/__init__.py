from fastapi import APIRouter

router_tasks = APIRouter(
    redirect_slashes=False,
    prefix="/api/tasks",
    tags=["tasks"],
)
router_check = APIRouter(
    redirect_slashes=False,
    prefix="/api/check",
    tags=["check"],
)

