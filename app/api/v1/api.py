from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, payments, projects, admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
