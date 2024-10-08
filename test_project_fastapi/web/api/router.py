from fastapi.routing import APIRouter
from test_project_fastapi.web.api import echo, orders
from test_project_fastapi.web.api import docs
from test_project_fastapi.web.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(orders.router, prefix="/orders", tags=["order"])
