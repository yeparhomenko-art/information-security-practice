from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
 
from app.database import get_db
from app.models import User
from app.auth.jwt_handler import verify_token
 
# Схема Bearer — витягує токен із заголовка Authorization: Bearer <token>
security = HTTPBearer()
 
 
def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	db: Session = Depends(get_db)
) -> User:
	"""
	Dependency, що перевіряє JWT та повертає об'єкт User.
	Використовується у кожному захищеному ендпоінті.
	"""
	token = credentials.credentials
 
	try:
		payload = verify_token(token)
	except JWTError:
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Невалідний або протермінований токен",
        	headers={"WWW-Authenticate": "Bearer"},
    	)
 
	# Перевірка типу токена — access, а не refresh
	if payload.get("type") != "access":
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Потрібен access token, а не refresh token",
    	)
 
	user_id = payload.get("sub")
	if user_id is None:
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Токен не містить ідентифікатора користувача",
    	)
 
	user = db.query(User).filter(User.id == int(user_id)).first()
	if user is None:
		raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Користувача не знайдено",
    	)
 
	return user
 
 
def require_role(*allowed_roles: str):
	"""
	Фабрика залежностей для перевірки RBAC-ролі.
	Використання: Depends(require_role("admin", "teacher"))
	"""
	def role_checker(current_user: User = Depends(get_current_user)) -> User:
		user_roles = [r.name for r in current_user.roles]
		if not any(role in user_roles for role in allowed_roles):
			raise HTTPException(
            	status_code=status.HTTP_403_FORBIDDEN,
            	detail=f"Доступ заборонено. Потрібна роль: {', '.join(allowed_roles)}",
        	)
		return current_user
 
	return role_checker