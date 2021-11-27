# coding=utf-8
# author: Lan_zhijiang
# description: To saving the keyword skill class
# date: 2020/10/4


class HASkillManager:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        from backend.bot.skill.skills.orgin.alarm import HASkillAlarm
        from backend.bot.skill.skills.orgin.tuling import HASkillTuling
        from backend.bot.skill.skills.orgin.notion import HASkillNotion
        from backend.bot.skill.skills.orgin.music import HASkillMusicPlayer

        # self.keyword_intent_list ={
        #     "闹钟": "clock",
        #     "打开": "call_skill",
        #     "天气": "weather",
        #     "翻译": "translate",
        #     "搜索": "search",
        #     "聊天": "talk",
        #     "闲聊": "talk",
        #     "关机": "shutdown",
        #     "重启": "reboot",
        #     "怎么走": "map",
        #     "订": "book",
        #     "新闻": "news",
        #     "笑话": "joke",
        #     "播放": "play"
        # }
        self.name_skill_list = {
            "智能家居": "hass",
            "音乐播放器": "kugou_music",
            "航班查询": "flight_searcher"
        }
        self.intent_skills_list = {
            "notion": HASkillNotion,
            "alarm": HASkillAlarm,
            "weather": HASkillTuling,
            "talk": HASkillTuling,
            "play_audio": HASkillMusicPlayer,
            "joke": HASkillTuling
        }
        self.skill_skills_list = {
            "hass": HASkillHass,
            "music_player": HASkillMusicPlayer,
            "notion": HASkillNotion,
            "alarm": HASkillAlarm
            # "flight_searcher": HASkillFlightSearcher
        }