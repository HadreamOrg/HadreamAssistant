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

        self.name_skills_list = {
            "智能家居": "hass",
            "音乐播放器": "kugou_music",
            "航班查询": "flight_searcher",
            "助理": "tempoary"
        }
        # nlu识别意图和词槽的资料库
        # [[关键词组]], [意图组], [意图对应词槽组], "技能名称"]
        self.keyword_intent_list = [
            (
                [["订", "闹钟"], ["订", "时钟"], ["提醒"]], ["set_alarm"], [[("date", "$date!"), ("time", "$time!")]], "alarm"),
            (
                [["查", "天气"], ["如何", "天气"], ["怎样", "天气"]], ["get_weather"], [[("location", "$city"), ("date", "$date")]], "weather"),
            (
                [["音乐", "放"]], ["play_music"], [[]], "kugou_music"),
            (
                [
                    ["订", "会议"],
                    ["留言"],
                    ["告诉"]
                ],
                [
                    "booking_meeting",
                    "message",
                    "message"
                ],
                [
                    [("date", "$date!"), ("time", "$time!"), ("name", "*meeting_name"), ("attender", "$attender")],
                    [""]
                ],
                "tempoary"
            )
        ]
        self.skill_skills_list = {
            # "hass": HASkillHass,
            "music_player": HASkillMusicPlayer,
            "tempoary": HASkillNotion,
            "alarm": HASkillAlarm
            # "flight_searcher": HASkillFlightSearcher
        }

        self.skills_list = {
            "tempoary": HASkillNotion,
            "alarm": HASkillAlarm,
            "weather": HASkillTuling,
            "talk": HASkillTuling,
            "play_audio": HASkillMusicPlayer,
            "joke": HASkillTuling
        }