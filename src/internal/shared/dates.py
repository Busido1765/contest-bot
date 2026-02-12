import time
from datetime import datetime

from .types import UnixTimestamp


def now(timezone: int = 0) -> UnixTimestamp:
    time_ts = int(time.mktime(time.gmtime()))
    return time_ts + timezone*HOUR(1)


def dt_to_timestamp(dt: datetime) -> UnixTimestamp:
    return int(time.mktime(dt.timetuple()))


def timestamp_to_dt(timestamp: int) -> datetime:
    try:
        return datetime.fromtimestamp(timestamp)
    except:
        raise ValueError(f"Invalid timestamp value: '{timestamp}'")


HOUR = lambda s: s*3600
MINUTE = lambda s: s*60
