# All endpoint paths as constants, /api/v1/{scope}/{resource}/{action}.
# Populated domain by domain as each section from docs/3.1-3.5-*.md migrates.

AUTH_LOGIN = "/api/v1/auth/login"
AUTH_REFRESH = "/api/v1/auth/refresh"

CONTACT_CREATE = "/api/v1/contact/create"
ADMIN_CONTACT_COLLECTION = "/api/v1/admin/contact/collection"
ADMIN_CONTACT_DELETE = "/api/v1/admin/contact/{contact_id}/delete"

ADMIN_FILE_INIT = "/api/v1/admin/file/init"
ADMIN_FILE_UPLOAD = "/api/v1/admin/file/{file_id}/upload"
ADMIN_FILE_CONFIRM = "/api/v1/admin/file/{file_id}/confirm"
ADMIN_FILE_COLLECTION = "/api/v1/admin/file/collection"
ADMIN_FILE_DELETE = "/api/v1/admin/file/{file_id}/delete"

TOOLS_COLLECTION = "/api/v1/tools/collection"
ADMIN_TOOLS_CREATE = "/api/v1/admin/tools/create"
ADMIN_TOOLS_UPDATE = "/api/v1/admin/tools/{tool_id}/update"
ADMIN_TOOLS_DELETE = "/api/v1/admin/tools/{tool_id}/delete"
ADMIN_TOOLS_IMAGE_ATTACH = "/api/v1/admin/tools/{tool_id}/images"
ADMIN_TOOLS_IMAGE_DETACH = "/api/v1/admin/tools/{tool_id}/images/{file_id}"

ABOUT_ME = "/api/v1/aboutme"
ADMIN_ABOUT_ME_UPDATE = "/api/v1/admin/aboutme/update"
ADMIN_ABOUT_ME_IMAGE_ATTACH = "/api/v1/admin/aboutme/images"
ADMIN_ABOUT_ME_IMAGE_DETACH = "/api/v1/admin/aboutme/images/{file_id}"

WORK_COLLECTION = "/api/v1/work/collection"
ADMIN_WORK_CREATE = "/api/v1/admin/work/create"
ADMIN_WORK_UPDATE = "/api/v1/admin/work/{work_id}/update"
ADMIN_WORK_DELETE = "/api/v1/admin/work/{work_id}/delete"
ADMIN_WORK_LOGO = "/api/v1/admin/work/{work_id}/logo"
ADMIN_WORK_ITEM_CREATE = "/api/v1/admin/work/{work_id}/items"
ADMIN_WORK_ITEM_UPDATE = "/api/v1/admin/work/{work_id}/items/{item_id}/update"
ADMIN_WORK_ITEM_DELETE = "/api/v1/admin/work/{work_id}/items/{item_id}/delete"

CV = "/api/v1/cv"
ADMIN_CV_UPLOAD = "/api/v1/admin/cv/upload"

PROJECTS_COLLECTION = "/api/v1/projects/collection"
PROJECTS_ONE = "/api/v1/projects/{project_id}"
ADMIN_PROJECTS_CREATE = "/api/v1/admin/projects/create"
ADMIN_PROJECTS_UPDATE = "/api/v1/admin/projects/{project_id}/update"
ADMIN_PROJECTS_DELETE = "/api/v1/admin/projects/{project_id}/delete"
ADMIN_PROJECTS_IMAGE_ATTACH = "/api/v1/admin/projects/{project_id}/images"
ADMIN_PROJECTS_IMAGE_DETACH = "/api/v1/admin/projects/{project_id}/images/{file_id}"
