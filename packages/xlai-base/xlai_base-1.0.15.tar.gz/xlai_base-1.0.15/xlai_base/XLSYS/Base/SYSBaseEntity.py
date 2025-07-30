# coding=utf8
import inspect
from importlib import import_module

from . import XLObjectUtil


class AISerializeObject(object):

    def __to_json__(self):
        pass

    @staticmethod
    def __from_json__(json_str: str):
        pass

    pass


class AIDataSerialize(AISerializeObject):
    def __to_json__(self):
        save_dict = {'__class_data': self.__dict__, '__class_flag': "AISerializeObject", '__class_module': self.__module__,
                     '__class_name': self.__class__.__name__}
        return save_dict
        pass

    @staticmethod
    def __from_json__(json_dict: dict):
        obj_class_info = getattr(import_module(name=json_dict['__class_module']), json_dict['__class_name'])
        obj = object.__new__(obj_class_info)
        obj.__dict__ = json_dict['__class_data']
        return obj
        pass

    pass


class AIFuncSerialize(AISerializeObject):
    def __to_json__(self):
        save_dict = {'__class_data': self.__dict__, '__class_flag': "AISerializeObject", '__class_module': self.__module__,
                     '__class_name': self.__class__.__name__}
        return save_dict
        pass

    @staticmethod
    def __from_json__(json_dict: dict):
        obj_class_info = getattr(import_module(name=json_dict['__class_module']), json_dict['__class_name'])
        obj = object.__new__(obj_class_info)
        obj.__dict__ = json_dict['__class_data']
        return obj

    pass


class ObjectMangeBase(object):

    def __init__(self, name_key, cover_obj=False, **kwargs):
        self.name_key = name_key
        old_obj = XLObjectUtil.getObj(name_key, prn=False)
        if old_obj is not None and not cover_obj:
            # old_obj_info = XLObjectUtil.getObjInfo(name_key)
            # print(json.dumps(old_obj_info))
            raise Exception("{} 的 obj已经存在了".format(name_key))
        # 获取当前调用栈的帧
        stack = inspect.stack()
        obj_info = {
            'stack_info_list': ["{}--{}".format(stack[i].filename, stack[i].lineno) for i in range(1, len(stack)) if
                                "XLAI" in stack[i].filename]
        }

        XLObjectUtil.updateObj(name_key, self, obj_info)
        pass

    pass
