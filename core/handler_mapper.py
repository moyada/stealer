from typing import Type

from service import *
from core.interface import Service
from core.type import Video

service_mapper = {
    Video.DOUYIN: douyin.DouyinService,
    Video.KUAISHOU: kuaishou.KuaishouService,
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
