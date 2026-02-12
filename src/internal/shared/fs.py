import os

from .settings import ROOT_PROJECT_DIR


def prepare_folders():
    db_folder = ROOT_PROJECT_DIR / "db"
    static_folder = ROOT_PROJECT_DIR / "static"

    if not os.path.exists(db_folder):
        os.mkdir(db_folder)
    if not os.path.exists(static_folder):
        os.mkdir(static_folder)
