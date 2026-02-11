import asyncio

from app.contest import ContestApplication
from app.users import AdminApplication

from shared.logging import log

from app.factory import AppKind, ApplicationFactory

from apscheduler.schedulers.background import BackgroundScheduler

app_factory = ApplicationFactory()
contest_app: ContestApplication = app_factory.get(AppKind.CONTEST)  # type:ignore
admins_app: AdminApplication = app_factory.get(AppKind.ADMIN)  # type:ignore


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def check_contests():
    log.info("start check contests")
    loop.run_until_complete(
        contest_app.check_and_update_contests()
    )


def check_blacklist():
    log.info("start check blacklist")
    admins_app.update_blacklist()


scheduler = BackgroundScheduler()
scheduler.add_job(check_contests, "interval", seconds=10)
scheduler.add_job(check_blacklist, "interval", seconds=11)
