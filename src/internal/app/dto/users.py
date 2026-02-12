from typing import Optional

from pydantic import BaseModel

from shared.types import UnixTimestamp
from shared.uids import get_id


class UserCreate(BaseModel):
    tg_id: int
    nickname: str

class UserUpdate(UserCreate):
    pass


class UserGet(UserCreate):
    id: str


class AdminCreate(BaseModel):
    phone_number: int
    tg_id: int


class AdminUpdate(AdminCreate):
    pass


class AdminGet(AdminCreate):
    id: str


class BlackListRecordCreate(BaseModel):
    telegram_id: int
    nickname: Optional[str] = None  # Allow None values
    added_at: UnixTimestamp
    days_of_blacklist: int = 0


class BlackListRecordGet(BlackListRecordCreate):
    id: str
