from typing import Callable, Union
from log4py import logging
from fastapi import FastAPI
from mctech_discovery.discovery import discovery_client, configure
from mctech_core import tracing
from . import middlewares

log = logging.getLogger('python.cloud.appServer')


def init_app_manager():
    # log.info('开始初始化各部分组件......')
    # #  配置合并完成，开始触发执行延迟初始化事件
    # #  @ts-expect-error 未暴露方法
    # appManager.onIniting(configure)
    # log.info('组件初始化完成！')
    pass


class AppServer:
    def __init__(self):
        self._app = FastAPI()

    @property
    def app(self):
        return self._app

    def _init(self):
        middlewares.create_actuator(configure, self._app)
        init_app_manager()
        middlewares.create_extras(self._app)
        tracing.create_tracing(self._app)

    def start(self, launchFn: Union[Callable[[FastAPI, int]], None] = None):
        '''
        初始化配置并启动http监听服务

        :launchFn: 由调用问自主选择FastAPI的宿主实现和启动方式，传递的两个参数分别为FastAPI实例和从配置文件读取到的监听端口
        '''
        # 启动eureka(当前应用不会注册到注册中心)
        discovery_client.start()
        #  通过注册中心找到配置服务，加载远程配置
        discovery_client.load_config()
        configure.merge()
        #  初始化本地模块
        self._init()
        #  根据需要把当前应用注册到服务中心
        discovery_client.register()

        #  启动网站
        info = configure.get_app_info()
        port = info['port']

        if launchFn is not None:
            return launchFn(self._app, port)

        import uvicorn
        uvicorn.run(self._app, host="0.0.0.0", port=port, access_log=False)
        if log.isInfoEnabled():
            log.info("应用程序在端口 %s 启动完成." % port)

    def stop(self):
        discovery_client.unregister()
