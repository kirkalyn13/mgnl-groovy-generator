from fastapi import APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address

# Base router and limiter used across routers
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)