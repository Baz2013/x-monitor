## 打镜像 ##
* `cd ${PROJECT_HOME}`
* `docker build -t 'x-monitor' .`
* run: `docker run -it -v /var/run/docker.sock:/var/run/docker.sock --rm -p 8888:8888 x-monitor`
* run as daemon: `docker run -d -v /var/run/docker.sock:/var/run/docker.sock -p 8888:8888 --name=mymonitor x-monitor:latest`