from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
 
from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import TokenResponse, TokenRefreshRequest, UserInfo
 
# Імпортуйте вашу функцію перевірки пароля з практичної №4
from app.security import verify_password
 
router = APIRouter(prefix="/auth", tags=["Authentication"])
 

from app.audit.logger import log_login_success, log_login_failed
from app.audit.detector import check_brute_force, check_off_hours_access
 
@router.post("/login")
async def login(request: Request, credentials: LoginRequest,
            	db: Session = Depends(get_db)):
	ip = request.client.host
 
	# Перевірка Brute Force ДО перевірки пароля
	if check_brute_force(db, ip):
		log_login_failed(db, credentials.username, ip, "brute_force_blocked")
		raise HTTPException(status_code=429,
        	detail="Забагато невдалих спроб. Спробуйте пізніше.")
 
	user = authenticate_user(db, credentials.username, credentials.password)
	if not user:
		log_login_failed(db, credentials.username, ip)
		raise HTTPException(status_code=401, detail="Невірний логін або пароль")
 
	from datetime import datetime, timezone
	check_off_hours_access(db, user.id, user.username, ip,
                       	datetime.now(timezone.utc).hour)
	log_login_success(db, user.id, user.username, ip)
 
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
	"""Оновлення access token за допомогою refresh token."""
	try:
		payload = verify_token(body.refresh_token)
	except JWTError:
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Невалідний refresh token",
    	)
 
	if payload.get("type") != "refresh":
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Потрібен refresh token, а не access token",
    	)
 
	user_id = int(payload["sub"])
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="Користувача не знайдено")
 
	role = user.roles[0].name if user.roles else "student"
	new_access = create_access_token(user_id, role)
	new_refresh = create_refresh_token(user_id)
 
	return TokenResponse(access_token=new_access, refresh_token=new_refresh)
 
 
@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
	"""Повертає інформацію про поточного автентифікованого користувача."""
	role = current_user.roles[0].name if current_user.roles else "student"
	return UserInfo(
    	id=current_user.id,
    	username=current_user.username,
    	email=current_user.email,
    	full_name=current_user.full_name,
    	role=role,
	)