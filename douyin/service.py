import re
import requests
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseServerError, FileResponse

from tools import store
from tools.type import Video

headers = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
}

download_headers = {
    "accept": "*/*",
    "accept-encoding": "identity;q=1, *;q=0",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6,de;q=0.5,fr;q=0.4,ca;q=0.3,ga;q=0.2",
    "range": "bytes=0-",
    "referer": "https://www.iesdouyin.com/share/video/6810212113966025991/?region=CN&mid=6806868603829225474&u_code=4bbc2hgjj56e&titleType=title&utm_source=copy_link&utm_campaign=client_share&utm_medium=android&app=aweme",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-sit",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
}


def get_url(text) -> str:
    urls = re.findall(r'(?<=douyin.com\/)\w+\/', text, re.I | re.M)
    if urls:
        return "https://v.douyin.com/" + urls[0]
    return ''


def get_download(url) -> str:
    """
    获取视频详情
    :param url:
    :return:
    """
    # 请求短链接，获得itemId和dytk
    try:
        get = requests.get(url, headers=headers)
    except:
        return ""

    if get.status_code != 200:
        return ""

    print(get.url)
    html = get.content
    # print(html)
    itemId = re.findall(r"(?<=itemId:\s\")\d+", str(html))
    # print(itemId[0])
    dytk = re.findall(r"(?<=dytk:\s\")(.*?)(?=\")", str(html))
    # print(dytk[0])

    # 组装视频长链接
    infourl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + itemId[0] + "&dytk=" + dytk[0]

    print(infourl)
    # 请求长链接，获取play_addr
    videoopen = requests.get(infourl, headers=headers)
    vhtml = videoopen.text
    # print(vhtml)
    uri = re.findall(r'(?<=\"uri\":\")\w{32}(?=\")', str(vhtml))

    if uri:
        return "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + uri[0] + \
                "&line=0&ratio=540p&media_type=4&vr_type=0&improve_bitrate=0" \
                "&is_play_url=1&is_support_h265=0&source=PackSourceEnum_PUBLISH"
    return ""


def get_index(url) -> str:
    index = re.findall(r'(?<=com\/)\w+\/', url)
    index = index[0].replace('/', '')
    return index


def download(url) -> HttpResponse:
    """
    下载视频
    :param url:
    :return:
    """
    # 检查文件
    index = get_index(url)
    file = store.find(Video.DOUYIN, index)
    if file is not None:
        return stream(file, index)

    # 请求短链接，获得itemId和dytk
    try:
        referer = requests.get(url, headers=headers)
    except:
        return HttpResponseServerError()

    if referer.status_code != 200:
        return HttpResponseServerError()

    html = referer.content
    # print(html)
    itemId = re.findall(r"(?<=itemId:\s\")\d+", str(html))
    # print(itemId[0])
    dytk = re.findall(r"(?<=dytk:\s\")(.*?)(?=\")", str(html))
    # print(dytk[0])

    # 组装视频长链接
    infourl = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + itemId[0] + "&dytk=" + dytk[0]
    referer.close()

    # 请求长链接，获取play_addr
    videoopen = requests.get(infourl, headers=headers)
    vhtml = videoopen.text
    # print(vhtml)
    uri = re.findall(r'(?<=\"uri\":\")\w{32}(?=\")', str(vhtml))

    if not uri:
        return HttpResponseServerError()

    play_addr = "https://aweme.snssdk.com/aweme/v1/play/?video_id=" + uri[0] + \
           "&line=0&ratio=540p&media_type=4&vr_type=0&improve_bitrate=0" \
           "&is_play_url=1&is_support_h265=0&source=PackSourceEnum_PUBLISH"

    dheaders = download_headers.copy()
    dheaders['referer'] = referer.url

    res = requests.get(url=play_addr, headers=dheaders)
    store.save(Video.DOUYIN, res, index)
    res.close()

    file = store.find(Video.DOUYIN, index)
    return stream(file, index)


def stream(file, index) -> HttpResponse:
    try:
        # 设置响应头
        # StreamingHttpResponse将文件内容进行流式传输，数据量大可以用这个方法
        response = FileResponse(file)
        # 以流的形式下载文件,这样可以实现任意格式的文件下载
        response['Content-Type'] = 'application/octet-stream'
        # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(index + '.mp4')
    except Exception as e:
        response = HttpResponse(e)

    return response