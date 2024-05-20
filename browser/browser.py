import os
import threading
import json
from playwright.sync_api import sync_playwright, Browser, Playwright
import atexit
from core import config
from tools import http_utils


lock = threading.Lock()

playwright_map = {
}

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

args = [
    f'--user-agent={user_agent}',
    '--no-first-run',
    '--no-default-browser-check',
    '--no-sandbox',
    '--no-zygote',
    '--disable-gpu',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--allow-file-access-from-files',
    '--allow-file-access',
    "--disable-infobars",
    '--disable-blink-features=AutomationControlled'
]

ck_path = '/tmp/dy.json'
cks = [{'name': '', 'value': 'douyin.com', 'domain': 'www.douyin.com', 'path': '/video', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'device_web_cpu_core', 'value': '8', 'domain': 'www.douyin.com', 'path': '/video', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'device_web_memory_size', 'value': '8', 'domain': 'www.douyin.com', 'path': '/video', 'expires': -1, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'ttwid', 'value': '1%7CBaOuINUvKIDzpYaxE9kiGZDiPNvjkCzeq0Opbdl5VIk%7C1716110266%7Ce4314ba7773b6ce02d308eb1d05f0d259aa8fc52a95d8b2c8f417826c9dc2014', 'domain': '.iesdouyin.com', 'path': '/', 'expires': 1747214266.836294, 'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}, {'name': '__ac_nonce', 'value': '06649c3ba0024ddf07136', 'domain': 'www.douyin.com', 'path': '/', 'expires': 1716112066.968196, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': '__ac_signature', 'value': '_02B4Z6wo00f01lokgZAAAIDCmYf-lRRpOWZaBIUAAPDPf6', 'domain': 'www.douyin.com', 'path': '/', 'expires': 1747646267, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'ttwid', 'value': '1%7CuCmgL7j4f44mWkHwC8EJ4iFp3ApyvEaVeaJj9XE8tyQ%7C1716110267%7Cb6317aa1a0cdb8ae5d3ad58d6f36ad7eeef085e8e2fafe0bc721ac7ae944340a', 'domain': '.douyin.com', 'path': '/', 'expires': 1747214267.365654, 'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}, {'name': 'IsDouyinActive', 'value': 'true', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715068.032838, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'home_can_add_dy_2_desktop', 'value': '%220%22', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715068.033804, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'dy_swidth', 'value': '1280', 'domain': 'www.douyin.com', 'path': '/', 'expires': 1716715068, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'dy_sheight', 'value': '720', 'domain': 'www.douyin.com', 'path': '/', 'expires': 1716715068, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'stream_recommend_feed_params', 'value': '%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1280%2C%5C%22screen_height%5C%22%3A720%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715068.038004, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'strategyABtestKey', 'value': '%221716110268.177%22', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715068.17778, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'csrf_session_id', 'value': '5e1f3d33adf5c0883052d57bcfef7c11', 'domain': 'www.douyin.com', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'FORCE_LOGIN', 'value': '%7B%22videoConsumedRemainSeconds%22%3A180%7D', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715068.422286, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 's_v_web_id', 'value': 'verify_lwdbqthk_y54Yk72i_crn9_4nuZ_A7Ep_7maLEOojitjI', 'domain': 'www.douyin.com', 'path': '/', 'expires': 1721294268, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'passport_csrf_token', 'value': '74a651d7ecb7ec478c7b9780e854296f', 'domain': '.douyin.com', 'path': '/', 'expires': 1721294268.496005, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'passport_csrf_token_default', 'value': '74a651d7ecb7ec478c7b9780e854296f', 'domain': '.douyin.com', 'path': '/', 'expires': 1721294268.496039, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'bd_ticket_guard_client_data', 'value': 'eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRktIN3J4cXlUdzErL2tsUG9ReWVuQmpCTVo0SndVMWp5emtZTzNmRGpGQ2lyZ3I2ZFFuMEhjeWFYSWtaZTQxeElMamVvbFZUd1VlcG9tQnMzSHprSWM9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D', 'domain': '.douyin.com', 'path': '/', 'expires': 1721294268.796166, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'bd_ticket_guard_client_web_domain', 'value': '2', 'domain': '.douyin.com', 'path': '/', 'expires': 1721294268.796263, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'msToken', 'value': 'pHD31bx0jhrQmCl2bRjG_k-UN4daiPfOz8z8Ldg0v_BAoaDnuqhEbrwVsTXFFY4pgTAHgtXXeVrjQSrSWrhEO8vj4sNtx31BZNPglZ5c', 'domain': '.douyin.com', 'path': '/', 'expires': 1716715070.120579, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}]

if os.path.exists(ck_path):
    try:
        with open(ck_path, 'r') as file:
            data = file.read()
            cks = json.loads(data)
    except Exception as e:
            print(f"An error occurred: {e}")
else:
    res = http_utils.get('https://cdn.jsdelivr.net/gh/moyada/stealer@master/cookie.json', redirect=False)
    if http_utils.is_error(res) is False:
        try:
            cks = json.loads(res.content)
            with open(ck_path, 'w') as file:
                json.dump(cks, file, indent=4)
        except Exception as e:
                print(f"An error occurred: {e}")



class PageContext:
    browser = None
    context = None
    page = None

    def __init__(self, p: Playwright):
        self.browser = p.chromium.launch(headless=os.environ['headless'] == "1", args=args, timeout=20000)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.context.add_cookies(cks)

    def sync(self):
        try:
            cks = self.context.cookies()
        except Exception as e:
            print(e)
            return
        
        with open(ck_path, 'w') as file:
            json.dump(cks, file, indent=4)


    def close(self):
        self.sync()
        try:
            self.browser.close()
            self.context.close()
            self.page.close()
        except:
            pass


def create_unique_value(func):
    value = None

    def wrapper():
        nonlocal value
        if value is None:
            value = func()
        return value

    return wrapper


def new_page() -> PageContext:
    ct = threading.current_thread()
    pw = playwright_map.get(ct.name)
    if pw is None:
        with lock:
            pw = sync_playwright().start()
            playwright_map[ct.name] = pw
            atexit.register(pw.stop)

    return PageContext(pw)


# def get() -> Browser | None:
#     with sync_playwright() as p:
#         b = p.chromium.launch(headless=True)
#         return b
#     return None

