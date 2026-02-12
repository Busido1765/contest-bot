from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.factory import SQLITE_APP_FACTORY, AppKind
from app.contest import ContestApplication

from shared.logging import log


api = FastAPI()


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/api/contest/participate")
async def participate_in_contes(contest_id: str, nickname: str, user_tg_id: int):
    app: ContestApplication = SQLITE_APP_FACTORY.get(AppKind.CONTEST)  # type:ignore

    try:
        status = await app.participate_in_contest(user_tg_id, nickname, contest_id)
    except Exception as err:
        log.error("Unable to participate in contest:", err)
        return JSONResponse({"message": str(err), "status_code": 500, "contest_status": -1}, 500)

    return JSONResponse({"message": "ok", "status_code": 200, "contest_status": status}, 200)
