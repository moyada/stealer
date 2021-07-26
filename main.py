from flask import Flask, render_template, redirect, url_for
from flask import jsonify
from flask_cors import CORS

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
    app.run(host="localhost", port=8000, debug=True)
