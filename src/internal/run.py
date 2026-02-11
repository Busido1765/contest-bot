import asyncio

from aiogram.types import BotCommand

from bot.base import DISPATCHER, BOT
from bot.handlers import router

from db.core.sqlite.utils import prepare_db

from app.info import InfoApplication

from shared.fs import prepare_folders
from shared.exceptions import handle
from shared.logging import log


@handle
async def main():
    log.debug("bot started")

    await InfoApplication().update_version()

    await BOT.set_my_commands([
        BotCommand(command="/start", description="start bot")
    ])
    DISPATCHER.include_router(router)
    await DISPATCHER.start_polling(BOT)


if __name__ == "__main__":
    prepare_folders()
    prepare_db()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("bot stopped")
