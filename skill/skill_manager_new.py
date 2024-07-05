# author: Lanzhijiang
# date: 2023/6/30
# desc: 采用sqlite3实现skill相关配置数据的管理
#    table: skill_slot_config
#   根据意图名称查询技能 
#   管理技能相关的配置
#   

from lib.settings import Settings
from lib.log import HALog

import sqlite3


skill_table = Settings.get_py_setting("skill_table")
log = HALog("HASkillManager")

skill_config_db = sqlite3.connect('./data/db/skill_config.db')
skill_config_cursor = skill_config_db.cursor()
slot_config_db = sqlite3.connect('./data/db/slot_config.db')
slot_config_cursor = slot_config_db.cursor()


def get_skill_func_by_intent(intent: tuple, set_conversation=None):

    """
    通过意图获取技能函数
        l1->skill->l2->skill_func
    :param intent: 意图 tuple
    """
    log.add_log("从意图-技能映射中获取意图对应技能", 1)

    try:
        skill_func_table = skill_table.l1_intent_to_skill[intent[0]]
    except KeyError:
        log.add_log("无法找到意图对应技能，请检查意图与配置 intent-%s" % intent[0], 3)
    else:
        skill_func_table["skill_file"].conversation = set_conversation
        try:
            skill_func = skill_func_table[intent[1]]
        except KeyError:
            log.add_log("无法找到技能函数，请检查意图与配置 intent-%s" % intent[1], 3)
        else:
            return skill_func
        
    return None


def get_skill_func_config(skill_id, skill_func_id):

    """
    获取技能函数的配置信息
    :param skill_id 也就是skill_config_db 的 table名称 l1_intent_id
    :param skill_func_id 也就是这个table中的这个技能函数的id l2_inent_id
    """
    log.add_log("查找%s-%s的技能配置信息" % (skill_id, skill_func_id), 1)
    return {"slots": None}
    

def get_slot_config(skill_id, slot_id):

    """
    获取槽位配置
        先在common中找，然后再到特定的skill_slot标中找
    :param skill_id: 用于找到技能特定slot配置table（当slot_id中首位为#时才使用）
    :param slot_id: 找slot
    """
    return None


def get_lexer_rule():

    pass



def get_sentence_rule():

    pass



