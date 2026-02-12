from db.core.sqlite.models.info import Info

from app.contest import ContestApplication

from shared.settings import __desription__, __version__

from .factory import SQLITE_APP_FACTORY, AppKind


class InfoApplication:
    def __init__(self) -> None:
        self._contest_app: ContestApplication = SQLITE_APP_FACTORY.get(AppKind.CONTEST)  # type:ignore

    async def update_version(self):
        try:
            _ = Info.get(Info.bot_version == __version__)
        except:
            Info.delete().execute()
            Info(bot_version=__version__).save(force_insert=True)

            await self._contest_app._notify_admins_about_new_version(__version__, __desription__)
