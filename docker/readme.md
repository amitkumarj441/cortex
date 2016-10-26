# Docker file for Cortex 

## How to setup cortex dev env in local machine

```
docker pull worldbrain/cortex
docker run -it --net=host --name=cortex worldbrain/cortex
```
## What's Happening 

* Docker image of cortex is pulled from docker hub
* Docker container start with 8000 post mapped between the host and container
