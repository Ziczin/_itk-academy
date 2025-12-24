from api.v1.wallets import wallets_router
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(wallets_router)
