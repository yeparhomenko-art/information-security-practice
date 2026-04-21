from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import auth

from app.auth.router import router as auth_router 
from app.routers.students import router as students_router
from app.routers.teachers import router as teachers_router
from app.routers.admin import router as admin_router

app = FastAPI(
	title="Електронний деканат",
	description="API для управління академічними даними",
	version="0.4.0"
)
 
# Підключення роутерів
app.include_router(auth.router)
 
 
@app.get("/")
def root():
	return {"message": "Електронний деканат API v0.4.0"}
 
 
@app.get("/health")
def health_check():
	# ... ваш існуючий health check з практичної №3 ...
	pass


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)