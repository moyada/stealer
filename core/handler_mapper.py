from typing import Type

from service import *
from core.interface import Service
from core.type import Video
from service import tiktok

service_mapper = {
    Video.TIKTOK: tiktok.TiktokService,
    Video.DOUYIN: douyin.DouyinService,
    Video.KUAISHOU: kuaishou.KuaishouService,
    Video.HUOSHAN: huoshan.HuoshanService,
    Video.XIGUA: xigua.XiguaService,
    Video.PIPIXIA: pipixia.PipixiaService,
    Video.BILIBILI: bilibili.BiliBiliService,
    Video.BANGUMI: bangumi.BangumiService,
}


def get_service(xtype: Video) -> Type[Service]:
    service = service_mapper.get(xtype)
    if service is None:
        raise ModuleNotFoundError('Not match route, type ' + xtype.label)
    return service
