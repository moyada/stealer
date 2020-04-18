import json
from enum import Enum, unique


@unique
class Video(Enum):
    DOUYIN = '抖音', 'douyin'
    # TIKTOK = 'TikTok', 'tiktok'
    KUAISHOU = '快手', 'kuaishou'
    HUOSHAN = '火山小视频', 'huoshan'
    XIGUA = ' 西瓜视频', 'xigua'
    PIPIXIA = '皮皮虾', 'pipixia'

    def __new__(cls, *value):
        obj = object.__new__(cls)
        obj.label = value[0]
        obj._value_ = value[1]
        return obj

    def __int__(self):
        return int(self._value_)


video_mapper = {item.value: item for item in Video.__members__.values()}

video_mapper_json = []
for item in Video.__members__.values():
    video_mapper_json.append({
        'label': item.label,
        'value': item.value,
     })
video_mapper_json = json.dumps(video_mapper_json, ensure_ascii=False)
