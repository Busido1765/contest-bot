from .settings import SETTINGS


def generate_miniapp_participate_link(contest_id: str):
    path = "JoinLot"
    return f"https://t.me/{SETTINGS.BOT_NAME}/{path}?startapp={contest_id}" # &startApp={contest_id}"
