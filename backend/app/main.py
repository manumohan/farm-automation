from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user_router, tenant_router, farm_router, section_router, device_router, peripheral_router, schedule_router
from app.core.config import settings

app = FastAPI(title="Farm Automation Platform")

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1")
app.include_router(tenant_router, prefix="/api/v1")
app.include_router(farm_router, prefix="/api/v1")
app.include_router(section_router, prefix="/api/v1")
app.include_router(device_router, prefix="/api/v1")
app.include_router(peripheral_router, prefix="/api/v1")
app.include_router(schedule_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Farm Automation Platform API"} 