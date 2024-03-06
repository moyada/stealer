import time
from playwright.sync_api import Request, Response
from browser import browser
from core import config
import urllib.parse


class DouyinHandler:

    data = None

    @classmethod
    def get_info(cls, url: str) -> any:
        p = browser.new_page()

        # p.page.on("response", lambda response: print("<<", response.status, response.url))
        p.page.on("response", cls.handle_request)

        try:
            p.page.goto(url, timeout=10000)
            p.page.wait_for_timeout(2000)
        except:
            pass

        for i in range(0, config.page_wait, 100):
            if cls.data is not None:
                break
            try:
                p.page.wait_for_timeout(100)
            except:
                break

        path = get_path(p.page.url)
        p.close()

        if path == "/":
            cls.data = None
            return None

        # /note/7264601120775916855

        data = cls.data
        cls.data = None
        return data

    @classmethod
    def handle_request(cls, req: Response) -> any:
        # if req.url.startswith("https://www.douyin.com/") is False:
        #     return
        #
        # print(req.url)
        #     https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7293074028649139508&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1280&screen_height=720&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=120.0.0.0&browser_online=true&engine_name=Blink&engine_version=120.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7319378131268634164&msToken=&X-Bogus=DFSzswRYWBiANV18t7UNHQIm4L7J
        if req.url.startswith("https://www.douyin.com/aweme/v1/web/aweme/detail") is False:
            return
        # print(req.url)
        if req.status != 200:
            return

        try:
            cls.data = req.json()
        except:
            pass


def get_path(url) -> str:
    try:
        result = urllib.parse.urlparse(url).path
        if result == "":
            return None
        return result
    except ValueError:
        return None
