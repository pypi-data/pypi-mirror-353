# coding=utf8
"""
logging模块是Python的内置模块，不需要安装。

步骤：
1，创建一个把日志信息保存到文件中的处理器FileHandler
2，把文件处理器添加到logger中
3，把格式器传入到文件处理器中
"""
# 导入logging模块
import logging.handlers
import os

import logstash

from ..Department import BaseDPart
from ..XLSYS.Base import SingletonArgs
from ..XLSYS.Entities import XLContext


class MyLogHandler(logging.Handler, object):
    def __init__(self, extend_info=None, department_name=None, env_flag=None, **kwargs):
        logging.Handler.__init__(self)
        self.base_info = {
            'department': department_name,
            'env_flag': env_flag
        }
        if extend_info is not None and isinstance(extend_info, dict):
            self.base_info.update(extend_info)
        pass

    def emit(self, record):
        # 注意不要大写
        record.__dict__.update(self.base_info)


def buildRequestLogger(log_dir, department_name, env_flag):
    requestLogger = logging.getLogger('request')
    requestLogger.setLevel(level=logging.INFO)
    # 添加TimedRotatingFileHandler
    # 定义一个1秒换一次log文件的handler
    # 保留5个旧log文件
    timefilehandler = logging.handlers.TimedRotatingFileHandler(
        '{}/request_{}.log'.format(log_dir, department_name),
        when='D',
        interval=1,
        encoding="utf-8",
        backupCount=5
    )

    # 设置后缀名称，跟strftime的格式一样
    timefilehandler.suffix = "%Y-%m-%d.log"
    # 创建日志格式器
    formatter = logging.Formatter(
        fmt="%(asctime)s| [%(mod)s] | [%(context_id)s| [%(global_info)s |\n%(message)s")
    timefilehandler.setFormatter(formatter)
    requestLogger.addHandler(timefilehandler)
    if env_flag == 'dev':
        chlr = logging.StreamHandler()  # 输出到控制台的handler
        chlr.setFormatter(formatter)
        requestLogger.addHandler(chlr)

    return requestLogger
    pass


@SingletonArgs
class XLLogger(logging.getLoggerClass()):
    def __init__(self, department: BaseDPart = None, base_path=None, logstash_host=None, env_flag='dev',
                 extend_info=None, out_print=True, **kwargs):
        logging.getLoggerClass().__init__(self, "logger", level=logging.INFO)
        department_name = department.name.lower().strip()
        my_log_handler = MyLogHandler(extend_info=extend_info, department_name=department_name, env_flag=env_flag,
                                      **kwargs)
        # 如果日志文件夹不存在，则创建
        if base_path is not None and isinstance(base_path, str):
            log_path = base_path if base_path.endswith("/") else base_path + "/"
            log_dir = log_path + "logs"
        else:
            log_dir = os.path.abspath('..') + os.sep + "logs"  # 日志存放文件夹名称
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        # 添加TimedRotatingFileHandler
        # 定义一个1秒换一次log文件的handler
        # 保留5个旧log文件
        timefilehandler = logging.handlers.TimedRotatingFileHandler(
            '{}/log_{}.log'.format(log_dir, department_name),
            when='D',
            interval=1,
            encoding="utf-8",
            backupCount=5
        )

        # 设置后缀名称，跟strftime的格式一样
        timefilehandler.suffix = "%Y-%m-%d.log"
        # 创建日志格式器
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(filename)s %(lineno)d行]| [ %(levelname)s ] | [%(message)s]")
        timefilehandler.setFormatter(formatter)
        self.addHandler(timefilehandler)
        self.addHandler(my_log_handler)
        if logstash_host is not None:
            self.addHandler(logstash.LogstashHandler(logstash_host, 20044, version=1))

        if out_print:
            chlr = logging.StreamHandler()  # 输出到控制台的handler
            chlr.setFormatter(formatter)
            self.addHandler(chlr)

        self.requestLogger = buildRequestLogger(log_dir, department_name, env_flag)
        pass

    def infoContext(self, context: XLContext, msg, **kwargs):
        extra = {
            'context_id': context.context_id,
            'all_trace_id': context.global_info.all_trace_id
        }
        self.info(msg, extra=extra, **kwargs)
        pass

    def errorContext(self, context: XLContext, msg, **kwargs):
        extra = {
            'context_id': context.context_id,
            'all_trace_id': context.global_info.all_trace_id
        }
        self.error(msg, extra=extra, **kwargs)
        pass
