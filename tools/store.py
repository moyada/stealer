import io
import os
import logging
import zipfile
import hashlib
from typing import List

from django.http import HttpResponseServerError
from requests import Response

from core import config
from tools import terminal, system, http_utils
from core.type import Video

logger = logging.getLogger(__name__)


def get_token(vtype: Video, url: str) -> str:
    return str(vtype.value) + hashlib.md5(url.encode()).hexdigest()


def make_path(sub: str, index: str) -> str:
    path = config.base_path + sub
    if not os.path.exists(path):
        os.makedirs(path)
    return config.base_path + sub + "/" + index


def find_file(vtype: Video, filename: str) -> io.open:
    filename = make_path(vtype.value, filename)
    if os.path.exists(filename):
        return open(filename, 'rb')
    return None


def save_file(vtype: Video, res: Response, filename: str):
    filename = make_path(vtype.value, filename)
    with open(filename, 'wb') as file:
        file.write(res.content)
        file.close()


def find(vtype: Video, index: str, extra: str) -> (io.open, str):
    if index is None:
        return None, None
    filename = make_path(vtype.value, index)
    if os.path.exists(filename + extra):
        return open(filename + extra, 'rb'), index + extra

    if (vtype == Video.DOUYIN or vtype == Video.KUAISHOU) and os.path.exists(filename + ".zip"):
        return open(filename + ".zip", 'rb'), index + ".zip"
    return None, filename


def save_image(vtype: Video, images: List[str], filename: str):
    filename = make_path(vtype.value, filename)
    with zipfile.ZipFile(filename, 'w') as imgZip:
        index = 1
        for image in images:
            res = http_utils.get(url=image)
            if http_utils.is_error(res):
                return HttpResponseServerError(str(res))
            # res.headers.get('content-type')
            imgZip.writestr(f"{index}.jpg", res.content)
            index = index + 1


def save(vtype: Video, res: Response, index: str, extra: str) -> str:
    filename = make_path(vtype.value, index) + extra
    with open(filename, 'wb') as file:
        file.write(res.content)
        file.close()

    return filename
    # if system.is_mac():
    #     command = 'md5 -q'
    # else:
    #     command = 'md5sum'
    # logger.info(terminal.run_cmd('sh video/remd5.sh {} {}'.format(command, filename)))
