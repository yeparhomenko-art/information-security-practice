from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import auth 

 
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
