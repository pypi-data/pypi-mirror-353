# coding=utf8

class BaseDPart(object):

    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        pass

    def getHttpUrl(self, path):
        if path.startswith('/'):
            path = path[1:]
        return "http://{}:{}/{}".format(self.host, self.port, path)

    pass


PP = BaseDPart('PP', 'pp.ai.home.tokgo.cn', 15001)
SF = BaseDPart('SF', 'sf.ai.home.tokgo.cn', 15002)
AL = BaseDPart('AL', 'al.ai.home.tokgo.cn', 15003)
MB = BaseDPart('MB', 'mb.ai.home.tokgo.cn', 15004)
EXT = BaseDPart('EXT', 'ext.ai.home.tokgo.cn', 15005)
EV = BaseDPart('EV', 'ev.ai.home.tokgo.cn', 15006)
MP = BaseDPart('MP', 'mp.ai.home.tokgo.cn', 15007)
