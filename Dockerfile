FROM python:3.6.8

ENV PYTHONUNBUFFERED 1

# 更新pip
RUN pip install --upgrade pip --index-url https://pypi.douban.com/simple

# 工作目录
WORKDIR /code
ADD . /code

# pip安装依赖包
RUN pip install -r requirements.txt --index-url https://pypi.douban.com/simple

# 打开容器的8000端口
EXPOSE 8000

# 执行命令行,启动django服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]