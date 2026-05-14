from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.security import hash_password, verify_password
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, TokenRefreshRequest, UserInfo
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user

from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])
 
 
@router.post("/register",
         	response_model=UserResponse,
         	status_code=status.HTTP_201_CREATED,
         	summary="Реєстрація нового користувача")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
	"""
	Створює нового користувача з хешованим паролем.
 
	Кроки:
	1. Перевірити, що username та email ще не зайняті
	2. Хешувати пароль через Bcrypt
	3. Зберегти користувача в БД
	4. Повернути дані користувача (без пароля!)
	"""
	# Перевірка унікальності username
	existing_user = db.query(User).filter(
    	User.username == user_data.username
	).first()
	if existing_user:
		raise HTTPException(
        	status_code=status.HTTP_409_CONFLICT,
        	detail=f"Користувач '{user_data.username}' вже існує"
    	)
 
	# Перевірка унікальності email
	existing_email = db.query(User).filter(
    	User.email == user_data.email
	).first()
	if existing_email:
		raise HTTPException(
        	status_code=status.HTTP_409_CONFLICT,
        	detail=f"Email '{user_data.email}' вже зареєстровано"
    	)
 
	# Створення користувача з хешованим паролем
	new_user = User(
    	username=user_data.username,
    	email=user_data.email,
    	full_name=user_data.full_name,
    	password_hash=hash_password(user_data.password),
	)
 
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
 
	return new_user
 
 
@router.post("/login", response_model=TokenResponse, summary="Вхід користувача")
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Акаунт деактивовано"
        )

    role = user.roles[0].name if user.roles else "student"

    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer"
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен refresh token, а не access token"
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    role = user.roles[0].name if user.roles else "student"

    return TokenResponse(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer"
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    role = current_user.roles[0].name if current_user.roles else "student"

    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role
    )