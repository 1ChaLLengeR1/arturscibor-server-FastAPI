from fastapi import APIRouter

# Central router — each migrated domain (see docs/3.1-3.5-*.md) registers its
# endpoint router here via api_router.include_router(...).
api_router = APIRouter()
