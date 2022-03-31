import io
import os
import logging
import zipfile
from typing import List

from django.http import HttpResponseServerError
from requests import Response

from tools import terminal, system, http_utils
from core.type import Video


logger = logging.getLogger(__name__)
base_path = os.getcwd() + "/video/"


def find(vtype: Video, index: str, extra: str) -> (io.open, str):
    if index is None:
        return None, None
    filename = get_name(vtype, index)
    if os.path.exists(filename + extra):
        return open(filename + extra, 'rb'), index+extra

    if (vtype == Video.DOUYIN or vtype == Video.KUAISHOU) and os.path.exists(filename + ".zip"):
        return open(filename + ".zip", 'rb'), index + ".zip"
    return None, None


def get_name(vtype: Video, index: str) -> str:
    path = base_path + vtype.value
    if not os.path.exists(path):
        os.mkdir(path)
    return base_path + vtype.value + "/" + index


def save(vtype: Video, res: Response, index: str, extra: str):
    filename = get_name(vtype, index) + extra
    with open(filename, 'wb')as file:
        file.write(res.content)
        file.close()

    if system.is_mac():
        command = 'md5 -q'
    else:
        command = 'md5sum'
    logger.info(terminal.run_cmd('sh video/remd5.sh {} {}'.format(command, filename)))


def save_image(vtype: Video, images: List[str], index: str):
    filename = get_name(vtype, index) + ".zip"
    with zipfile.ZipFile(filename, 'w') as imgZip:
        index = 1
        for image in images:
            res = http_utils.get(url=image)
            if http_utils.is_error(res):
                return HttpResponseServerError(str(res))
            # res.headers.get('content-type')
            imgZip.writestr(f"{index}.jpg", res.content)
            index += 1
    return None