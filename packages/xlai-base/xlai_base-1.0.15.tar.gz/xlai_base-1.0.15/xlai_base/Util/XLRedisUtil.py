# coding=utf8
import redis
import json
from datetime import datetime, timedelta
from ..Department import BaseDPart
from ..XLSYS.Base import SingletonArgs


@SingletonArgs
class XLRedisUtil(object):
    @staticmethod
    def get_remaining_seconds_of_today():
        now = datetime.now()
        tomorrow_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        remaining_time = tomorrow_midnight - now
        return int(remaining_time.total_seconds())

    def __init__(self, department: BaseDPart, host, port, password,
                 is_mq=False, is_data_client=False, save_db=1):
        self.department = department
        # decode_responses=True 这样写存的数据是字符串格式
        pool = redis.ConnectionPool(host=host, port=port, decode_responses=True,  db=save_db,
                                    max_connections=4, password=password)
        self.r = redis.StrictRedis(connection_pool=pool)

        if is_mq:
            mq_pool = redis.ConnectionPool(host=host, port=port, decode_responses=True,  db=2,
                                        max_connections=15, password=password)
            self.mq_client = redis.StrictRedis(connection_pool=mq_pool)

        if is_data_client:
            data_pool = redis.ConnectionPool(host=host, port=port, decode_responses=True,  db=3,
                                    max_connections=4, password=password)
            self.data_client = redis.StrictRedis(connection_pool=data_pool)

        pass

    def get_data_client(self):
        return self.data_client

    def get_mq_client(self):
        return self.mq_client

    def buildKey(self, key):
        return "{}:{}".format(self.department.name, key)

    def delete(self, key):
        self.r.delete(self.buildKey(key))

    def set(self, key, info, ex=None):
        self.r.set(self.buildKey(key), info, ex=ex)

    def acquire_lock(self, key, ex):
        if self.r.setnx(self.buildKey(key), key):
            self.r.expire(self.buildKey(key), ex)
            return True
        return False

    def get(self, key, default=None):
        res = self.r.get(self.buildKey(key))
        if res is None:
            return default
        return res

    def ttl(self, key):
        return self.r.ttl(self.buildKey(key))

    def incr(self, key, ex=None):
        t_key = self.buildKey(key)
        res =  self.r.incr(t_key)
        if ex is not None:
            self.r.expire(t_key, ex)
        return res

    def setDict(self, key, info: dict, ex=60):
        info_str = json.dumps(info, ensure_ascii=False)
        self.r.set(self.buildKey(key), info_str, ex=ex)

    def getDict(self, key) -> dict:
        info_str = self.r.get(self.buildKey(key))
        if info_str is None:
            return {}
        return json.loads(info_str)

    def listPut(self, key, info):
        self.r.lpush(self.buildKey(key), info)
    def listGetByIndex(self, key, index):
        return self.r.lindex(self.buildKey(key), index)

    def listGetLen(self, key):
        return self.r.llen(self.buildKey(key))

    def listSetByIndex(self, key,  index, info):
        return self.r.lset(self.buildKey(key), index, info)

    def listRemoveByIndex(self, key, index):
        run_key = self.buildKey(key)
        if index < 0 or index >= self.r.llen(run_key):
            return False  # 索引越界
        element = self.r.lindex(run_key, index)
        if not element:
            return False  # 元素不存在
        self.r.lset(run_key, index, "__DELETE__")
        self.r.lrem(run_key, 0, "__DELETE__")
        return True
    def listGetAll(self, key) -> dict:
        m_key = self.buildKey(key)
        t_size = self.r.llen(m_key)
        if t_size == 0:
            return []
        return self.r.lrange(m_key, 0, t_size)

    def hset(self, key,  vkey, vinfo):
        self.r.hset(self.buildKey(key), vkey, vinfo)

    def hget(self, key, vkey):
        return self.r.hget(self.buildKey(key), vkey)

    def hgetAll(self, key) -> dict:
        return self.r.hgetall(self.buildKey(key))

    def zadd(self, key,  info: dict):
        self.r.zadd(self.buildKey(key), info)

    def zscore(self, key,  value):
        return self.r.zscore(self.buildKey(key), value)

    def zcount(self, key, z_min=float("-inf"), z_max=float("inf")):
        return self.r.zcount(self.buildKey(key), z_min, z_max)

    def zrangebyscore(self, key, z_min=float("-inf"), z_max=float("inf")):
        return self.r.zrangebyscore(self.buildKey(key), z_min, z_max)


if __name__ == '__main__':
    red = XLRedisUtil()
    # red.set('sss', 'bbb')
    # print(red.get('sss'))
    # print(red.get('sssee'))
    # print(red.getDict('sssss'))
    # red.setDict('dsfs', {'ss': 'dd'})
    # print(red.getDict('dsfs'))
    red.zadd('ss', {'dd':12.3})
    print(red.zscore('ss','dd'))
    print(red.zcount('ss',z_min=20))
    print(red.zrangebyscore('ss'))



    pass
