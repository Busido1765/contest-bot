from .settings import SETTINGS


def generate_miniapp_participate_link(contest_id: str, bot_name: str | None = None) -> str:
    target_bot_name = bot_name or SETTINGS.BOT_NAME
    return f"https://t.me/{target_bot_name}/{SETTINGS.BOT_WEBAPP_NAME}?startapp={contest_id}"
