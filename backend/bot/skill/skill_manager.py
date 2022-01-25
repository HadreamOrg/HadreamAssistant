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

        self.name_skills_list = [
            (["助理", "工作助理", "notion", "办公助手"], "notion"),
            (["音乐播放器", "音乐"], "play_music"),
            (["航班查询", "航班助手"], "flight_searcher")
        ]
        # nlu识别意图和词槽的资料库
        # [[关键词组]], [意图组], [意图对应词槽组], "技能名称"]
        # 目前词槽不支持定义多个询问话术以及询问次数
        self.keyword_intent_list = [
            (
                [[("订", "闹钟"), ("订", "时钟"), ("提醒")]], ["set_alarm"], [[("date", "$date!"), ("time", "$time!", "请问你想要预定什么时候的闹钟呢？")]], "alarm"),
            (
                [[("查", "天气"), ("如何", "天气"), ("怎样", "天气")]], ["get_weather"], [[("location", "$city!", "请问你想要查询哪个城市的天气"), ("date", "$date", "请问你想要查询哪一天的天气")]], "weather"),
            (
                [[("音乐", "放"), ("听", "音乐"), ("放", "歌")], [("停", "播放"), ("退出", "放")]], ["play_music", "pause"], [[], []], "play_music"),
            (
                [
                    [("定", "会议"), ("约", "会议"), ("开", "会"), ("订", "会议"), ("举行", "会")],
                    [("取消", "会议")],
                    [("改", "会议")], # 将XXX会议的会议时间更改为XXX
                    [("留言"), ("告诉"), ("通知")],
                ],
                [
                    "book_meeting",
                    "cancel_meeting",
                    "update_meeting",
                    "message"
                ],
                [
                    [("date", "$date!", "请问您想要在哪天的几时举行会议"), ("attender", "$attender", "会议参会人有谁呢？"),
                     ("place", "$place", "会议在哪里举行呢")],
                    [("date", "$date", "请问您想要在哪天的几时举行会议"), ("attender", "$attender", "会议参会人有谁呢？"),
                     ("place", "$place", "会议在哪里举行呢")],
                    [],
                    [],
                    []
                ],
                "notion"
            )
        ]
        self.skill_skills_list = {
            # "hass": HASkillHass,
            "music_player": HASkillMusicPlayer,
            "notion": HASkillNotion,
            "alarm": HASkillAlarm
            # "flight_searcher": HASkillFlightSearcher
        }

        self.skills_list = {
            "notion": HASkillNotion,
            "alarm": HASkillAlarm,
            "weather": HASkillTuling,
            "tuling": HASkillTuling,
            "play_music": HASkillMusicPlayer,
            "joke": HASkillTuling
        }