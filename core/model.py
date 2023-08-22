import time
from enum import unique, Enum

from core.type import Video


class Info:
    def __init__(self, platform: Video):
        self.expired = int(time.time())+10 * 60
        self.platform = platform
        self.filename = None
        self.cover = ''
        self.desc = ''
        self.video = ''
        self.images = []
        self.extra = None

    @property
    def ref(self):
        return self.desc

    @ref.setter
    def ref(self, value):
        self.desc = value

    @property
    def ref(self):
        return self.cover

    @ref.setter
    def ref(self, value):
        self.cover = value

    def to_dict(self) -> dict:
        _dict = {
            'cover': self.cover,
            'desc': self.desc,
        }
        return _dict


class Extra:
    def __init__(self, videos: any, audios: any):
        self.videos = videos
        self.audios = audios

    @property
    def ref(self):
        return self.videos

    @ref.setter
    def ref(self, value):
        self.videos = value

    @property
    def ref(self):
        return self.audios

    @ref.setter
    def ref(self, value):
        self.audios = value


class Result:

    def __init__(self, success: bool, data):
        self._success = success
        self._data = data
        self._extra = ".mp4"
        self._type = 0

    def is_success(self):
        return self._success

    def get_data(self):
        return self._data

    def is_image(self):
        return self._type != 0

    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        self._ref = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value):
        self._extra = value

    @staticmethod
    def success(data):
        return Result(True, data=data)

    @staticmethod
    def failed(msg):
        return Result(False, data=msg)

    @staticmethod
    def error(err: Exception):
        return Result(False, data=str(err))


@unique
class ErrorResult(Result, Enum):
    TOO_MANY_OPERATE = False, 'too many operate.'
    URL_NOT_PRESENT = False, 'url is not present.'
    TYPE_NOT_PRESENT = False, 'type is not present.'
    MAPPER_NOT_EXIST = False, 'type mapper not exist.'
    URL_NOT_INCORRECT = False, '分享地址有误'
    VIDEO_INFO_ERROR = False, '作品信息错误'
    VIDEO_INFO_NOT_FOUNT = False, '作品获取失败'
    VIDEO_ADDRESS_NOT_FOUNT = False, '视频地址获取失败'

    def __init__(self, *value):
        super(self.__class__, self).__init__(success=value[0], data=value[1])
        # super(Enum, self).__init__()

