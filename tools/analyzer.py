import re
from typing import Optional

from tools.type import Video


def get_douyin_url(text: str) -> Optional[str]:
    urls = re.findall(r'(?<=douyin.com\/)\w+', text, re.I | re.M)
    if urls:
        return "https://v.douyin.com/" + urls[0]
    return None


def get_huoshan_url(text: str) -> Optional[str]:
    urls = re.findall(r'(?<=com/hotsoon/s\/)\w+', text, re.I | re.M)
    if urls:
        return "https://share.huoshan.com/hotsoon/s/" + urls[0]
    return None


def get_kuaishou_url(text: str) -> Optional[str]:
    urls = re.findall(r'(?<=kuaishou.com\/)\w+', text, re.I | re.M)
    if urls:
        return "http://v.kuaishou.com/" + urls[0]
    return None


def get_pipixia_url(text: str) -> Optional[str]:
    urls = re.findall(r'(?<=h5.pipix.com/s\/)\w+', text, re.I | re.M)
    if urls:
        return "http://h5.pipix.com/s/" + urls[0]
    return None


analyzer_mapper = {
    Video.DOUYIN: get_douyin_url,
    Video.HUOSHAN: get_huoshan_url,
    Video.KUAISHOU: get_kuaishou_url,
    Video.PIPIXIA: get_pipixia_url,
}


def get_url(vtype: Video, text: str) -> Optional[str]:
    func = analyzer_mapper.get(vtype)
    return func(text=text)


if __name__ == '__main__':
    get_url(Video.KUAISHOU, "http://v.kuaishou.com/3ke4p2")