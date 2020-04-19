import os
import logging
from requests import Response

from tools import terminal, system
from core.type import Video


logger = logging.getLogger(__name__)
base_path = os.getcwd() + "/video/"


def find(vtype: Video, index: str) -> object:
    if index is None:
        return None
    filename = get_name(vtype, index)
    if not os.path.exists(filename):
        return None
    return open(filename, 'rb')


def get_name(vtype: Video, index: str) -> str:
    path = base_path + vtype.value
    if not os.path.exists(path):
        os.mkdir(path)
    return base_path + vtype.value + "/" + index + ".mp4"


def save(vtype: Video, res: Response, index: str):
    filename = get_name(vtype, index)
    with open(filename, 'wb')as file:
        file.write(res.content)
        file.close()

    if system.is_mac():
        command = 'md5 -q'
    else:
        command = 'md5sum'
    logger.info(terminal.run_cmd('sh video/remd5.sh {} {}'.format(command, filename)))
