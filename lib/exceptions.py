# author: Lanzhijiang
# desc: 异常库
# date: 2022/12/11
# last_edit: 2023/06/27

import time



class ExceptionBase(BaseException):

    def __init__(self, where=None) -> None:

        BaseException.__init__(self)
        self.when = time.time()
        self.where = where

        self.context = {}
        self.description = None
        self.helpmsg = ""
        self.surpressed = []

        self.cleanup_handling_result = None

        self.log_level = 2

    def __repr__(self):
        return "%s, 你可以: %s" % (self.description, self.helpmsg)
    
    def report(self, log, attach=""):
        content = "%s, %s" % (str(self), attach)
        self.report_through_speech(content)
        self.report_through_log(log, content)

    def report_through_speech(self, content=None):
        if content is None:
            content = str(self) 
        from conversation.output.tts import HATTS
        from lib.common_func import Pixels
        Pixels.speak()
        HATTS.start(content)
        Pixels.off()

    def report_through_log(self, log, content=None):
        if content is None:
            content = str(self)
        log.add_log(content, self.log_level)



class Error(ExceptionBase):

    def __init__(self, where=None) -> None:

        ExceptionBase.__init__(self, where)
        self.error_handling_result = None

        self.log_level = 3


class Fatal(ExceptionBase):

    def __init__(self, where=None) -> None:

        ExceptionBase.__init__(self, where)
        self.fatal_handling_result = None

        self.log_level = 4

    def __str__(self):

        return self.helpmsg


class ParamLostFatal(Fatal):

    def __init__(self, lost_params, desc=None, where=None, helpmsg=None, **sth):

        Fatal.__init__(self, where)
        self.description = desc
        self.lost_params = lost_params

        if helpmsg is None:
            helpmsg = "请确认输入正确, 没有缺漏错误"
        self.helpmsg = helpmsg

    def __str__(self):

        return "缺失参数: %s。%s" % (self.lost_params, self.helpmsg)


class RequireLostFatal(Fatal):

    def __init__(self, requiring, desc=None, helpmsg=None, where=None) -> None:
        
        Fatal.__init__(self, where)
        self.description = desc
        self.requiring = requiring

        if helpmsg is None:
            helpmsg = "请检查依赖环境"
        self.helpmsg = helpmsg

    def __str__(self):

        return "缺少依赖：%s。%s" % (self.requiring, self.helpmsg)


class NonsupportFatal(Fatal):

    def __init__(self, nonsupport_target, desc=None, where=None, **sth):

        Fatal.__init__(self, where)
        self.description = desc
        self.nonsupport_target = nonsupport_target


class InitializationFatal(Fatal):

    def __init__(self, desc=None, where=None, **sth):

        Fatal.__init__(self, where)
        self.description = desc


class NetworkFatal(Fatal):
    
    def __init__(self, request_target, desc=None, helpmsg=None, where=None) -> None:
        
        Fatal.__init__(self, where)
        self.request_target = request_target
        self.description = desc

        if helpmsg is None:
            helpmsg = "稍后再试"
        self.helpmsg = helpmsg

    def __str__(self):

        return "请求%s时发生错误。问题为:%s。你可以%s" % (self.request_target, self.description, self.helpmsg)
 
