from fastapi import APIRouter

from api.endpoints.admin.contact import collection as admin_contact_collection
from api.endpoints.admin.contact import delete as admin_contact_delete
from api.endpoints.admin.file import collection as admin_file_collection
from api.endpoints.admin.file import confirm as admin_file_confirm
from api.endpoints.admin.file import delete as admin_file_delete
from api.endpoints.admin.file import init as admin_file_init
from api.endpoints.admin.file import upload as admin_file_upload
from api.endpoints.admin.tools import create as admin_tools_create
from api.endpoints.admin.tools import delete as admin_tools_delete
from api.endpoints.admin.tools import update as admin_tools_update
from api.endpoints.admin.tools.images import attach as admin_tools_image_attach
from api.endpoints.admin.tools.images import detach as admin_tools_image_detach
from api.endpoints.auth import login as auth_login
from api.endpoints.auth import refresh as auth_refresh
from api.endpoints.contact import create as contact_create
from api.endpoints.tools import collection as tools_collection

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

# File (docs/6-file-storage-section-done.md)
api_router.include_router(admin_file_init.router)
api_router.include_router(admin_file_upload.router)
api_router.include_router(admin_file_confirm.router)
api_router.include_router(admin_file_collection.router)
api_router.include_router(admin_file_delete.router)

# Tools (docs/3.3-tools-section-done.md)
api_router.include_router(tools_collection.router)
api_router.include_router(admin_tools_create.router)
api_router.include_router(admin_tools_update.router)
api_router.include_router(admin_tools_delete.router)
api_router.include_router(admin_tools_image_attach.router)
api_router.include_router(admin_tools_image_detach.router)
