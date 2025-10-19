from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, payments, projects, admin, investments, business_admin, support, support_ws, notifications, notifications_ws, kyc, webhooks, documents

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(investments.router, prefix="/investments", tags=["Investments"])
api_router.include_router(business_admin.router, prefix="/business-admin", tags=["Business Admin"])
api_router.include_router(support.router, prefix="/support", tags=["Support"])
api_router.include_router(support_ws.router, tags=["Support WebSocket"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(notifications_ws.router, tags=["Notifications WebSocket"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
