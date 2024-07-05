# author: Lanzhijiang
# date: 2023/06/30
# desc: 自然语言理解：文本意图判断+技能分配+技能函数分配+槽位提取


import sqlite3
import requests
from lib.common_func import get_token
from lib.exceptions import NetworkFatal
from lib.settings import Settings
from lib.log import HALog


class HANLU:

    log = HALog("HANLU")
    setting = Settings.get_json_setting("process")["nlu"]

    token = None

    @classmethod
    def get_intent(cls, text, conversation=None):
        
        """
        解析意图
            初次判断：
                通过调用云端训练的意图判断模型识别意图->一个中文标签->本地字典转换
                    如果置信度过低
                        1.选出备选，进入确认流程：identiyfing_intent
                        2.使用关键词判断
                
                再通过各个技能的专有意图模型/本地模式识别技能内意图（二级意图），也就是处理函数

                通过技能函数的配置文件，得出需要的槽位信息以及槽位配置文件
                根据槽位信息以及相关配置文件对当前文本提取槽位

            槽位提取：
                字典模式：关键词匹配
                句法依存模式
                句式模式：整个句式 局部句式
                模糊模式：AI
                字典+句法依存模式：
                句式+句法模式

            传代判断（一般是询问之后触发）：
                根据当前用户文本，结合之前的用户文本和意图做出判断
                如果新的文本给出了不同的意图取向，直接结束当前对话，重新创建

        :param text: 用户文本
        :param conversation: conversation对象，可以提供历史对话信息与已有意图判断
        :return intent, flag
        """
        cls.log.add_log("开始分析用户文本意图", 1)

        # if conversation.state is None:  # todo 忽略了状态
        intent, flag = cls.get_intent_for_first(text)
        if not flag:
            return intent, False
        return intent, flag
        
    @classmethod
    def get_intent_for_first(cls, text) -> list:

        """
        初次解析意图
        :param text: 用户文本
        :return intent[(l1_intent, l2_intent], (..., ...)), flag
        """
        cls.log.add_log("初次分析意图", 0)

        if cls.token is None:
            cls.token = get_token(cls, cls.setting["appKey"], cls.setting["secretKey"])

        # 解析L1意图
        l1_intent = cls.get_l1_intent(text)
        if not l1_intent:
            # 无法解析，采用默认意图: chat
            return (("chat", "chat"),), True
        if l1_intent[0] == "smarthome":
            return (("smarthome", "throw_it_to_aqara"),), True
        else:
            return (("chat", "chat"),), True  # 除了智能家居，全部都丢给了图灵  todo

        if len(l1_intent) > 1:
            # 需要确认
            intent_result = []
            for i in l1_intent:
                intent_result.append((i, None))
            return intent_result, False
        
        # 解析L2意图
        # l2_intent = cls.get_l2_intent(text)

    
    @classmethod
    def get_l1_intent(cls, text) -> list:

        """
        解析L1意图
        """
        cls.log.add_log("开始解析一级意图", 1)

        url = "%s?access_token=%s" % (cls.setting["l1IntentJudgeUrl"], cls.token)
        res = requests.post(url, json={"text": text})

        try:
            res.raise_for_status()
        except:
            raise NetworkFatal("请求意图判断API")
        else:
            try:
                l1_intent_judge_result = res.json()["results"]
            except KeyError:
                cls.log.add_log("依赖AI解析意图失败，响应-%s" % res.json(), 3)
                l1_intent = []
            else:
                cls.log.add_log("解析成功，响应-%s" % res.json() , 0)
                item = l1_intent_judge_result[0]
                score = item["score"]
                l1_intent = [cls.setting["l1IntentMapping"][item["name"]]]

                if score > cls.setting["intentJudgeScoreThreshold"][0]:
                    # 一定置信
                    pass
                else:
                    return []
                # elif score > cls.setting["intentJudgeScoreThreshold"][1]:
                #     # 需要确认(如果差过大，就无需确认；反之，就需要确认)
                #     l1_intent = cls.pick_possible_l1_intent(l1_intent, l1_intent_judge_result, score, 0.084)
                # elif score < cls.setting["intentJudgeScoreThreshold"][1]:
                #     # 需要进行关键词判断
                #     l1_intent = cls.pick_possible_l1_intent(l1_intent, l1_intent_judge_result, score, 0.12)
                    
                #     result = cls.get_intent_by_keyword(text, l1_intent, "l1")
                #     if result is not None:
                #         l1_intent = [result]
                #     else:
                #         l1_intent = []

        return l1_intent
        
    
    @classmethod
    def get_intent_by_keyword(cls, text, possible_intent_list: list, mode=None, l1_intent_id=None) -> str:

        """
        使用关键词法判断意图
            采用sqlite3查找
            kw_intent_db设计：
                l1_intent_table
                <l1_intent>_l2_intent_table

                table: id intent_id kw1 kw2 kw3 .. kwn 各个kw之间为and的关系

        :param mode: 决定了possible_intent_list的内容，为None就是l1+l2；为l1/2就是l1/2
        :param l1_intent_id
        """
        cls.log.add_log("开始使用关键词法判断意图, 意图级别-%s" % mode, 1)

        result = None
        kw_intent_db = sqlite3.connect("./data/db/kw_intent.db")
        kw_intent_cursor = kw_intent_db.cursor()

        if mode == "l1" or mode is None:
            table_name = "l1_intent_table"

            for possible_intent in possible_intent_list:
                kw_intent_cursor.execute("SELECT * FROM %s WHERE intent_id = '%s';" % (table_name, possible_intent))
            
            l1_kw_intent_row_list = kw_intent_cursor.fetchall()
            for l1_kw_intent_row in l1_kw_intent_row_list:
                conditions = l1_kw_intent_row[1].split(";")

                if not conditions:
                    for kw_group in l1_kw_intent_row[2:]:
                        kw_group = kw_group.split(",")
                        for kw in kw_group:
                            if kw in text:
                                result = l1_kw_intent_row[0]
                                break
                        if result is not None: break
                else:
                    _pass = False
                    for condition in conditions:
                        condition = condition.split(",")
                        condition_pass = False

                        # todo 取消了kw_group的设计
                        for group_id in condition:
                            kw_group = l1_kw_intent_row[2:][group_id]
                            kw_group = kw_group.split(",")
                            for kw in kw_group:
                                if kw in text:
                                    condition_pass = True
                                    break
                            
                            if condition_pass: 
                                _pass = True
                                break  # or条件，只要一个组过就行
                        
                        if not condition_pass: 
                            _pass = False
                            break  # and条件，比如所有条件都通过
                    
                    if _pass: result = l1_kw_intent_row[0]
                
                if result is not None: break


        elif mode == "l2":
            table_name = "%s_l2_intent_table" % l1_intent_id

        kw_intent_cursor.close()

    @classmethod
    def pick_possible_l1_intent(cls, l1_intent: list, l1_intent_judge_result: list, top_score: float, gap: float) -> list:

        """
        挑选几个可能性大的一级意图
        """
        for i in l1_intent_judge_result:
            if abs(top_score - i["score"]) < gap:  # 可能应该取平均间隔 todo
                l1_intent.append(cls.setting["l1IntentMapping"][i["name"]])
            else:
                break

        return l1_intent
    
    @classmethod
    def indentifying_intent(cls, user_text, intent_list, keyword_list):

        """
        确认意图（效果很差，但是诶...） todo
            根据用户文本，结合关键词列表作关键词匹配，然后对应到intent_list中的意图
        """
        for i in range(len(keyword_list)):
            keywords = keyword_list[i]
            if keywords[0] in user_text or keywords[1] in user_text:
                return intent_list[i]
            
    @classmethod
    def get_identifying_intent_expression():
        # todo
        pass

    @classmethod
    def update_kw_intent_table():

        """
        更新关键词与意图的对应表
        """

    @classmethod
    def get_slot(cls, user_text, slot_config):

        return {}, []  # todo

    @classmethod
    def use_db_lexer_rule(cls, lexer_rule_id, kw):
        
        """
        使用数据库句法规则
        """
        pass

    @classmethod
    def use_db_dict(cls, dict_id, kw):

        """
        使用数据库(纯)字典模式
            用kw
        """

    @classmethod
    def use_db_dict_lexer_mixing(cls, dict_id, nlp_rule, kw):

        """
        使用数据库字典+句法规则混合模式
            在字典匹配之后，还要符合句法规则，是and关系
        """

