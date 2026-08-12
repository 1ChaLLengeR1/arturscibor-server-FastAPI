from fastapi import APIRouter

from api.endpoints.auth import login as auth_login
from api.endpoints.auth import refresh as auth_refresh

# Central router — each migrated domain (see docs/3.1-3.5-*.md) registers its
# endpoint router here via api_router.include_router(...).
api_router = APIRouter()

# Auth (docs/3.1-auth-section.md)
api_router.include_router(auth_login.router)
api_router.include_router(auth_refresh.router)
