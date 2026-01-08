from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

RATE_LIMIT_AI = settings.rate_limit_ai
RATE_LIMIT_AUTH = settings.rate_limit_auth
