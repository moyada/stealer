import time
from typing import Optional

from core.model import Info

cacheMap = {}


def save(key: str, value: Info):
    cacheMap[key] = value


def get(key: str) -> Optional[Info]:
    if key not in cacheMap:
        return None
    info = cacheMap[key]
    if info.expired < int(time.time()):
        cacheMap.pop(key)
        return None
    return info

