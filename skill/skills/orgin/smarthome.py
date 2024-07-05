# author: Lanzhijiang
# date: 2023/07/02
# desc: 实现智能家居控制的技能
#       目前支持：绿米(调用AqaraBridge)


from lib.common_func import send_request_to_aqara
from lib.log import HALog
from lib.settings import Settings


log = HALog("HASKillSmarthome")
conversation = None


def turn_on_device(device_name, resource_name=None):

    """
    打开设备
        也就是打开设备的默认资源：
        找到设备的默认资源
        查询怎样设置这个资源算作打开
        交给set_resource_value
    """
    pass


def turn_off_device():

    """
    关闭设备
        实现方法同上
    """


def set_resouce(device_name, resource_name):

    """
    设置资源
        这里的资源包括了名称、位置、等等
    """


def set_l1_resource(l1_resource_name):

    """
    设置一级资源
    :param l1_resource_name: 设置
    """


def set_resource_value():

    """
    设置资源值
    """

def set_resource_name():

    """
    设置资源名称
    """


def query_resource_current():

    """
    查询资源当前值
        查到值之后，还得转化成人话
    """


def query_resource_history():

    """
    查询资源历史 todo
    """

def query_resource_statistics():

    """
    查询资源统计 todo
    """


def throw_it_to_aqara(user_text=None):

    """
    丢给绿米负责
    """
    log.add_log("交给绿米语控接口", 1)

    if user_text is None:
        user_text = conversation.history[-1]["userText"]

    res = send_request_to_aqara("command.device.resource", 
        {
            "positionId": "real1.1121170759796547584",
            "queryText": user_text
        }
    )
    res_json = res.json()
    # log.add_log("绿米语控接口响应: %s" % res_json, 1)
    try:
        speak = res_json["result"]["speak"].replace("小乔", "我")
        conversation.output_func(speak)
    except TypeError:
        conversation.output_func("控制失败, %s" % res_json["message"])