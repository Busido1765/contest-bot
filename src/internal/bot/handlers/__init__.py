from .base import router as base_router
from .admins import router as admins_router
from .blacklist import router as blacklist_router
from .channels import router as channels_router
from .contests import router as contests_router
from .events import router as events_router
from .contest_results import router as contest_results_router
from .contests_active import router as contests_active_router

from aiogram import Router 

router = Router()

router.include_router(base_router)
router.include_router(admins_router)
router.include_router(blacklist_router)
router.include_router(channels_router)
router.include_router(contests_router)
router.include_router(events_router)
router.include_router(contest_results_router)
router.include_router(contests_active_router)
