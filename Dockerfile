FROM python:3.8.18-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update &&  \
    apt-get upgrade -y &&  \
    apt-get install -y gcc &&  \
    apt-get install -y ffmpeg &&  \
    apt-get install -y libnss3 &&  \
    apt-get install -y libnspr4 &&  \
    apt-get install -y libatk1.0-0 &&  \
    apt-get install -y libatk-bridge2.0-0 &&  \
    apt-get install -y libcups2 &&  \
    apt-get install -y libatspi2.0-0 &&  \
    apt-get install -y libxcomposite1 &&  \
    apt-get install -y libxdamage1

# 更新pip
RUN pip install --upgrade pip --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 工作目录
WORKDIR /app
ADD . /app

# pip安装依赖包
RUN pip install -r requirements.txt --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

RUN playwright install chromium

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 打开容器的8000端口
EXPOSE 8000

# 执行命令行,启动django服务
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
