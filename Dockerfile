FROM python:3.8.18-slim

ENV PYTHONUNBUFFERED 1

# 更新pip
RUN pip install --upgrade pip --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 工作目录
WORKDIR /code
ADD . /code

# pip安装依赖包
RUN pip install -r requirements.txt --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 打开容器的8000端口
EXPOSE 8000

# 执行命令行,启动django服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
