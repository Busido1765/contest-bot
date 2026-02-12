import asyncio
import celery

from app.contest import ContestApplication
from app.users import AdminApplication

from shared.logging import log
from shared.settings import SETTINGS

from app.factory import AppKind, ApplicationFactory

app_factory = ApplicationFactory()
contest_app: ContestApplication = app_factory.get(AppKind.CONTEST)  # type:ignore
admins_app: AdminApplication = app_factory.get(AppKind.ADMIN)  # type:ignore


BG_APP = celery.Celery(
    broker=SETTINGS.REDIS_BROKER_URI,
    include=["tasks"],
)

BG_APP.conf.update(
    broker_connection_retry_on_startup=True,
    task_always_eager=False,
    result_backend=SETTINGS.REDIS_BROKER_RESULT_BACKEND_URI,
    broker_pool_limit=10_000,
    broker_connection_max_retries=10,
    beat_schedule={
        "check_contests_bg_task": {
            "task": "tasks.check_contests",
            "schedule": SETTINGS.PERIODIC_TASKS_TIMEOUT_SECONDS,  # 10 seconds interval
        },
        "check_blacklist_bg_task": {
            "task": "tasks.check_blacklist",
            "schedule": SETTINGS.PERIODIC_TASKS_TIMEOUT_SECONDS + 1,  # Custom setting
        }
    }
)


@BG_APP.task
def check_contests():
    log.info("start check contests")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        contest_app.check_and_update_contests()
    )


@BG_APP.task
def check_blacklist():
    log.info("start check blacklist")
    admins_app.update_blacklist()
