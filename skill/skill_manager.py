# coding=utf-8
# author: Lan_zhijiang
# description: To saving the keyword skill class
# date: 2020/10/4
# last_edit: 2023/06/30


from skill.skills.orgin.alarm import HASkillAlarm
from skill.skills.orgin.turing import HASkillTuling
from skill.skills.orgin.music import HASkillMusicPlayer



name_skills_list = [
    (["助理", "工作助理", "notion", "办公助手"], "notion"),
    (["音乐播放器", "音乐"], "play_music"),
    (["航班查询", "航班助手"], "flight_searcher")
]
# nlu识别意图和词槽的资料库
# [[关键词组(xx, xx), (xxx)]], [意图组], [意图对应词槽组[(slot_name, slot_data, slot_asking), (slot_name2, ...)]], "技能名称"]
# 目前词槽不支持定义多个询问话术以及询问次数
keyword_intent_list = [
    (
        [[("订", "闹钟"), ("订", "时钟"), ("提醒",)]], ["set_alarm"], [[("date", "$date!"), ("time", "$time!", "请问你想要预定什么时候的闹钟呢？")]], "alarm"),
    (
        [[("查", "天气"), ("如何", "天气"), ("怎样", "天气")]], ["get_weather"], [[("location", "$city!", "请问你想要查询哪个城市的天气"), ("date", "$date", "请问你想要查询哪一天的天气")]], "weather"),
    (
        [[("音乐", "放"), ("听", "音乐"), ("放", "歌")], [("停", "播放"), ("退出", "放")]], ["play_music", "pause"], [[], []], "play_music"),
    (
        [
            [("定", "会议"), ("约", "会议"), ("开", "会"), ("订", "会议"), ("举行", "会")],
            [("取消", "会议")],
            [("改", "会议")],  # 将XXX会议的会议时间更改为XXX
            [("留言",), ("告诉",), ("通知",)],
        ],
        [
            "book_meeting",
            "cancel_meeting",
            "update_meeting",
            "message"
        ],
        [
            [("date_start", "$date!", "请问您想要在哪天的几时举行会议"), ("attender", "$attender", "会议参会人有谁呢？"),
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
skill_skills_list = {
    # "hass": HASkillHass,
    "music_player": HASkillMusicPlayer,
    "alarm": HASkillAlarm
    # "flight_searcher": HASkillFlightSearcher
}

skills_list = {
    "alarm": HASkillAlarm,
    "weather": HASkillTuling,
    "tuling": HASkillTuling,
    "play_music": HASkillMusicPlayer,
    "joke": HASkillTuling
}