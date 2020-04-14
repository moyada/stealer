import re
from typing import Optional


def get_douyin_url(text: str) -> Optional[str]:
    urls = re.findall(r'(?<=douyin.com\/)\w+\/', text, re.I | re.M)
    if urls:
        return "https://v.douyin.com/" + urls[0]
    return None
