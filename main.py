import re
import time
from urllib import parse

from flask import Flask, render_template, redirect, url_for
from flask import jsonify
from flask_cors import CORS
from past.builtins import unicode

from core import type
from route import controller

app = Flask(
    __name__, static_folder="appfront/dist/static", template_folder="appfront/dist")
CORS(app)


@app.get('/')
def home():
    '''
        当在浏览器访问网址时，通过 render_template 方法渲染 dist 文件夹中的 index.html。
        页面之间的跳转交给前端路由负责，后端不用再写大量的路由
    '''
    return render_template('index.html')


@app.get('/index')
def index():
    redirect('/', code=302)


# @app.handle_exception(500)
# def error():
#     redirect('/', code=302)


# 启动运行
if __name__ == '__main__':
    a = int(time.time())+10 * 60
    print(a)
    print(time.time())

    text1 = "<script id=\"RENDER_DATA\" type=\"application/json\">%7B%22_location%22%3A%22%2Fshare%2Fvideo%2F7169791080395754788%2F%3Fregion%3DCN%26mid%3D7169791120413969160%26u_code%3D4bbc2hgjj56e%26did%3DMS4wLjABAAAAMXYfVrcs_hSHU1eDB-vwjYggYdsjK7OaxIJOYhmRnIg%26iid%3DMS4wLjABAAAAoJd5fKpA7Gm8BgDLbBs23RuCQPkgs7qWEolBH82m3pwptFweVFsdliUDAxujN_ye%26with_sec_did%3D1%26titleType%3Dtitle%26from_ssr%3D1%26utm_source%3Dcopy%26utm_campaign%3Dclient_share%26utm_medium%3Dandroid%26app%3Daweme%22%2C%22app%22%3A%7B%22ua%22%3A%22Mozilla%2F5.0%20(iPhone%3B%20CPU%20iPhone%20OS%2013_2_3%20like%20Mac%20OS%20X)%20AppleWebKit%2F605.1.15%20(KHTML%2C%20like%20Gecko)%20Version%2F13.0.3%20Mobile%2F15E148%20Safari%2F604.1%22%2C%22isSpider%22%3Afalse%2C%22webId%22%3A%227179993625471305273%22%2C%22query%22%3A%7B%22region%22%3A%22CN%22%2C%22mid%22%3A%227169791120413969160%22%2C%22u_code%22%3A%224bbc2hgjj56e%22%2C%22did%22%3A%22MS4wLjABAAAAMXYfVrcs_hSHU1eDB-vwjYggYdsjK7OaxIJOYhmRnIg%22%2C%22iid%22%3A%22MS4wLjABAAAAoJd5fKpA7Gm8BgDLbBs23RuCQPkgs7qWEolBH82m3pwptFweVFsdliUDAxujN_ye%22%2C%22with_sec_did%22%3A%221%22%2C%22titleType%22%3A%22title%22%2C%22from_ssr%22%3A%221%22%2C%22utm_source%22%3A%22copy%22%2C%22utm_campaign%22%3A%22client_share%22%2C%22utm_medium%22%3A%22android%22%2C%22app%22%3A%22aweme%22%7D%2C%22renderInSSR%22%3A1%2C%22lastPath%22%3A%227169791080395754788%22%2C%22appName%22%3A%22safari%22%2C%22host%22%3A%22www.iesdouyin.com%22%2C%22isNotSupportWebp%22%3Atrue%2C%22commonContext%22%3A%7B%22ua%22%3A%22Mozilla%2F5.0%20(iPhone%3B%20CPU%20iPhone%20OS%2013_2_3%20like%20Mac%20OS%20X)%20AppleWebKit%2F605.1.15%20(KHTML%2C%20like%20Gecko)%20Version%2F13.0.3%20Mobile%2F15E148%20Safari%2F604.1%22%2C%22isSpider%22%3Afalse%2C%22webId%22%3A%227179993625471305273%22%2C%22renderInSSR%22%3A1%2C%22lastPath%22%3A%227169791080395754788%22%2C%22appName%22%3A%22safari%22%2C%22host%22%3A%22www.iesdouyin.com%22%2C%22isNotSupportWebp%22%3Atrue%7D%2C%22videoInfoRes%22%3A%7B%22item_list%22%3A%5B%7B%22aweme_id%22%3A%227169791080395754788%22%2C%22desc%22%3A%22%E8%BF%98%E5%BE%97%E6%98%AF%E6%B3%BD%E6%B3%95%E8%80%81%E5%B8%88dxf%E4%B9%9F%E6%B0%94%E5%9C%BA%E5%8D%81%E8%B6%B3%23%E6%B5%B7%E8%B4%BC%E7%8E%8B%20%23%E7%94%B7%E5%AD%A9%E5%AD%90%E8%8A%B1%E7%82%B9%E9%92%B1%E6%80%8E%E4%B9%88%E4%BA%86%20%23%E6%B5%B7%E8%B4%BC%E7%8E%8B%E6%89%8B%E5%8A%9E%20%23%E6%89%8B%E5%8A%9E%E5%BC%80%E7%AE%B1%20%23%E6%B5%B7%E8%B4%BC%22%2C%22create_time%22%3A1669347081%2C%22author%22%3A%7B%22uid%22%3A%222577669873474023%22%2C%22short_id%22%3A%2242990682995%22%2C%22nickname%22%3A%22%E7%8C%AA%E7%8C%AA%E9%AD%94%E7%8E%A9%22%2C%22signature%22%3A%22%E6%AD%A3%E7%89%88%E9%87%91%E7%8C%AB%E5%8D%96%E5%AE%B6%EF%BD%9E%E4%BF%9D%E8%B4%A8%E5%8F%88%E4%BF%9D%E4%BB%B7%EF%BC%81%5Cn%E6%AF%8F%E5%A4%A915%3A00-17%3A00%EF%BC%8C18%3A00-22%3A30%E7%9B%B4%E6%92%AD%E5%88%86%E4%BA%AB%E6%AD%A3%E7%89%88%E9%87%91%E7%8C%AB%E6%89%8B%E5%8A%9E%5Cn%E6%AC%A2%E8%BF%8E%E5%A4%A7%E5%AE%B6%E6%9D%A5%E7%9B%B4%E6%92%AD%E9%97%B4%E7%8E%A9%E8%80%8D%EF%BC%8CSalute%EF%BC%81%5Cn%E5%BA%97%E9%93%BA%E8%90%A5%E4%B8%9A%E6%97%B6%E9%97%B410%3A00-23%3A00%22%2C%22avatar_larger%22%3A%7B%22uri%22%3A%221080x1080%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf%22%2C%22url_list%22%3A%5B%22https%3A%2F%2Fp26.douyinpic.com%2Faweme%2F1080x1080%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf.jpeg%3Ffrom%3D116350172%22%2C%22https%3A%2F%2Fp3.douyinpic.com%2Faweme%2F1080x1080%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf.jpeg%3Ffrom%3D116350172%22%2C%22https%3A%2F%2Fp11.douyinpic.com%2Faweme%2F1080x1080%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf.jpeg%3Ffrom%3D116350172%22%5D%7D%2C%22avatar_thumb%22%3A%7B%22uri%22%3A%22100x100%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf%22%2C%22url_list%22%3A%5B%22https%3A%2F%2Fp6.douyinpic.com%2Faweme%2F100x100%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf.jpeg%3Ffrom%3D116350172%22%2C%22https%3A%2F%2Fp26.douyinpic.com%2Faweme%2F100x100%2Faweme-avatar%2Ftos-cn-avt-0015_4cc481b6214bde92c76d7327f87f2dcf.jpeg%3Ffrom%3D116350172%22%2C%22https%3A%2F%2Fp11.douyinpic.com%2Faweme%2F100x100%2Faweme-avatar</script>"
    text2 = "<script id=\"RENDER_DATA\" type=\"application/json\">aweme-avatar</script>"
    data = re.findall(r'(?<=<script id=\"RENDER_DATA\" type=\"application\/json\">)(.*?)(?=<\/script>)', text1)
    d = parse.unquote(data[0])
    print(d)
    # app.run(host="localhost", port=8000, debug=True)
