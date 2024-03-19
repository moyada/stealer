import os
import threading

from playwright.sync_api import sync_playwright, Browser, Playwright
import atexit
from core import config


# from browser import playwright
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


class PageContext:
    browser = None
    context = None
    page = None

    def __init__(self, p: Playwright):
        self.browser = p.chromium.launch(headless=os.environ['headless'] == "1", args=args, timeout=20000)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def close(self):
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

