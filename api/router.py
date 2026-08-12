from fastapi import APIRouter

from api.endpoints.admin.contact import collection as admin_contact_collection
from api.endpoints.admin.contact import delete as admin_contact_delete
from api.endpoints.auth import login as auth_login
from api.endpoints.auth import refresh as auth_refresh
from api.endpoints.contact import create as contact_create

# Central router — each migrated domain (see docs/3.1-3.5-*.md) registers its
# endpoint router here via api_router.include_router(...).
api_router = APIRouter()

# Auth (docs/3.1-auth-section.md)
api_router.include_router(auth_login.router)
api_router.include_router(auth_refresh.router)

# Contact (docs/3.2-contact-section.md)
api_router.include_router(contact_create.router)
api_router.include_router(admin_contact_collection.router)
api_router.include_router(admin_contact_delete.router)
