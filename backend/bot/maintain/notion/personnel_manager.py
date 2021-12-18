# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: Notion Personnel Manager
# date: 2021/12/11

import json
from pypinyin import lazy_pinyin


class HAPersonnelManager:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log

        self.nlp = ba.nlp

        self.personnel_list = json.load(open("./backend/data/json/personnel_list.json", "r", encoding="utf-8"))
        self.person_list = self.personnel_list["person"]
        self.department_list = self.personnel_list["department"]

    def get_person_info(self, person_id):

        """
        获取个人信息
        :param person_id: 人员id
        """
        self.log.add_log("HAPersonnelManager: start search for person-%s's info" % person_id, 1)

        try:
            person_list = self.personnel_list["person"]
            return person_list[person_id]
        except KeyError:
            self.log.add_log("HAPersonnelManager: person-%s does not exist" % person_id, 3)
            return False

    def delete_person(self, person_id):

        """
        删除人员
        :param person_id 人员id
        """
        self.log.add_log("HAPersonnelManager: delete person-%s" % person_id, 1)

        try:
            department = self.person_list["person"][person_id]["department"]
            del self.person_list["person"][person_id]
            self.person_list["department"][department].remove(person_id)

            json.dump(self.person_list, open("./backend/data/json/personnel_list.json", "w", encoding="utf-8"))
            return True
        except KeyError:
            self.log.add_log("HAPersonnelManager: person-%s does not exist" % person_id, 3)
            return False

    def analyze_person_id_from_text(self, text, text_type, nickname_mode=False):

        """
        从文本中提取人员id
        :param text: 文本
        :param text_type: 文本类型（sentence, word)
        :param nickname_mode: 是否使用nickname列表查询（一定）
        :return: like lpy/yyh, str
        """
        self.log.add_log("HAPersonnelManager: try to analyze person_id from text-%s, text_type-%s" % (text, text_type), 1)
        result_list = []

        if text_type == "sentence":
            # nlp mode
            nlp_result = self.nlp.lexer_result_process(self.nlp.lexer(text))
            per_result = nlp_result["ne"]["PER"]
            for i in per_result:
                name = i["content"]
                result = ""
                word_pinyin = lazy_pinyin(name)
                for a in word_pinyin:
                    result = result + a[0]
                result_list.append(result)
            # [{'offset': 5, 'length': 3, 'content': '玫红红', 'basic_words': ['玫', '红红'], 'ne': 'PER', 'pos': ''}]

        elif text_type == "word":
            result = ""
            # nickname mode
            nickname_list = self.personnel_list["nickname"]
            for nickname_group in nickname_list:
                for nickname in nickname_group[0]:
                    if nickname == text:
                        result = nickname_group[-1]
                        break
                if result != "":
                    break

            if result == "" and not nickname_mode:
                # pinyin head mode
                self.log.add_log("HAPersonnelManager: nickname mode failed, try pinyin head mode", 1)
                word_pinyin = lazy_pinyin(text)
                for a in word_pinyin:
                    result = result + a[0]

            result_list.append(result)

        if not result_list:
            self.log.add_log("HAPersonnelManager: failed to analyze person_id from text", 2)
        else:
            self.log.add_log("HAPersonnelManager: person_id analyze success, result-%s" % result_list, 1)

        return result_list


