from slowapi import Limiter
from slowapi.util import get_remote_address
 
limiter = Limiter(key_func=get_remote_address)

# @router.post("/login")
# @limiter.limit("5/minute")  # Макс. 5 спроб входу за хвилину
# async def login(request: Request, ...):
# 	...