
抖音、快手、皮皮虾、火山视频。。。去水印程序 

项目使用 `python3` + `Vue` 开发，安装所需依赖:

`pip install -r requirements.txt --index-url https://pypi.douban.com/simple`
OR
```shell script
pip install Django
pip install requests
pip install enum34
pip install django-cors-headers
```

下载解压完运行 `start.sh` 或 `run.sh`，通过浏览器打开 [localhost:8000](http://localhost:8000) 进入使用页面。

- 点击`下载`直接下载视频 (经过 md5 处理)
- 点击`解析`获取下载地址


[~~试用地址~~](http://127.0.0.01:8000/#/) 暂无空余服务器可用 

### Docker 方式部署

1. 构建镜像，拉取镜像 `docker pull xueyikang/stealer:1.1.0`
2. 给拉取的镜像打tag `docker tag xueyikang/stealer:1.1.0 stealer:1.1.0` 
3. 启动容器，执行命令 `docker run -d -p 8000:8000 stealer:1.1.0`, 应用地址为：127.0.0.1:8000


### 直接使用最新的镜像

```bash
docker pull xueyikang/stealer
docker run -itd --name stealer -p 8000:8000 xueyikang/stealer
```

### 
