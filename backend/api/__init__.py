from .auth_api import router as auth_router
from .topic_api import router as topic_router
from .profile_api import router as profile_router

__all__ = ['auth_router', 'topic_router', 'profile_router'] 