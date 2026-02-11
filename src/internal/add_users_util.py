import asyncio


from app.factory import SQLITE_APP_FACTORY, AppKind
from app.contest import ContestApplication

app: ContestApplication = SQLITE_APP_FACTORY.get(AppKind.CONTEST)  # type: ignore

users = [
    (5298342439, None),
    (5144761988, None),
    (1303778012, None),
    (1228771814, None),
    (5821854779, None),
    (5130852747, None)
]

contest_id = "d8edd5a2-907b-4430-8b2c-8258836dff8a"

for user in users:
    asyncio.run(app.add_to_contest(user[0], user[1], contest_id))
