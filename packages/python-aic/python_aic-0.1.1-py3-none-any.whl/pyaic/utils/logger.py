
import os
import time 
import logging
import colorlog # pip install colorlog 
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict 

from abc import ABC, abstractmethod


_default_formats = {
    # 终端输出格式
    'color_format': '%(log_color)s%(asctime)s.%(msecs)03d %(name)s %(filename)s:%(lineno)d %(levelname)s \t| %(message)s',
    # 日志输出格式
    'log_format': '%(asctime)s.%(msecs)03d %(name)s %(filename)s:%(lineno)d %(levelname)s \t| %(message)s'
}

_logdict = dict()





def get_logger(name: str="muyaiot", dirname: str="logs", prename: str="log-", timfmt="%Y%m%d"):
    # print(f"_logdict.keys(): {_logdict.keys()}, name: {name}, dirname: {dirname}")
    if name in _logdict:
        return _logdict[name] 
    


    nowtimestr = datetime.now().strftime(f"{timfmt}")
    os.makedirs(dirname, exist_ok=True)
    filename = os.path.join(dirname, f"{prename}{nowtimestr}.log")

        # 创建日志记录器
    __logger = logging.getLogger(name)

    # 设置默认日志记录器记录级别
    # DEBUG, INFO, CRITICAL, FATAL, ERROR
    level = getattr(logging, os.getenv("MUYAIOT_LOG_LEVEL", "DEBUG"))
    __logger.setLevel(level)


    # set handler 
    handler = RotatingFileHandler(filename=filename, maxBytes=7 * 1024 * 1024, backupCount=7, encoding='utf-8')
    formatter = logging.Formatter(_default_formats["log_format"], datefmt='%Y%m%d-%H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(level=level)
    __logger.addHandler(handler)


    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(_default_formats["color_format"], datefmt='%Y%m%d-%H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(level=level)
    __logger.addHandler(handler)

    _logdict[name] = __logger
    return __logger 



class Logger:
    @staticmethod 
    def get():
        return get_logger()



if __name__ == "__main__":
    print(f"Hello")
    logger = get_logger()

    logger.debug("debug")
    logger.info("info")
    logger.error("error")


    # logger = get_logger(name = "hello")
    # logger.debug("debug")
    # logger.info("info")
    # logger.error("error")


    logger1 = get_logger()
    logger1.debug("debug")
    logger1.info("info")
    logger1.error("error")


    logger.debug("debug")
    logger1.debug("debug")


    logger2 = get_logger(name = "logger2", prename="logger2")
    logger2.debug("debug")
    logger2.info("info")
    logger2.error("error") 
    

