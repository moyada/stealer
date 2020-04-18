import schedule
import logging

# 生成一个以当前文件名为名字的logger实例
logger = logging.getLogger(__name__)
collect_logger = logging.getLogger("collect")

invoke_counter = {
}


def do_clear():
    logger.info('Run clear filter job.')
    invoke_counter.clear()


def init_job():
    logger.info('Init clear filter job.')
    schedule.every().day.at("00:00").do(do_clear, 'clear filter')


def get_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_filter(request) -> bool:
    ip = get_ip(request)
    collect_logger.info('request ip >>> {}'.format(ip))
    val = invoke_counter.get(ip)
    if val is None:
        invoke_counter[ip] = 1
        return False
    if val > 3:
        return True
    invoke_counter[ip] = val + 1
    return False


init_job()
