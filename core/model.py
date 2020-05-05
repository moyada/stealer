from enum import unique, Enum


class Result:

    def __init__(self, success: bool, data):
        self._success = success
        self._data = data

    def is_success(self):
        return self._success

    def get_data(self):
        return self._data

    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self, value):
        self._ref = value

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
    URL_NOT_INCORRECT = False, '分享地址有误.'
    VIDEO_ADDRESS_NOT_FOUNT = False, '视频地址获取失败.'

    def __init__(self, *value):
        super(self.__class__, self).__init__(success=value[0], data=value[1])
        # super(Enum, self).__init__()

