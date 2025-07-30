# coding=utf8
import json
from importlib import import_module
from io import StringIO
import pandas
import torch
import numpy
from datetime import datetime
from .XLRedisUtil import XLRedisUtil
from expiringdict import ExpiringDict
from ..XLSYS.Base import AISerializeObject
from ..XLSYS.Entities import XLContext


class ContextSaveEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            save_dict = {'__class_flag': "datetime", '__time': obj.strftime("%Y-%m-%d %H:%M:%S")}
            return save_dict
        elif isinstance(obj, numpy.ndarray):
            save_dict = {'__class_flag': "numpy", '__data': json.dumps(obj.tolist(), ensure_ascii=False)}
            return save_dict
        elif isinstance(obj, pandas.DataFrame):
            save_dict = {'__class_flag': "DataFrame", '__data': obj.to_json()}
            return save_dict
        elif isinstance(obj, torch.Tensor):
            save_dict = {'__class_flag': "torch", '__data': json.dumps(obj.detach().cpu().tolist(), ensure_ascii=False)}
            return save_dict
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, AISerializeObject):
            save_dict = obj.__to_json__()
            return save_dict
        else:
            raise Exception("ContextSaveEncoder Unexpected object type " + str(type(obj)))


class ContextLoadDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(
            object_hook=self.object_hook,
            *args, **kwargs)

    def object_hook(self, o):
        """
        对字典解码，如果同时设置'object_pairs_hook'，'object_hook'将不生效
        :param o: 原始数据字典
        :return: 实际需要的数据
        """
        if o.get('__class_flag') is not None and o.get('__class_flag') == 'numpy':
            return numpy.asarray(json.loads(o['__data']))
        if o.get('__class_flag') is not None and o.get('__class_flag') == 'torch':
            return torch.asarray(numpy.asarray(json.loads(o['__data'])))
        if o.get('__class_flag') is not None and o.get('__class_flag') == 'DataFrame':
            return pandas.read_json(StringIO(o['__data']))
        if o.get('__class_flag') is not None and o.get('__class_flag') == 'AISerializeObject':
            return getattr(import_module(name=o['__class_module']), o['__class_name']).__from_json__(o)
        if o.get('__class_flag') is not None and o.get('__class_flag') == 'datetime':
            return datetime.strptime(o['__time'], "%Y-%m-%d %H:%M:%S")
        return o


class XLStorageUtil(object):
    def __init__(self, max_len=1000, pool_ttl_seconds=3600):
        self.pool_ttl_seconds = pool_ttl_seconds
        self.redis_util = XLRedisUtil()
        # 创建一个带有过期时间的字典，过期时间为5秒
        self.context_pool = ExpiringDict(max_len=max_len, max_age_seconds=pool_ttl_seconds)
        pass

    def getFlow(self, context_id) -> XLContext:
        local_context = self.context_pool.get(context_id)
        if local_context is not None:
            return local_context
        redis_data_str = self.redis_util.get("context:" + context_id)
        if redis_data_str is None:
            return None
        redis_context = json.loads(redis_data_str, cls=ContextLoadDecoder)
        if redis_context is None:
            return None
        self.context_pool[context_id] = redis_context
        return redis_context
        pass

    def saveContextInfo(self, context: XLContext):
        save_info = json.dumps(context, cls=ContextSaveEncoder, ensure_ascii=False)
        self.redis_util.set("context:" + context.context_id, save_info, ex=self.pool_ttl_seconds)
        pass


pass
