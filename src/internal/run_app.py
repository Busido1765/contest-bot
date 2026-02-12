import uvicorn


from shared.fs import prepare_folders
from shared.settings import SETTINGS


if __name__ == "__main__":
    prepare_folders()
    uvicorn.run(
        "api.main:api",
        port=8000,
        host="localhost",
        reload=SETTINGS.API_RELOAD,
    )
