from enum import Enum, unique


@unique
class Video(Enum):
    DOUYIN = 'douyin'
    TIKTOK = 'tiktok'
    KUAISHOU = 'kuaishou'
    HUOSHAN = 'houshan'
    XIGUA = 'xigua'
    PIPIXIA = 'pipixia'
