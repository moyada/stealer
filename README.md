# Sealer

[![Docker workflow](https://img.shields.io/github/actions/workflow/status/moyada/stealer/docker-image.yml?logo=github)](https://img.shields.io/github/actions/workflow/status/moyada/stealer/docker-image.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/xueyikang/stealer.svg?logo=docker)](https://hub.docker.com/r/xueyikang/stealer/)

抖音、快手、BiliBili、皮皮虾。。。去水印程序 

> 💡出现解析失败可在 issue 中提问，请提供可用于复现的`平台信息`、`分享链接`

## 应用部署

```shell
# git clone
git clone https://github.com/moyada/stealer
cd stealer

# install python dependencies
pip3 install -r requirements.txt
playwright install chromium
```

### 配置 `core/config.py`，

```python
# 下载高清b站视频
bilibili_cookie = "xxxx"
```
> ⚠️ 注意：下载bilibili视频会需要使用 `ffmpeg` 合成，下载耗时较久

```shell
python3 manage.py runserver 0.0.0.0:8000
```

下载解压完运行 `start.sh` 或 `run.sh`，通过浏览器打开 [localhost:8000](http://localhost:8000) 进入使用页面。

- 点击`解析`获取视频信息
- 点击`下载`直接下载视频

[~~试用地址~~](http://127.0.0.01:8000/#/) 

## Docker 方式部署

```shell
docker stop -t 300 stealer
docker rm -f stealer

docker pull xueyikang/stealer

mkdir -p stealer-logs
docker run -d --name stealer -p 8000:8000 -v `pwd`/stealer-logs:/app/logs -e BILIBILI_COOKIE= --restart=always xueyikang/stealer:latest
```