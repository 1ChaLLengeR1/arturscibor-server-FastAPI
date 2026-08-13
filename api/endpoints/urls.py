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
