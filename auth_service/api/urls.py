from fastapi import APIRouter

from api.v1 import auth, roles, user

router = APIRouter(prefix='/api')

router.include_router(auth.router, prefix='/v1')
router.include_router(user.router, prefix='/v1')
router.include_router(roles.router, prefix='/v1')
