from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.exception_handlers import register_exception_handlers
from api.router import api_router
from config.settings import settings
from database.psql.models.file import ALLOWED_DIRECTORIES

# Old, not-yet-migrated domains (routers/) are unplugged on purpose — see
# docs/3.2-3.5-*.md. Files still exist on disk, just not imported/included
# here, so only the migrated endpoints (currently: auth, contact, file) are live.

app = FastAPI()

register_exception_handlers(app)

# Uploady: jedno źródło prawdy dla ścieżki (settings.static_root, absolutna) i dla
# listy katalogów (ALLOWED_DIRECTORIES z modelu File) — patrz docs/6-file-storage-section-done.md.
_STATIC_ROOT = settings.static_root
_STATIC_ROOT.mkdir(parents=True, exist_ok=True)
for _directory in sorted(ALLOWED_DIRECTORIES):
    (_STATIC_ROOT / _directory).mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_STATIC_ROOT)), name="static")

# Restrykcyjnie: skończona lista originów (nie []  — to blokowałoby też legalny
# frontend; nie "*" — niebezpieczne w połączeniu z allow_credentials), skończona
# lista metod/nagłówków zamiast "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(api_router)
