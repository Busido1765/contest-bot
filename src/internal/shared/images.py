import os

from aiogram.types import PhotoSize

from bot.base import BOT

from .settings import SETTINGS


async def save_images(images: list[PhotoSize], path_: str = SETTINGS.IMG_FOLDER) -> list[str]:
    paths = []
    for image in images:
        file = await BOT.get_file(image.file_id)
        if file.file_path is None:
            continue
        new_path = os.path.join(path_, file.file_id)
        await BOT.download_file(file.file_path, new_path)
        paths.append(new_path)
    return paths
