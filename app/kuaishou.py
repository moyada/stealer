
import re
from django.http import HttpResponse, HttpResponseServerError

from stealer.interface import Service
from stealer.model import Result, ErrorResult
from tools import store, analyzer, http_utils, config
from tools.type import Video

headers = {
    "user-agent": config.user_agent
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": config.user_agent
}


class _DouyinService(Service):

    def fetch(self, url: str, model=0) -> Result:
        """
        获取视频详情
        :param url:
        :param model:
        :return:
        """
        url = analyzer.get_douyin_url(url)
        if url is None:
            return ErrorResult.URL_NOT_FOUNT

        # 请求短链接，获得itemId和dytk
        res = http_utils.get(url, header=headers)
        if http_utils.is_error(res):
            return Result.error(res)

        html = str(res.content)
        item_id = re.findall(r"(?<=itemId:\s\")\d+", html)[0]
        dytk = re.findall(r"(?<=dytk:\s\")(.*?)(?=\")", html)[0]

        # 组装视频长链接
        infourl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + item_id + "&dytk=" + dytk

        # 请求长链接，获取play_addr
        url_res = http_utils.get(infourl, header=headers)
        if http_utils.is_error(url_res):
            return Result.error(url_res)

        vhtml = str(url_res.text)
        uri = re.findall(r'(?<=\"uri\":\")\w{32}(?=\")', vhtml)[0]

        if not uri:
            return Result.failed('fetch play_addr error')

        link = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + uri + \
                "&line=0&ratio=540p&media_type=4&vr_type=0&improve_bitrate=0" \
                "&is_play_url=1&is_support_h265=0&source=PackSourceEnum_PUBLISH"
        result = Result.success(link)

        if model != 0:
            result.ref = res.url
        return result

    def get_index(self, url) -> str:
        index = re.findall(r'(?<=com\/)\w+', url)
        return index[0]

    def download(self, url) -> HttpResponse:
        """
        下载视频
        :param url:
        :return:
        """
        # 检查文件
        index = self.get_index(url)
        file = store.find(Video.DOUYIN, index)
        if file is not None:
            return self.stream(file, index)

        result = self.fetch(url, model=1)
        if not result.is_success():
            return HttpResponseServerError(result.get_data())

        dheaders = download_headers.copy()
        dheaders['referer'] = result.ref

        res = http_utils.get(url=result.get_data(), header=dheaders)
        if http_utils.is_error(res):
            return HttpResponseServerError(str(res))

        store.save(Video.DOUYIN, res, index)
        res.close()

        file = store.find(Video.DOUYIN, index)
        return self.stream(file, index)


INSTANCE = _DouyinService()
