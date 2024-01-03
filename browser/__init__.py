# playwright install chrome
# from playwright.sync_api import sync_playwright, Browser
# import atexit


# playwright = sync_playwright().start()
# atexit.register(playwright.stop)

# BROWSER = Browser


# pl = sync_playwright().start()
# pl.chromium.launch(headless=False)
# print("start")
# with sync_playwright() as p:
#     print("startb")
#     BROWSER = p.chromium.launch(headless=True)


# def close():
#     if BROWSER is None:
#         return
#
#     try:
#         BROWSER.close()
#     except:
#         pass

# 注册 exit_function 方法，在程序退出时执行
# atexit.register(close)
