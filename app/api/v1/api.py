from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, payments, projects, admin, investments, business_admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(investments.router, prefix="/investments", tags=["Investments"])
api_router.include_router(business_admin.router, prefix="/business-admin", tags=["Business Admin"])
