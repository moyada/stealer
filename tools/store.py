import os

from requests import Response

from tools import terminal
from tools.type import Video

base_path = os.getcwd() + "/video/"


def find(vtype: Video, index: str) -> object:
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
    print(terminal.run_cmd('sh video/remd5.sh ' + filename))
