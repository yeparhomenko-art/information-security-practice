from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models

from app.routers import auth
from app.routers.students import router as students_router
from app.routers.teachers import router as teachers_router
from app.routers.admin import router as admin_router

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.middleware.rate_limiter import limiter

from app.middleware.security_headers import SecurityHeadersMiddleware

from app.audit.middleware import AuditMiddleware

from app.audit.models import AuditLog

app = FastAPI(
    title="Електронний деканат",
    description="API для управління академічними даними",
    version="0.4.0"
)

Base.metadata.create_all(bind=engine)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(SecurityHeadersMiddleware)
 
from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router
 
app.add_middleware(AuditMiddleware)
app.include_router(audit_router, prefix="/admin", tags=["audit"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3010",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "Електронний деканат API v0.4.0"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "SQLite",
        "tables": len(Base.metadata.tables)
    }