# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's backend base
# date: 2021/11/4
# last_edit: 2023/06/27

import threading

import os
import sys
import time
import signal
import sqlite3
import requests
from lib import common_func
# import multiprocessing

from lib.log import HALog
from lib.settings import Settings

# from awaken_engine import snowboy_awaken
from awaken_engine import pvporcupine_awaken
from awaken_engine import keyboard_awaken
from awaken_engine import http_awaken
# from awaken_engine import socket_awaken

from conversation.conversation import HAConversation
from conversation.output.player import HAPlayer
from conversation.input.recorder import HARecorder

from lib.exceptions import Fatal, InitializationFatal, ExceptionBase


def get_callback(engine, callback_func):
    
    def callback(**sth):
        callback_func(engine, **sth)
        return

    return callback


class HAInit:

    setting = Settings.get_json_setting("overall")
    log = HALog("HAInit")

    conversation_state = [False]

    @classmethod
    def run(cls):

        """
        启动HadreamAssistant
        :return:
        """
        print("""

            ###########################################
                         HadreamAssistant
                  [SpecialEdition:CodemaoSmartHome]
                     ---Customize Assistant---

              (c)2023 Lanzhijiang all rights reserved
                  Email: lanzhijiang@foxmail.com
            ###########################################

        """)
        cls.log.add_log("==============================", 1)
        cls.log.add_log("HadreamAssistant 启动 ", 1)

        try:
            cls.self_check()
        except InitializationFatal as e:
            e.report(cls.log, "初始化失败")

        cls.log.add_log("启动 pulseaudio", 1)
        os.system("pulseaudio --start")

        cls.log.add_log("设置signal", 1)
        signal.signal(signal.SIGINT, HARecorder.handle_int)

        cls.log.add_log("启动系统", 1)
        common_func.Pixels.off()
        cls.run_in_thread()

        # fn = sys.stdin.fileno()
        # sys.stdin=os.fdopen(fn)

        # pipe = multiprocessing.Pipe()

        # pipe[1].send
        # keyboard_process = multiprocessing.Process(
        #     target=keyboard_awaken.run, args=(pipe,), name="keyboard")
        #  = multiprocessing.Process(
        #     target=voice_awaken.run, args=(pipe,), name="voice")
        # # socket_process = multiprocessing.Process(
        # #     target=socket_awaken.run, args=(pipe,)
        # # )

        # keyboard_process.start()
        # snowboy_process.start()
        # socket_process.start()

        # cls.awaken_detect(pipe)

    @classmethod
    def run_in_thread(cls):

        cls.keyboard_thread = threading.Thread(target=keyboard_awaken.run_in_thread, name="keyboard",
                                               args=(get_callback("KeyboardAwakenEngine", cls.awaken_callback),))
        # cls.socket_thread = threading.Thread(target=http_awaken.run_in_thread, name="socket",
        #                                      args=(get_callback("SocketAwakenEngine", cls.awaken_callback),))
        cls.http_thread = threading.Thread(target=http_awaken.run_in_thread, name="http", 
                                           args=(get_callback("HttpAwakenEngine", cls.awaken_callback),))
        
        # cls.socket_thread.start()
        cls.http_thread.start()
        cls.keyboard_thread.start()

        cls.start_voice_awaken_thread()

    @classmethod
    def start_voice_awaken_thread(cls):

        # cls.voice_thread = threading.Thread(target=snowboy_awaken.run_in_thread, name="snowboy",
        #                                       args=(get_callback("SnowboyAwakenEngine", cls.awaken_callback), 
        #                                             snowboy_awaken.generate_interupt_check(cls.conversation_state)))
        cls.voice_thread = threading.Thread(target=pvporcupine_awaken.run_in_thread, name="pvporcupine",
                                            args=(get_callback("PvporcupineAwakenEngine", cls.awaken_callback),))
        cls.voice_thread.start()
    

    @classmethod
    def self_check(cls):

        cls.log.add_log("自检中...", 1)

        try:
            HAPlayer.file_play("./data/audio/welcome.wav")
        except:
            raise InitializationFatal("声卡配置错误")

        try:
            r = requests.get("http://www.baidu.com")
        except:
            raise InitializationFatal("网络错误")
        else:
            if r.status_code != 200:
                raise InitializationFatal("网络错误")
            
        cls.init_db()
    
    @classmethod
    def awaken_detect(cls, pipe):

        """
        等待pipe传过来唤醒以开始对话
        :return:
        """
        cls.log.add_log("start detecting awake status", 1)
        while True:
            engine = pipe[0].recv()
            cls.log.add_log("收到来自%s的唤醒" % engine, 1)
            pipe[1].send("start_conversation")
            cls.conversation.new_conversation(cls.setting["interfaceModeMapping"][engine])
            pipe[1].send("end_conversation")
    
    @classmethod
    def awaken_callback(cls, engine, **sth):
        awaken_callback_thread = threading.Thread(target=cls.real_awaken_callback, args=(engine, sth,), name="handler")
        awaken_callback_thread.start()

    @classmethod
    def real_awaken_callback(cls, engine, sth):
        cls.log.add_log("收到来自%s唤醒" % engine, 1)
        common_func.Pixels.wakeup()

        if not cls.conversation_state[0]:
            cls.conversation_state[0] = True
            try:
                HAConversation.start_conversation(cls.setting["interfaceModeMapping"][engine], **sth)
            except Fatal as e:
                e.report(cls.log)
            if not cls.voice_thread.is_alive():
                cls.start_voice_awaken_thread()
            cls.conversation_state[0] = False

    @classmethod
    def init_db(cls):

        """
        初始化数据库（不存在则创建） 
            目前是硬编码 todo
        """
        cls.log.add_log("初始化数据库中", 1)
        db_pre_setting = Settings.get_json_setting("db_pre")
        l1_intent_list = Settings.get_json_setting("process")["nlu"]["l1IntentList"]
        skill_list = Settings.get_py_setting("skill_table").skill_list

        pre_slot_config_db = Settings.get_json_setting("db_pre")["slotConfigDB"]
        pre_dict_tables = pre_slot_config_db["dictTables"]
        pre_lexer_rules = pre_slot_config_db["lexerRuleTable"]
        pre_sentence_rules = pre_slot_config_db["sentenceRuleTable"]

        if not os.path.exists("./data/db/kw_intent.db"):
            kw_intent_db = sqlite3.connect("./data/db/kw_intent.db")
            kw_intent_cursor = kw_intent_db.cursor()

            kw_intent_cursor.execute(
                "CREATE TABLE l1_intent_table (intent_id TEXT PRIMARY KEY, kw0 TEXT)"
            )
            for l1_intent_id in l1_intent_list:
                kw_intent_cursor.execute(
                "CREATE TABLE %s_l2_intent_table (intent_id TEXT PRIMARY KEY, kw0 TEXT)"
                % l1_intent_id
            )

            kw_intent_db.commit()
            kw_intent_cursor.close()
            kw_intent_db.close()

        if not os.path.exists('./data/db/skill_config.db'):
            skill_config_db = sqlite3.connect('./data/db/skill_config.db')
            skill_config_cursor = skill_config_db.cursor()

            for skill_id in skill_list:
                skill_config_cursor.execute(
                    "CREATE TABLE %s_table (skill_func_id TEXT PRIMARY KEY, slots TEXT)" % skill_id
                )
            
            skill_config_db.commit()
            skill_config_cursor.close()
            skill_config_db.close()


        if not os.path.exists('./data/db/slot_config.db'):
            slot_config_db = sqlite3.connect('./data/db/slot_config.db')
            slot_config_cursor = slot_config_db.cursor()

            slot_config_cursor.execute(
                "CREATE TABLE common_slot_table (slot_id TEXT PRIMARY KEY, mode TEXT, must INTEGER, asking TEXT, config TEXT)"
            )
            for skill_id in skill_list:
                slot_config_cursor.execute(
                    "CREATE TABLE %s_slot_table (slot_id TEXT PRIMARY KEY, mode TEXT, must INTEGER, asking TEXT, config TEXT)" % skill_id
                )
            
            for dict_id in pre_dict_tables:
                dict_table_name = "%s_dict_table" % dict_id
                slot_config_cursor.execute(
                    "CREATE TABLE %s (main TEXT PRIMARY KEY, fuzzy1 TEXT)" % dict_table_name
                )
                slot_config_cursor.execute(
                    "INSERT INTO %s VALUES (%s)" % (dict_table_name, ", ".join(pre_dict_tables[dict_table_name]))
                )
            
            slot_config_cursor.execute(
                "CREATE TABLE lexer_rule_table (lexer_rule_id TEXT PRIMARY KEY, postag TEXT, deprel TEXT)"
            )
            for lexer_rule_id in pre_lexer_rules:
                slot_config_cursor.execute(
                    "INSERT INTO %S VALUES (%s, %s)" % (lexer_rule_id, ", ".join(pre_lexer_rules[lexer_rule_id]))
                )

            slot_config_cursor.execute(
                "CREATE TABLE sentence_rule_table (sentence_rule_id TEXT PRIMARY KEY, sentences TEXT)"
            )
            for sentence_rule_id in pre_sentence_rules:
                slot_config_cursor.execute(
                    "INSERT INTO %S VALUES (%s, %s)" % (sentence_rule_id, ", ".join(pre_sentence_rules[sentence_rule_id]))
                )

            slot_config_db.commit()
            slot_config_cursor.close()
            slot_config_db.close()
    
    
