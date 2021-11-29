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

        self.name_skill_list = {
            "智能家居": "hass",
            "音乐播放器": "kugou_music",
            "航班查询": "flight_searcher"
        }
        self.keyword_intent_list = [
            (
                [["订", "闹钟"], ["订", "时钟"], ["提醒"]], ["set_alarm"], "alarm"),
            (
                [["查", "天气"], ["如何", "天气"], ["怎样", "天气"]], ["get_weather"], "weather"),
            (
                [["音乐", "放"]], ["play_music"], "kugou_music")
        ]
        self.intent_skills_list = {
            "notion": HASkillNotion,
            "alarm": HASkillAlarm,
            "weather": HASkillTuling,
            "talk": HASkillTuling,
            "play_audio": HASkillMusicPlayer,
            "joke": HASkillTuling
        }
        self.skill_skills_list = {
            # "hass": HASkillHass,
            "music_player": HASkillMusicPlayer,
            "notion": HASkillNotion,
            "alarm": HASkillAlarm
            # "flight_searcher": HASkillFlightSearcher
        }