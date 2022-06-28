import json
from enum import Enum, unique


@unique
class Video(Enum):
    AUTO = '自动适配', 'auto', True
    DOUYIN = '抖音', 'douyin', True
    TIKTOK = 'TikTok', 'tiktok', False
    KUAISHOU = '快手', 'kuaishou', True
    HUOSHAN = '火山小视频', 'huoshan', True
    XIGUA = ' 西瓜视频', 'xigua', False
    PIPIXIA = '皮皮虾', 'pipixia', True
    BILIBILI = '哔哩哔哩', 'bilibili', True
    BANGUMI = '哔哩哔哩番剧', 'bangumi', True

    def __new__(cls, *value):
        obj = object.__new__(cls)
        obj.label = value[0]
        obj._value_ = value[1]
        obj.enable = value[2]
        return obj

    def __int__(self):
        return int(self._value_)


video_mapper = {item.value: item for item in Video.__members__.values() if item.enable}

video_mapper_json = []
for item in Video.__members__.values():
    if not item.enable:
        continue
    video_mapper_json.append({
        'label': item.label,
        'value': item.value,
     })
video_mapper_json = json.dumps(video_mapper_json, ensure_ascii=False)
