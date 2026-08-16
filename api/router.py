from fastapi import APIRouter

from api.endpoints.aboutme import get as aboutme_get
from api.endpoints.admin.aboutme import update as admin_aboutme_update
from api.endpoints.admin.aboutme.images import attach as admin_aboutme_image_attach
from api.endpoints.admin.aboutme.images import detach as admin_aboutme_image_detach
from api.endpoints.admin.contact import collection as admin_contact_collection
from api.endpoints.admin.contact import delete as admin_contact_delete
from api.endpoints.admin.cv import upload as admin_cv_upload
from api.endpoints.admin.file import collection as admin_file_collection
from api.endpoints.admin.file import confirm as admin_file_confirm
from api.endpoints.admin.file import delete as admin_file_delete
from api.endpoints.admin.file import init as admin_file_init
from api.endpoints.admin.file import upload as admin_file_upload
from api.endpoints.admin.projects import create as admin_projects_create
from api.endpoints.admin.projects import delete as admin_projects_delete
from api.endpoints.admin.projects import update as admin_projects_update
from api.endpoints.admin.projects.images import attach as admin_projects_image_attach
from api.endpoints.admin.projects.images import detach as admin_projects_image_detach
from api.endpoints.admin.tools import create as admin_tools_create
from api.endpoints.admin.tools import delete as admin_tools_delete
from api.endpoints.admin.tools import update as admin_tools_update
from api.endpoints.admin.tools.images import attach as admin_tools_image_attach
from api.endpoints.admin.tools.images import detach as admin_tools_image_detach
from api.endpoints.admin.work import create as admin_work_create
from api.endpoints.admin.work import delete as admin_work_delete
from api.endpoints.admin.work import update as admin_work_update
from api.endpoints.admin.work.items import create as admin_work_item_create
from api.endpoints.admin.work.items import delete as admin_work_item_delete
from api.endpoints.admin.work.items import update as admin_work_item_update
from api.endpoints.admin.work.logo import delete as admin_work_logo_delete
from api.endpoints.admin.work.logo import update as admin_work_logo_update
from api.endpoints.auth import login as auth_login
from api.endpoints.auth import refresh as auth_refresh
from api.endpoints.contact import create as contact_create
from api.endpoints.cv import get as cv_get
from api.endpoints.projects import collection as projects_collection
from api.endpoints.projects import one as projects_one
from api.endpoints.tools import collection as tools_collection
from api.endpoints.work import collection as work_collection

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

# AboutMe (docs/3.4-aboutme-home-section.md)
api_router.include_router(aboutme_get.router)
api_router.include_router(admin_aboutme_update.router)
api_router.include_router(admin_aboutme_image_attach.router)
api_router.include_router(admin_aboutme_image_detach.router)

# Work (docs/3.4-aboutme-home-section.md)
api_router.include_router(work_collection.router)
api_router.include_router(admin_work_create.router)
api_router.include_router(admin_work_update.router)
api_router.include_router(admin_work_delete.router)
api_router.include_router(admin_work_logo_update.router)
api_router.include_router(admin_work_logo_delete.router)
api_router.include_router(admin_work_item_create.router)
api_router.include_router(admin_work_item_update.router)
api_router.include_router(admin_work_item_delete.router)

# CV (docs/3.4-aboutme-home-section.md)
api_router.include_router(cv_get.router)
api_router.include_router(admin_cv_upload.router)

# Projects (docs/3.5-projects-section.md)
api_router.include_router(projects_collection.router)
api_router.include_router(projects_one.router)
api_router.include_router(admin_projects_create.router)
api_router.include_router(admin_projects_update.router)
api_router.include_router(admin_projects_delete.router)
api_router.include_router(admin_projects_image_attach.router)
api_router.include_router(admin_projects_image_detach.router)
